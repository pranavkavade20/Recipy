import json
import re
import numpy as np
import faiss
import requests

from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from rapidfuzz import process, fuzz
from decouple import config

from .models import Recipe, Ingredient, MealPlanner, UserRecipeActivity, RecipeVideo
from .forms import RecipeForm, IngredientFormSet, RecipeVideoFormSet, MealPlannerForm
from .serializers import RecipeSerializer, UserRecipeActivitySerializer

@login_required
def dashboard(request):
    return render(request, 'recipes/dashboard.html', {'section': 'dashboard'})

# ---------------------------------------------------------------------------
# Helper: build and cache the recommendation FAISS index
# ---------------------------------------------------------------------------
def _get_recommendation_index():
    """
    Returns (faiss_index, reduced_matrix, recipe_ids, recipe_map) from cache.
    Rebuilds the index if the cache is cold or the recipe count has changed.
    Cache timeout is controlled by settings.RECOMMENDATION_CACHE_TIMEOUT.
    """
    recipe_count = Recipe.objects.count()
    cache_key = f'rec_index_{recipe_count}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    all_recipes = list(Recipe.objects.all())
    if not all_recipes:
        return None

    recipe_ids = [r.id for r in all_recipes]
    recipe_map = {r.id: r for r in all_recipes}
    recipe_texts = [
        f"{r.cuisine or ''} {r.course or ''} {r.diet or ''} {r.description or ''}"
        for r in all_recipes
    ]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(recipe_texts)

    n_samples, n_features = tfidf_matrix.shape

    # n_components must be strictly less than BOTH n_samples AND n_features.
    # Without the n_samples guard, SVD on small databases (e.g. fewer recipes
    # than 50) produces a rank-deficient matrix, which causes:
    #   - RuntimeWarning: invalid value encountered in divide (sklearn)
    #   - AssertionError: assert d == self.d (faiss)
    n_components = min(50, n_features - 1, n_samples - 1)
    if n_components <= 0:
        return None

    svd = TruncatedSVD(n_components=n_components, random_state=42)
    reduced_matrix = svd.fit_transform(tfidf_matrix).astype('float32')

    # Sanitize NaN/Inf that appear when SVD hits near-zero variance
    # (very few recipes or near-identical text descriptions).
    reduced_matrix = np.nan_to_num(reduced_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    # Use the ACTUAL output dimension rather than requested n_components.
    # SVD can silently produce fewer columns on rank-deficient matrices;
    # using reduced_matrix.shape[1] prevents the FAISS dimension assert.
    actual_dim = reduced_matrix.shape[1]
    if actual_dim <= 0:
        return None

    faiss_index = faiss.IndexFlatL2(actual_dim)
    faiss_index.add(reduced_matrix)

    result = (faiss_index, reduced_matrix, recipe_ids, recipe_map)
    timeout = getattr(settings, 'RECOMMENDATION_CACHE_TIMEOUT', 900)
    cache.set(cache_key, result, timeout)
    return result


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def home(request):
    recommended_recipes = []
    favorite_ids = []

    if request.user.is_authenticated:
        favorite_ids = list(
            UserRecipeActivity.objects.filter(
                user=request.user, action='favorite'
            ).values_list('recipe', flat=True)
        )

    if favorite_ids:
        index_data = _get_recommendation_index()
        if index_data:
            faiss_index, reduced_matrix, recipe_ids, recipe_map = index_data
            favorite_indices = [
                recipe_ids.index(fid) for fid in favorite_ids if fid in recipe_ids
            ]
            if favorite_indices:
                favorite_vectors = reduced_matrix[favorite_indices]
                _, I = faiss_index.search(favorite_vectors, k=min(10, len(recipe_ids)))
                similar_indices = set(
                    i for neighbors in I for i in neighbors
                    if i not in favorite_indices
                )
                recommended_recipes = [
                    recipe_map[recipe_ids[i]] for i in similar_indices
                ][:5]

    return render(request, 'home.html', {
        'section': 'home',
        'recommended_recipes': recommended_recipes,
    })


def about(request):
    return render(request, 'recipes/about.html', {'section': 'about'})


@login_required
def add_recipe(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = IngredientFormSet(request.POST)
        video_formset = RecipeVideoFormSet(request.POST, request.FILES)

        # Validate ALL forms before saving anything
        if recipe_form.is_valid() and ingredient_formset.is_valid() and video_formset.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user
            recipe.save()  # Save recipe first so formsets can link to it

            # Re-bind formsets with the saved recipe instance
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            video_formset = RecipeVideoFormSet(request.POST, request.FILES, instance=recipe)

            # Re-validate with instance (they were already valid, but instance is needed to save)
            if ingredient_formset.is_valid():
                ingredient_formset.save()
            if video_formset.is_valid():
                video_formset.save()

            return redirect('recipes:my_recipes')
    else:
        recipe_form = RecipeForm()
        ingredient_formset = IngredientFormSet()
        video_formset = RecipeVideoFormSet()

    context = {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'video_formset': video_formset,
    }
    return render(request, 'recipes/add_recipe.html', context)


@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(
        author=request.user
    ).prefetch_related('ingredients', 'videos')
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

    context = {
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'video_formset': video_formset,
        'recipe': recipe,
    }
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
        form.fields['recipe'].queryset = Recipe.objects.all()
    return render(request, 'recipes/add_meal_plan.html', {'form': form})


@login_required
def view_meal_plans(request):
    meal_plans = MealPlanner.objects.filter(user=request.user).select_related('recipe')
    return render(request, 'recipes/view_meal_plans.html', {'meal_plans': meal_plans})


def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})


