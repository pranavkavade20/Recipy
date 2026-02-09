#Django Built modules
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Temporarily for testing, but should be handled via headers
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST # Ensure UserRecipeActivity model is imported from your models file

# Python modules
import json, os, requests,faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from rapidfuzz import fuzz, process
from fuzzywuzzy import process, fuzz

# Django Files
from .forms import *
from .models import Receipe, Ingredients, Recipe, UserRecipeActivity
from .forms import ReceipeForm, IngredientFormSet
from .serializers import RecipeSerializer, UserRecipeActivitySerializer
from decouple import config


@login_required
def home(request):
    favorite_recipes = UserRecipeActivity.objects.filter(
        user=request.user, action='favorite'
    ).values_list('recipe', flat=True)

    recommended_recipes = []

    if favorite_recipes:
        all_recipes = list(Recipe.objects.all())
        if not all_recipes:
            return render(request, 'base.html', {
                'section': 'home',
                'recommended_recipes': [],
            })

        recipe_ids = [r.id for r in all_recipes]
        recipe_map = {r.id: r for r in all_recipes}

        # Combine text features
        recipe_texts = [f"{r.cuisine} {r.course} {r.diet} {r.ingredients}" for r in all_recipes]

        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(recipe_texts)

        # Dimensionality reduction
        svd = TruncatedSVD(n_components=50, random_state=42)
        reduced_matrix = svd.fit_transform(tfidf_matrix).astype('float32')

        # Build FAISS index
        faiss_index = faiss.IndexFlatL2(50)
        faiss_index.add(reduced_matrix)

        # Get favorite recipe vectors
        favorite_indices = [recipe_ids.index(fid) for fid in favorite_recipes if fid in recipe_ids]
        favorite_vectors = reduced_matrix[favorite_indices]

        # Search for similar recipes
        D, I = faiss_index.search(favorite_vectors, k=10)

        # Flatten indices and remove favorites
        similar_indices = set(i for neighbors in I for i in neighbors if i not in favorite_indices)

        # Map indices back to recipes
        recommended_recipes = [recipe_map[recipe_ids[i]] for i in similar_indices][:5]

    return render(request, 'base.html', {
        'section': 'home',
        'recommended_recipes': recommended_recipes,
    })

#About page
def about(request):
    return render(request,'recipes/about.html', {'section':'dashboard'})

#User profile or dashboard
@login_required 
def dashboard(request):
    return render(request,'registration/dashboard.html', {'section':'dashboard'})

#User registeration page
def register(request):
    if request.method == 'POST':
        user_form =UserRegistrationForm(request.POST) 
        if user_form.is_valid():
            #Create a new user object but avoid saving it yet.   
            new_user= user_form.save(commit=False)
            #set the choosen password
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            #Save the user object
            new_user.save()
            return render(request,'registration/login.html',{'new_user':new_user})
    else:
        user_form=UserRegistrationForm()
    return render(request,'registration/register.html',{'user_form' : user_form})

#Add recipe page
@login_required
def add_recipe(request):
    if request.method == 'POST':
        receipe_form = ReceipeForm(request.POST, request.FILES)

        if receipe_form.is_valid():
            # Save the recipe instance
            receipe = receipe_form.save(commit=False)
            receipe.user = request.user
            receipe.save()

            # Add ingredients one by one
            ingredients = [value for key, value in request.POST.items() if key.startswith('ingredients_name_')]
            for ingredient_name in ingredients:
                if ingredient_name.strip():  # Skip empty fields
                    Ingredients.objects.create(receipe=receipe, ingredients_name=ingredient_name.strip())

            return redirect('my_recipes')  # Redirect to the user's recipes
        else:
            print(receipe_form.errors)

    else:
        receipe_form = ReceipeForm()

    context = {'receipe_form': receipe_form}
    return render(request, 'recipes/add_receipe.html', context)

#User Add recipes 
@login_required
def my_recipes(request):
    # Fetch recipes with their related ingredients
    recipes = Receipe.objects.filter(user=request.user).prefetch_related('ingredients')
    return render(request, 'recipes/my_recipes.html', {'recipes': recipes})
    
