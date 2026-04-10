from django.contrib import admin
from .models import Recipe, Ingredient, RecipeVideo, MealPlanner, UserRecipeActivity

# ---------------------------------------------------------
# Inlines (Allows editing related models directly inside the Recipe admin page)
# ---------------------------------------------------------
class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1  # Number of empty rows to show by default

class RecipeVideoInline(admin.TabularInline):
    model = RecipeVideo
    extra = 1

# ---------------------------------------------------------
# Main Admin Classes
# ---------------------------------------------------------
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'tag', 'recipe_type', 'created_at')
    list_filter = ('tag', 'recipe_type', 'cuisine', 'course')
    search_fields = ('name', 'author__username', 'description')
    inlines = [IngredientInline, RecipeVideoInline]
    
    # Optional: If you want to make 'tag' read-only since the model's save() method overrides it anyway
    # readonly_fields = ('tag',)

@admin.register(MealPlanner)
class MealPlannerAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'meal_date', 'meal_type', 'meal_time')
    list_filter = ('meal_date', 'meal_type')
    # Fixed the old 'recipe__receipe_name' to match the merged model's 'name' attribute
    search_fields = ('recipe__name', 'user__username')

@admin.register(UserRecipeActivity)
class UserRecipeActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'action', 'timestamp')
    search_fields = ('user__username', 'recipe__name', 'action')
    list_filter = ('action', 'timestamp')
    ordering = ('-timestamp',)

# Note: We don't need to do admin.site.register() at the bottom anymore 
# because we used the @admin.register() decorator above each class!