# ---------------------------------------------------------------------------
# API Views
# ---------------------------------------------------------------------------

class LogUserActivity(APIView):
    def get(self, request):
        recipe_id = request.GET.get('recipe_id')
        if not recipe_id:
            return Response({"message": "id required!"}, status=400)

        data = {"recipe": recipe_id, "action": "view"}
        serializer = UserRecipeActivitySerializer(data=data)
        if serializer.is_valid():
            # Inject user server-side — not from client data
            serializer.save(user=request.user)

            # Keep at most 5 'view' records per user — single query
            activities = UserRecipeActivity.objects.filter(
                user=request.user, action='view'
            ).order_by('timestamp')
            count = activities.count()
            if count > 5:
                # Delete oldest records beyond the 5 most recent
                ids_to_delete = list(activities.values_list('id', flat=True)[:count - 5])
                UserRecipeActivity.objects.filter(id__in=ids_to_delete).delete()

            return Response({"message": "User activity logged successfully!"}, status=201)
        return Response(serializer.errors, status=400)


class RecipeAPI(APIView):
    def get(self, request):
        # Pass request in context so ImageField returns full absolute URLs
        all_recipes = RecipeSerializer(
            Recipe.objects.all().order_by('?')[:9],
            many=True,
            context={'request': request},
        )
        return Response({"all_recipes": all_recipes.data})


class RecipeDetailAPI(APIView):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe, context={'request': request})

        # Return up to 4 similar recipes (same cuisine or course, excluding self)
        similar_qs = Recipe.objects.filter(
            Q(cuisine=recipe.cuisine) | Q(course=recipe.course)
        ).exclude(id=recipe.id).order_by('?')[:4]
        similar_serializer = RecipeSerializer(
            similar_qs, many=True, context={'request': request}
        )

        return Response({
            "recipe": serializer.data,
            "similar_recipes": similar_serializer.data,
        })


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@login_required
def search_user_recipes(request):
    """
    Search user's own recipes by name, description, and ingredients.
    Supports partial matches and is case-insensitive.
    """
    query = request.GET.get("q", "").strip()
    recipes = None
    
    if query:
        # Build comprehensive filter combining name, description, and ingredients
        recipes = Recipe.objects.filter(
            author=request.user
        ).filter(
            # Search in name (case-insensitive)
            Q(name__icontains=query) |
            # Search in description
            Q(description__icontains=query) |
            # Search in ingredient names
            Q(ingredients__name__icontains=query) |
            # Search in cuisine type
            Q(cuisine__icontains=query) |
            # Search in course type
            Q(course__icontains=query)
        ).distinct().prefetch_related('ingredients', 'videos')
    
    return render(request, "recipes/search_results.html", {"recipes": recipes, "query": query})