#Update recipe page
@login_required
def update_recipe(request, recipe_id):
    recipe = get_object_or_404(Receipe, id=recipe_id, user=request.user)  # Ensure the user owns the recipe
    ingredient_formset = IngredientFormSet(instance=recipe)

    if request.method == 'POST':
        recipe_form = ReceipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe)

        if recipe_form.is_valid() and ingredient_formset.is_valid():
            recipe_form.save()
            ingredient_formset.save()
            return redirect('my_recipes')  # Redirect to the user's recipe list
        else:
            print("Errors:", recipe_form.errors, ingredient_formset.errors)

    else:
        recipe_form = ReceipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)

    context = {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'recipe': recipe,
    }
    return render(request, 'recipes/update_recipe.html', context)

#Add meal plan page.
@login_required
def add_meal_plan(request):
    if request.method == 'POST':
        form = MealPlannerForm(request.POST)
        if form.is_valid():
            meal_plan = form.save(commit=False)
            meal_plan.user = request.user
            meal_plan.save()
            return redirect('view_meal_plans')  # Redirect to the meal plans view
    else:
        form = MealPlannerForm()
    return render(request, 'recipes/add_meal_plan.html', {'form': form})

#User check meals(view meal plan page)
@login_required
def view_meal_plans(request):
    meal_plans = MealPlanner.objects.filter(user=request.user)
    return render(request, 'recipes/view_meal_plans.html', {'meal_plans': meal_plans})

#Delete recipes 
@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Receipe, id=recipe_id, user=request.user)

    if request.method == 'POST':
        recipe.delete()
        return redirect('my_recipes')  # Redirect to the recipe list after deletion

    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})

# Render recipe detail page
def recipe_detail(request, id):
    context = {'id': id}
    return render(request, 'recipes/recipe_detail.html', context)

# Log user activity for recipes
class LogUserActivity(APIView):
    def get(self, request):
        if request.GET.get('recipe_id') is None:
            return Response({"message": "id required!"}, status=201)

        data = {
            "user": request.user.id,
            "recipe": request.GET.get('recipe_id'),
            "action": "view"
        }
        serializer = UserRecipeActivitySerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Automatically set the logged-in user
            activities = UserRecipeActivity.objects.filter(user=request.user)
            if activities.count() > 5:
                activities.last().delete()
            return Response({"message": "User activity logged successfully!"}, status=201)
        return Response(serializer.errors, status=200)

# Get similar recipes based on user activity
def get_similar_recipes_by_user_activity(user_id, top_n=9):
    try:
        user_activities = UserRecipeActivity.objects.filter(user_id=user_id)
        if not user_activities.exists():
            return []

        recipe_ids = user_activities.values_list('recipe', flat=True).distinct()
        user_recipes = Recipe.objects.filter(id__in=recipe_ids)
        descriptions = [recipe.description for recipe in user_recipes]
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(descriptions)

        all_recipes = list(Recipe.objects.all())
        all_descriptions = [recipe.description for recipe in all_recipes]
        all_tfidf_matrix = tfidf_vectorizer.transform(all_descriptions)

        similar_recipes = set()
        for i, user_recipe in enumerate(user_recipes):
            cosine_sim = cosine_similarity(tfidf_matrix[i], all_tfidf_matrix).flatten()
            similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
            for idx in similar_indices:
                similar_recipe = all_recipes[idx]
                if similar_recipe != user_recipe and similar_recipe.id not in recipe_ids:
                    similar_recipes.add(similar_recipe)

        return list(similar_recipes)
    except Exception as e:
        print(f"Error: {e}")
        return []

# API to list recipes and similar recipes based on user activity
class RecipeAPI(APIView):
    def get(self, request):
        user_id = request.user.id
        all_recipes = RecipeSerializer(Recipe.objects.all().order_by('?')[:9], many=True)
        recipes = get_similar_recipes_by_user_activity(user_id)
        serializer = RecipeSerializer(recipes, many=True)
        return Response({"all_recipes": all_recipes.data, "similar_recipes": serializer.data})

