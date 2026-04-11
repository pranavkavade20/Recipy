from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Recipe Management
    path('add/', views.add_recipe, name='add_recipe'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('update/<int:recipe_id>/', views.update_recipe, name='update_recipe'),
    path('delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    
    # Meal Planner
    path('meal-planner/', views.view_meal_plans, name='view_meal_plans'),
    path('meal-planner/add/', views.add_meal_plan, name='add_meal_plan'),
    
    # Recommendations & APIs
    path('detail/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('api/recipe/<int:id>/', views.RecipeDetailAPI.as_view()),
    path('api/recipes/', views.RecipeAPI.as_view()),
    path('api/activity/', views.LogUserActivity.as_view()),
    
    # Search
    path("search-my-recipes/", views.search_user_recipes, name='search_user_recipes'),
    path('search/', views.search_page, name='search_page'),
    path('api/search/', views.search_recipes, name='search_recipes'),
    
    # Favorites
    path('save-favorite/', views.save_favorite_recipe, name='save_favorite_recipe'),
    path('saved-recipes/', views.get_saved_recipes, name='get_saved_recipes'),
    path('remove-favorite/', views.remove_saved_recipe, name='remove_saved_recipe'),
    
    # Video
    path('videos/<int:recipe_id>/', views.get_recipe_videos, name='recipe_videos'),
]