from django.contrib import admin
from .models import Receipe,Ingredients, MealPlanner
from .models import Recipe, UserRecipeActivity

admin.site.register(Receipe)
admin.site.register(Ingredients)

@admin.register(MealPlanner)
class MealPlannerAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'meal_date', 'meal_type', 'meal_time')
    list_filter = ('meal_date', 'meal_type')
    search_fields = ('recipe__receipe_name', 'user__username')

# Admin class for UserRecipeActivity model
class UserRecipeActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'action', 'timestamp')  # Fields to display in the list
    search_fields = ('user__username', 'recipe__name', 'action')  # Fields to search in the admin
    list_filter = ('action', 'timestamp')  # Fields to filter by in the admin
    ordering = ('-timestamp',)  # Ordering by timestamp, newest first

# Register the models and their respective admin classes
admin.site.register(Recipe)
admin.site.register(UserRecipeActivity, UserRecipeActivityAdmin)