# Get similar recipes for a specific recipe
def get_similar_recipes(recipe_id, top_n=9):
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        recipe_descriptions = Recipe.objects.all().values_list('description', flat=True)
        tfidf_matrix = vectorizer.fit_transform(recipe_descriptions)

        target_recipe = Recipe.objects.get(id=recipe_id)
        all_recipes = list(Recipe.objects.all())
        target_index = all_recipes.index(target_recipe)

        cosine_sim = cosine_similarity(tfidf_matrix[target_index], tfidf_matrix).flatten()
        similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
        similar_indices = [i for i in similar_indices if i != target_index]

        return [all_recipes[idx] for idx in similar_indices]
    except Exception as e:
        print(f"Error: {e}")
        return []

# API to fetch recipe details and similar recipes
class RecipeDetailAPI(APIView):
    def get(self, request, id):
        recipe = Recipe.objects.get(id=id)
        serializer = RecipeSerializer(recipe)
        similar_recipes = get_similar_recipes(id)
        similar_recipe_serializer = RecipeSerializer(similar_recipes, many=True)
        return Response({"recipe": serializer.data, "similar_recipes": similar_recipe_serializer.data})

#Serach recipes for user
@login_required
def search_user_recipes(request):
    query = request.GET.get("q", "")  # Get the search query from the URL
    recipes = None  # Set to None by default

    if request.user.is_authenticated and query:
        recipes = Receipe.objects.filter(
            Q(user=request.user) & 
            (Q(receipe_name__icontains=query) | 
             Q(ingredients__ingredients_name__icontains=query))
        ).distinct()

    return render(request, "recipes/search_results.html", {"recipes": recipes, "query": query})

# Backend: Adding search functionality

def search_page(request):
    diet_type = request.GET.get('diet', '')
    
    # Filter recipes by diet type if selected, otherwise get all
    if diet_type:
        recipes = Recipe.objects.filter(diet__iexact=diet_type)[:9]
    else:
        recipes = Recipe.objects.all()[:9]
    return render(request, 'recipes/search.html',{'recipes': recipes, 'diet_type': diet_type})

def search_recipes(request):
    """
    AI-powered search with auto-suggestions.
    Returns recipes with full image URLs for frontend display.
    """
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    # Fetch all recipes
    all_recipes = list(
        Recipe.objects.all().values(
            'id', 'name', 'image_url', 'description',
            'ingredients', 'cuisine', 'course', 'diet'
        )
    )

    if not all_recipes:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    # Prepare text data for TF-IDF
    recipe_texts = [
        f"{recipe['name']} {recipe.get('ingredients', '')} "
        f"{recipe.get('cuisine', '')} {recipe.get('course', '')} "
        f"{recipe.get('diet', '')}".lower()
        for recipe in all_recipes
    ]

    recipe_names = [recipe['name'].lower() for recipe in all_recipes]
    recipe_texts.append(query)

    # TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(recipe_texts)
    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Fuzzy matching
    fuzzy_matches = process.extract(query, recipe_names, scorer=fuzz.partial_ratio, limit=5)
    for match, score in fuzzy_matches:
        if score > 70:
            try:
                index = recipe_names.index(match)
                similarity_scores[index] += score / 100
            except ValueError:
                pass

    # Get top 5 results
    top_indices = np.argsort(similarity_scores)[::-1][:5]

    matched_recipes = []
    for i in top_indices:
        if similarity_scores[i] > 0.3:
            recipe = all_recipes[i]

            # Build full image URL from media/recipe/
            image_name = recipe['image_url'] or ""
            image_url = ""
            if image_name:
                image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{image_name}")


            matched_recipes.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'image_url': image_url,  # ✅ full URL
                'description': recipe.get('description', ''),
                'ingredients': recipe.get('ingredients', ''),
                'cuisine': recipe.get('cuisine', 'Unknown'),
                'course': recipe.get('course', 'Unknown'),
                'diet': recipe.get('diet', 'Unknown'),
            })

    suggestions = [
        all_recipes[i]['name'] for i in top_indices if similarity_scores[i] > 0.2
    ]

    return JsonResponse({'recipes': matched_recipes, 'suggestions': suggestions}, status=200)

