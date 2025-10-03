from rest_framework import serializers
from .models import Recipe, UserRecipeActivity

# Serializer for Recipe model
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'  # Serialize all fields of the Recipe model

# Serializer for UserRecipeActivity model

class UserRecipeActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRecipeActivity
        fields = ['user', 'recipe', 'action', 'timestamp']

