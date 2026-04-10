from rest_framework import serializers
from .models import Recipe, UserRecipeActivity

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class UserRecipeActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRecipeActivity
        fields = ['user', 'recipe', 'action', 'timestamp']