def search_page(request):
    """
    Explore/search page with advanced filtering by diet, cuisine, course, and recipe type.
    Optimized query with select_related and prefetch_related for performance.
    """
    diet_type = request.GET.get('diet', '').strip()
    cuisine_type = request.GET.get('cuisine', '').strip()
    course_type = request.GET.get('course', '').strip()
    recipe_type = request.GET.get('type', '').strip()
    
    # Start with all recipes and apply filters
    recipes_qs = Recipe.objects.all().prefetch_related('ingredients', 'videos')
    
    if diet_type:
        recipes_qs = recipes_qs.filter(diet__iexact=diet_type)
    
    if cuisine_type:
        recipes_qs = recipes_qs.filter(cuisine__iexact=cuisine_type)
    
    if course_type:
        recipes_qs = recipes_qs.filter(course__iexact=course_type)
    
    if recipe_type:
        recipes_qs = recipes_qs.filter(recipe_type__iexact=recipe_type)
    
    # Randomize display and limit to 12 for better UX
    recipes = recipes_qs.order_by('?')[:12]
    
    # Get unique filter options for dropdown population
    unique_diets = Recipe.objects.filter(diet__isnull=False).values_list('diet', flat=True).distinct()
    unique_cuisines = Recipe.objects.filter(cuisine__isnull=False).values_list('cuisine', flat=True).distinct()
    unique_courses = Recipe.objects.filter(course__isnull=False).values_list('course', flat=True).distinct()
    
    context = {
        'recipes': recipes,
        'diet_type': diet_type,
        'cuisine_type': cuisine_type,
        'course_type': course_type,
        'recipe_type': recipe_type ,
        'available_diets': unique_diets,
        'available_cuisines': unique_cuisines,
        'available_courses': unique_courses,
    }
    
    return render(request, 'recipes/search.html', context)


def _build_optimized_search_index():
    """
    Build and cache an optimized search index with TF-IDF + ingredient data.
    Returns (vectorizer, tfidf_matrix, all_recipes, ingredient_map, combined_texts)
    """
    recipe_count = Recipe.objects.count()
    cache_key = f'search_index_v2_{recipe_count}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    all_recipes = list(
        Recipe.objects.all().prefetch_related('ingredients').values(
            'id', 'name', 'image', 'description', 'cuisine', 'course', 'diet'
        )
    )
    if not all_recipes:
        return None

    # Build ingredient map for each recipe
    ingredient_map = {}
    for recipe in Recipe.objects.all().prefetch_related('ingredients'):
        ingredient_map[recipe.id] = [ing.name.lower() for ing in recipe.ingredients.all()]

    # Combined text includes recipe metadata + ingredients
    combined_texts = []
    for r in all_recipes:
        ingredients_text = ' '.join(ingredient_map.get(r['id'], []))
        combined_text = (
            f"{r['name']} {r.get('description', '')} "
            f"{r.get('cuisine', '')} {r.get('course', '')} {r.get('diet', '')} "
            f"{ingredients_text}"
        ).lower()
        combined_texts.append(combined_text)

    # Create TF-IDF vectorizer with optimized parameters
    vectorizer = TfidfVectorizer(
        stop_words='english',
        min_df=1,
        max_df=0.9,
        ngram_range=(1, 2),  # Unigrams + bigrams for better matching
        sublinear_tf=True,
        max_features=5000
    )
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    result = (vectorizer, tfidf_matrix, all_recipes, ingredient_map, combined_texts)
    timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 600)
    cache.set(cache_key, result, timeout)
    return result


