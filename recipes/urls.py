from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import get_recipe_videos, get_saved_recipes, recipe_detail, RecipeDetailAPI, RecipeAPI,LogUserActivity, remove_saved_recipe, save_favorite_recipe
from .views import search_page, search_recipes
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(),name='login'),
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),
    
    #password change
    path('password_change/',auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    
    #reset password
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    
    # user registration
    path('register/',views.register,name='register'),

    # recipes manage
    path('add-recipe/', views.add_recipe, name='add_recipe'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('meal-planner/', views.view_meal_plans, name='view_meal_plans'),
    path('meal-planner/add/', views.add_meal_plan, name='add_meal_plan'),
    path('recipe/update/<int:recipe_id>/', views.update_recipe, name='update_recipe'),
    path('recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path("search/", views. search_user_recipes, name='search_user_recipes'),

    #recommendation
    path('recipe_detail/<id>/', recipe_detail),
    path('recipe/<id>/', RecipeDetailAPI.as_view()),
    path('recipes/', RecipeAPI.as_view()),
    path('activity/', LogUserActivity.as_view()),
    path('search_page/', search_page, name='search_page'),  # Frontend search page
    path('api/search/', search_recipes, name='search_recipes'),  # Search API endpoint
    
    # Favorite recipes
    path('recipe_detail/<int:id>/', recipe_detail, name='recipe_detail'),
    path('save_favorite/', save_favorite_recipe, name='save_favorite_recipe'),
    path('saved_recipes/', get_saved_recipes, name='get_saved_recipes'),
    path('remove_saved_recipe/', remove_saved_recipe, name='remove_saved_recipe'),
    path('recipe_videos/<int:recipe_id>/', get_recipe_videos, name='recipe_videos'),

]
 