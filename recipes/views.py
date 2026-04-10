import json, requests, faiss
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from rapidfuzz import process, fuzz
from decouple import config

from .models import Recipe, Ingredient, MealPlanner, UserRecipeActivity, RecipeVideo
from .forms import RecipeForm, IngredientFormSet, RecipeVideoFormSet, MealPlannerForm
from .serializers import RecipeSerializer, UserRecipeActivitySerializer

def home(request):
    favorite_recipes = []
    if request.user.is_authenticated:
        favorite_recipes = UserRecipeActivity.objects.filter(
            user=request.user, action='favorite'
        ).values_list('recipe', flat=True)

    recommended_recipes = []
    if favorite_recipes:
        all_recipes = list(Recipe.objects.all())
        if all_recipes:
            recipe_ids = [r.id for r in all_recipes]
            recipe_map = {r.id: r for r in all_recipes}
            recipe_texts = [f"{r.cuisine or ''} {r.course or ''} {r.diet or ''} {r.description or ''}" for r in all_recipes]

            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(recipe_texts)
            
            n_components = min(50, tfidf_matrix.shape[1] - 1)
            if n_components > 0:
                svd = TruncatedSVD(n_components=n_components, random_state=42)
                reduced_matrix = svd.fit_transform(tfidf_matrix).astype('float32')

                faiss_index = faiss.IndexFlatL2(n_components)
                faiss_index.add(reduced_matrix)

                favorite_indices = [recipe_ids.index(fid) for fid in favorite_recipes if fid in recipe_ids]
                if favorite_indices:
                    favorite_vectors = reduced_matrix[favorite_indices]
                    D, I = faiss_index.search(favorite_vectors, k=min(10, len(all_recipes)))
                    similar_indices = set(i for neighbors in I for i in neighbors if i not in favorite_indices)
                    recommended_recipes = [recipe_map[recipe_ids[i]] for i in similar_indices][:5]

    return render(request, 'home.html', {'section': 'home', 'recommended_recipes': recommended_recipes})

def about(request):
    return render(request, 'recipes/about.html', {'section': 'about'})

@login_required
def add_recipe(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        if recipe_form.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            video_formset = RecipeVideoFormSet(request.POST, request.FILES, instance=recipe)
            
            if ingredient_formset.is_valid() and video_formset.is_valid():
                ingredient_formset.save()
                video_formset.save()
                return redirect('recipes:my_recipes')
    else:
        recipe_form = RecipeForm()
        ingredient_formset = IngredientFormSet()
        video_formset = RecipeVideoFormSet()

    context = {'recipe_form': recipe_form, 'ingredient_formset': ingredient_formset, 'video_formset': video_formset}
    return render(request, 'recipes/add_recipe.html', context)

@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user).prefetch_related('ingredients', 'videos')
    return render(request, 'recipes/my_recipes.html', {'recipes': recipes})

@login_required
def update_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
        video_formset = RecipeVideoFormSet(request.POST, request.FILES, instance=recipe)

        if recipe_form.is_valid() and ingredient_formset.is_valid() and video_formset.is_valid():
            recipe_form.save()
            ingredient_formset.save()
            video_formset.save()
            return redirect('recipes:my_recipes')
    else:
        recipe_form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)
        video_formset = RecipeVideoFormSet(instance=recipe)

    context = {'recipe_form': recipe_form, 'ingredient_formset': ingredient_formset, 'video_formset': video_formset, 'recipe': recipe}
    return render(request, 'recipes/update_recipe.html', context)

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipes:my_recipes')
    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})

@login_required
def add_meal_plan(request):
    if request.method == 'POST':
        form = MealPlannerForm(request.POST)
        if form.is_valid():
            meal_plan = form.save(commit=False)
            meal_plan.user = request.user
            meal_plan.save()
            return redirect('recipes:view_meal_plans')
    else:
        form = MealPlannerForm()
        form.fields['recipe'].queryset = Recipe.objects.all() # Or limit to user's favorites/own recipes
    return render(request, 'recipes/add_meal_plan.html', {'form': form})

@login_required
def view_meal_plans(request):
    meal_plans = MealPlanner.objects.filter(user=request.user)
    return render(request, 'recipes/view_meal_plans.html', {'meal_plans': meal_plans})

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

class LogUserActivity(APIView):
    def get(self, request):
        if not request.GET.get('recipe_id'):
            return Response({"message": "id required!"}, status=400)
        data = {"user": request.user.id, "recipe": request.GET.get('recipe_id'), "action": "view"}
        serializer = UserRecipeActivitySerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            activities = UserRecipeActivity.objects.filter(user=request.user, action='view')
            if activities.count() > 5:
                activities.order_by('timestamp').first().delete()
            return Response({"message": "User activity logged successfully!"}, status=201)
        return Response(serializer.errors, status=400)