# Favorite recipes functionality
@csrf_exempt
@login_required
def save_favorite_recipe(request):
    if request.method == "POST":
        data = json.loads(request.body)
        recipe_id = data.get("recipe_id")
        user = request.user

        try:
            recipe = Recipe.objects.get(id=recipe_id)
            # Check if the recipe is already favorited
            favorite, created = UserRecipeActivity.objects.get_or_create(
                user=user, recipe=recipe, action="favorite"
            )
            if not created:
                return JsonResponse({"message": "Recipe already favorited"}, status=400)

            return JsonResponse({"message": "Recipe saved as favorite!"}, status=201)

        except Recipe.DoesNotExist:
            return JsonResponse({"error": "Recipe not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def get_saved_recipes(request):
    user = request.user
    saved_recipes = UserRecipeActivity.objects.filter(user=user, action="favorite").select_related("recipe")

    context = {
        "saved_recipes": [
            {
                "id": activity.recipe.id,
                "name": activity.recipe.name,
                "image_url": activity.recipe.image_url,
                "cuisine": activity.recipe.cuisine,
                "course": activity.recipe.course,
                "diet": activity.recipe.diet,
            }
            for activity in saved_recipes
        ],
        "count": saved_recipes.count(),  # ✅ Pass updated count
    }

    return render(request, "recipes/saved_recipes.html", context)

@login_required
@require_POST
def remove_saved_recipe(request):
    """
    Removes a recipe from the user's favorites list.
    Expects JSON body: {"recipe_id": <id>}
    """
    # 1. FIX: Read JSON data from the request body
    try:
        data = json.loads(request.body)
        recipe_id = data.get("recipe_id")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    
    user = request.user
    
    if not recipe_id:
        return JsonResponse({"error": "Recipe ID missing"}, status=400)

    try:
        # Assumes UserRecipeActivity model exists
        activity = UserRecipeActivity.objects.get(user=user, recipe_id=recipe_id, action="favorite")
        activity.delete()
    except UserRecipeActivity.DoesNotExist:
        # This is the "Recipe not found in favorites" error you saw,
        # which can happen if the client sends a bad ID. We return success if deletion is the goal.
        return JsonResponse({"success": False, "error": "Recipe was not found in your favorites list."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Database error during removal: {str(e)}"}, status=500)

    # Recalculate new count for frontend badge update
    new_count = UserRecipeActivity.objects.filter(user=user, action="favorite").count()
    
    # 2. FIX: Return JsonResponse for AJAX success
    return JsonResponse({"success": True, "count": new_count, "message": "Recipe removed successfully!"})

# views.py
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decouple import config
from .models import Recipe

def get_recipe_videos(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # Adding 'shorts' helps find vertical content, but normal videos work too
    search_query = f"{recipe.name} recipe shorts"

    youtube_url = "https://www.googleapis.com/youtube/v3/search"
    api_key = config('YOUTUBE_API_KEY', default=None)

    if not api_key:
        return JsonResponse({"error": "API Key not found"}, status=500)

    params = {
        "part": "snippet",
        "q": search_query,
        "key": api_key,
        "maxResults": 2,
        "type": "video"
    }

    try:
        response = requests.get(youtube_url, params=params)
        
        if response.status_code != 200:
            return JsonResponse({"error": "YouTube API error"}, status=response.status_code)

        data = response.json()
        video_data = []
        
        for item in data.get("items", []):
            # Try to get the highest resolution thumbnail available
            thumbnails = item["snippet"]["thumbnails"]
            thumbnail_url = thumbnails.get("high", thumbnails.get("medium", {})).get("url")
            
            video_data.append({
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "thumbnail": thumbnail_url
            })

        return JsonResponse({"videos": video_data})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)