def search_recipes(request):
    """
    Optimized hybrid search combining:
    - TF-IDF semantic similarity
    - Fuzzy matching on recipe names
    - Ingredient-based search
    - Weighted ranking system
    """
    query = request.GET.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    # Check cache for exact query
    recipe_count = Recipe.objects.count()
    search_cache_key = f'search_results_v2_{query}_{recipe_count}'
    cached_results = cache.get(search_cache_key)
    if cached_results:
        return JsonResponse(cached_results, status=200)

    # Build or retrieve optimized search index
    index_data = _build_optimized_search_index()
    if not index_data:
        return JsonResponse({'recipes': [], 'suggestions': []}, status=200)

    vectorizer, tfidf_matrix, all_recipes, ingredient_map, combined_texts = index_data

    # ===== SEMANTIC SIMILARITY (TF-IDF) =====
    try:
        query_vec = vectorizer.transform([query])
        semantic_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    except Exception:
        semantic_scores = np.zeros(len(all_recipes))

    # ===== FUZZY NAME MATCHING =====
    recipe_names = [r['name'].lower() for r in all_recipes]
    fuzzy_name_scores = np.zeros(len(all_recipes))

    # Extract best fuzzy matches for names
    if recipe_names:
        fuzzy_matches = process.extract(
            query, recipe_names, scorer=fuzz.token_set_ratio, limit=20
        )
        for _match, score, index in fuzzy_matches:
            if score > 50:  # Lower threshold for more matches
                fuzzy_name_scores[index] = score / 100.0

    # ===== INGREDIENT-BASED SEARCH =====
    ingredient_scores = np.zeros(len(all_recipes))
    query_terms = set(query.split())

    for idx, (recipe, ingredients) in enumerate(zip(all_recipes, [ingredient_map.get(r['id'], []) for r in all_recipes])):
        if ingredients:
            # Fuzzy match ingredients
            matching_ingredients = []
            for ingredient in ingredients:
                for term in query_terms:
                    # Use token_set_ratio for ingredient matching
                    if fuzz.token_set_ratio(term, ingredient) > 60:
                        matching_ingredients.append(ingredient)
                        break

            # Score based on matched ingredients
            if matching_ingredients:
                ingredient_scores[idx] = min(len(matching_ingredients) / len(ingredients), 1.0) * 0.8

    # ===== COMBINED RANKING =====
    # Normalize scores to [0, 1] range
    max_semantic = np.max(semantic_scores) if len(semantic_scores) > 0 else 1
    semantic_scores = semantic_scores / max_semantic if max_semantic > 0 else semantic_scores

    # Weight combination (can be tuned based on preference)
    combined_scores = (
        semantic_scores * 0.50 +      # 50% semantic similarity
        fuzzy_name_scores * 0.35 +    # 35% name matching
        ingredient_scores * 0.15      # 15% ingredient matching
    )

    # ===== RESULT COMPILATION =====
    top_k = 10  # Get top 10 candidates
    top_indices = np.argsort(combined_scores)[::-1][:top_k]

    matched_recipes = []
    min_score_threshold = 0.15  # Adaptive threshold

    for i in top_indices:
        score = combined_scores[i]
        if score >= min_score_threshold:
            r = all_recipes[i]
            # Build proper absolute URL for images, with fallback
            if r['image']:
                image_url = request.build_absolute_uri(f"{settings.MEDIA_URL}{r['image']}")
            else:
                image_url = ""
            
            matched_recipes.append({
                'id': r['id'],
                'name': r['name'],
                'image_url': image_url,
                'description': r.get('description', '')[:150],  # Truncate description
                'cuisine': r.get('cuisine', 'Unknown'),
                'diet': r.get('diet', 'Standard'),  # ← ADDED: Frontend expects this
                'course': r.get('course', 'Main'),  # ← ADDED: Frontend expects this
                'score': float(score)
            })

    # Limit to 6 results for UI
    matched_recipes = matched_recipes[:6]

    # Generate smart suggestions from top matches
    suggestions = []
    for idx in top_indices[:5]:
        if combined_scores[idx] > 0.1:
            suggestions.append(all_recipes[idx]['name'])

    result = {'recipes': matched_recipes, 'suggestions': suggestions}

    timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 600)
    cache.set(search_cache_key, result, timeout)

    return JsonResponse(result, status=200)


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_favorite_recipe(request):
    """
    Save a recipe as a favorite for the current user.
    CSRF protection is intentionally kept active — the frontend must include
    the csrftoken cookie value in the X-CSRFToken request header.
    """
    try:
        data = json.loads(request.body)
        recipe = Recipe.objects.get(id=data.get("recipe_id"))
        favorite, created = UserRecipeActivity.objects.get_or_create(
            user=request.user, recipe=recipe, action="favorite"
        )
        if not created:
            return JsonResponse({"message": "Recipe already favorited"}, status=400)
        return JsonResponse({"message": "Recipe saved as favorite!"}, status=201)
    except Recipe.DoesNotExist:
        return JsonResponse({"error": "Recipe not found"}, status=404)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_saved_recipes(request):
    saved = UserRecipeActivity.objects.filter(
        user=request.user, action="favorite"
    ).select_related("recipe")
    context = {
        "saved_recipes": [s.recipe for s in saved],
        "count": saved.count(),
    }
    return render(request, "recipes/saved_recipes.html", context)