class RecipeAPI(APIView):
    def get(self, request):
        all_recipes = RecipeSerializer(Recipe.objects.all().order_by('?')[:9], many=True)
        return Response({"all_recipes": all_recipes.data})

class RecipeDetailAPI(APIView):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe)
        return Response({"recipe": serializer.data})

@login_required
def search_user_recipes(request):
    query = request.GET.get("q", "")
    recipes = None
    if query:
        recipes = Recipe.objects.filter(
            Q(author=request.user) & 
            (Q(name__icontains=query) | Q(ingredients__name__icontains=query))
        ).distinct()
    return render(request, "recipes/search_results.html", {"recipes": recipes, "query": query})

def search_page(request):
    diet_type = request.GET.get('diet', '')
    recipes = Recipe.objects.filter(diet__iexact=diet_type)[:9] if diet_type else Recipe.objects.all()[:9]
    return render(request, 'recipes/search.html', {'recipes': recipes, 'diet_type': diet_type})

def search_recipes(request):
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    all_recipes = list(Recipe.objects.all().values('id', 'name', 'image', 'description', 'cuisine', 'course', 'diet'))
    if not all_recipes:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    recipe_texts = [f"{r['name']} {r.get('cuisine', '')} {r.get('course', '')} {r.get('diet', '')}".lower() for r in all_recipes]
    recipe_names = [r['name'].lower() for r in all_recipes]
    recipe_texts.append(query)

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(recipe_texts)
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    fuzzy_matches = process.extract(query, recipe_names, scorer=fuzz.partial_ratio, limit=5)
    for match, score, index in fuzzy_matches:
        if score > 70:
            similarity_scores[index] += score / 100

    top_indices = np.argsort(similarity_scores)[::-1][:5]
    matched_recipes = []
    
    for i in top_indices:
        if similarity_scores[i] > 0.3:
            r = all_recipes[i]
            image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{r['image']}") if r['image'] else ""
            matched_recipes.append({
                'id': r['id'], 'name': r['name'], 'image_url': image_url,
                'description': r.get('description', ''), 'cuisine': r.get('cuisine', 'Unknown')
            })

    suggestions = [all_recipes[i]['name'] for i in top_indices if similarity_scores[i] > 0.2]
    return JsonResponse({'recipes': matched_recipes, 'suggestions': suggestions}, status=200)

@csrf_exempt
@login_required
def save_favorite_recipe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            recipe = Recipe.objects.get(id=data.get("recipe_id"))
            favorite, created = UserRecipeActivity.objects.get_or_create(user=request.user, recipe=recipe, action="favorite")
            if not created:
                return JsonResponse({"message": "Recipe already favorited"}, status=400)
            return JsonResponse({"message": "Recipe saved as favorite!"}, status=201)
        except Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def get_saved_recipes(request):
    saved = UserRecipeActivity.objects.filter(user=request.user, action="favorite").select_related("recipe")
    context = {"saved_recipes": [s.recipe for s in saved], "count": saved.count()}
    return render(request, "recipes/saved_recipes.html", context)

@login_required
@require_POST
def remove_saved_recipe(request):
    try:
        recipe_id = json.loads(request.body).get("recipe_id")
        UserRecipeActivity.objects.get(user=request.user, recipe_id=recipe_id, action="favorite").delete()
        new_count = UserRecipeActivity.objects.filter(user=request.user, action="favorite").count()
        return JsonResponse({"success": True, "count": new_count, "message": "Recipe removed successfully!"})
    except UserRecipeActivity.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not in favorites."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def get_recipe_videos(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    video_data = []

    # Include locally uploaded/linked videos from the new RecipeVideo model
    for v in recipe.videos.all():
        video_data.append({
            "title": v.title or f"{recipe.name} Video",
            "video_url": v.hls_stream_url or v.external_url or (v.raw_video_file.url if v.raw_video_file else ""),
            "thumbnail": v.thumbnail.url if v.thumbnail else ""
        })

    # Fallback to YouTube API if no local videos exist
    if not video_data:
        api_key = config('YOUTUBE_API_KEY', default=None)
        if api_key:
            try:
                res = requests.get("https://www.googleapis.com/youtube/v3/search", params={
                    "part": "snippet", "q": f"{recipe.name} recipe", "key": api_key, "maxResults": 1, "type": "video"
                })
                if res.status_code == 200:
                    for item in res.json().get("items", []):
                        video_data.append({
                            "title": item["snippet"]["title"],
                            "video_id": item["id"]["videoId"],
                            "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url")
                        })
            except Exception as e:
                pass 

    return JsonResponse({"videos": video_data})