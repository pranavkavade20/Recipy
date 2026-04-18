from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, MealPlanner, RecipeVideo

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'recipe_type', 'image', 'cuisine', 'course', 'diet', 'prep_time', 'instructions']

IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient, fields=('name',),
    extra=1, can_delete=True,
)

RecipeVideoFormSet = inlineformset_factory(
    Recipe, RecipeVideo, fields=('title', 'external_url', 'raw_video_file'),
    extra=1, can_delete=True,
)

class MealPlannerForm(forms.ModelForm):
    class Meta:
        model = MealPlanner
        fields = ['recipe', 'meal_date', 'meal_time', 'meal_type', 'notes']