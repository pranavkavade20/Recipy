from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, MealPlanner, RecipeVideo

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'recipe_type', 'image', 'cuisine', 'course', 'diet', 'prep_time', 'instructions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...', 'rows': 4}),
            'recipe_type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'block w-full...'}),
        }

IngredientFormSet = inlineformset_factory(
    Recipe, Ingredient, fields=('name',),
    widgets={'name': forms.TextInput(attrs={'class': 'flex-grow w-full px-4 py-3 rounded-xl bg-stone-50...'})},
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
        widgets = {
            'recipe': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'meal_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'meal_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'meal_type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl bg-gray-50...', 'rows': 3}),
        }