@login_required
@require_POST
def remove_saved_recipe(request):
    try:
        recipe_id = json.loads(request.body).get("recipe_id")
        UserRecipeActivity.objects.get(
            user=request.user, recipe_id=recipe_id, action="favorite"
        ).delete()
        new_count = UserRecipeActivity.objects.filter(
            user=request.user, action="favorite"
        ).count()
        return JsonResponse({"success": True, "count": new_count, "message": "Recipe removed successfully!"})
    except UserRecipeActivity.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not in favorites."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ---------------------------------------------------------------------------
# Helpers for video URL parsing
# ---------------------------------------------------------------------------

# Matches any YouTube video ID (11-char alphanumeric/dash/underscore)
_YT_ID_RE = re.compile(
    r'(?:v=|youtu\.be/|/shorts/|/embed/|/v/)([a-zA-Z0-9_-]{11})'
)


def _extract_youtube_id(url: str):
    """Return the 11-char YouTube video ID from any YouTube URL, or None."""
    if not url:
        return None
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else None


def _is_short_url(url: str) -> bool:
    return bool(url and '/shorts/' in url)


def get_recipe_videos(request, recipe_id):
    """
    Returns a normalised list of video objects, each with:
      - title       : display name
      - embed_url   : ready-to-use URL for <iframe> or <video src>
      - watch_url   : YouTube watch link for 'Open in YouTube' button, or null
      - type        : 'youtube' | 'youtube_short' | 'file' | 'external'
      - thumbnail   : absolute thumbnail URL (may be empty string)

    Keeping all URL normalisation here lets the JS stay simple.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    video_data = []

    for v in recipe.videos.all():
        # Prefer HLS stream → external URL → raw uploaded file
        source_url = v.hls_stream_url or v.external_url or ""
        raw_file_url = (
            request.build_absolute_uri(v.raw_video_file.url)
            if v.raw_video_file else ""
        )
        thumbnail_url = (
            request.build_absolute_uri(v.thumbnail.url)
            if v.thumbnail else ""
        )
        title = v.title or f"{recipe.name} Video"

        youtube_id = _extract_youtube_id(source_url)

        if youtube_id:
            # YouTube URL (any format) → convert to embeddable URL
            embed_url = (
                f"https://www.youtube.com/embed/{youtube_id}"
                f"?rel=0&modestbranding=1&playsinline=1"
            )
            watch_url = f"https://www.youtube.com/watch?v={youtube_id}"
            video_type = "youtube_short" if _is_short_url(source_url) else "youtube"

        elif raw_file_url:
            # Uploaded video file — served via Django media
            embed_url = raw_file_url
            watch_url = None
            video_type = "file"

        elif source_url:
            # Some other embeddable URL (Vimeo, HLS player, etc.)
            embed_url = source_url
            watch_url = None
            video_type = "external"

        else:
            continue  # No valid video source — skip this record

        video_data.append({
            "title": title,
            "embed_url": embed_url,
            "watch_url": watch_url,
            "type": video_type,
            "thumbnail": thumbnail_url,
        })

    # ---- Fallback: YouTube Data API v3 search ----
    if not video_data:
        api_key = config('YOUTUBE_API_KEY', default=None)
        if api_key:
            try:
                res = requests.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": f"{recipe.name} recipe",
                        "key": api_key,
                        "maxResults": 3,
                        "type": "video",
                    },
                    timeout=5,
                )
                if res.status_code == 200:
                    for item in res.json().get("items", []):
                        vid = item["id"]["videoId"]
                        video_data.append({
                            "title": item["snippet"]["title"],
                            "embed_url": (
                                f"https://www.youtube.com/embed/{vid}"
                                f"?rel=0&modestbranding=1&playsinline=1"
                            ),
                            "watch_url": f"https://www.youtube.com/watch?v={vid}",
                            "type": "youtube",
                            "thumbnail": (
                                item["snippet"]["thumbnails"]
                                .get("high", {})
                                .get("url", "")
                            ),
                        })
            except Exception:
                pass  # Graceful degradation — log to Sentry/etc. in production

    return JsonResponse({"videos": video_data})