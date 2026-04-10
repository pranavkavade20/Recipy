from rest_framework import serializers
from .models import Recipe, UserRecipeActivity


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'image', 'tag', 'recipe_type',
            'cuisine', 'course', 'diet', 'prep_time', 'instructions',
            'created_at', 'updated_at', 'author',
        ]
        read_only_fields = ['tag', 'created_at', 'updated_at']


class UserRecipeActivitySerializer(serializers.ModelSerializer):
    # 'user' is injected by the view via serializer.save(user=request.user);
    # 'timestamp' is auto-set by the model. Both must be read-only to
    # prevent clients from spoofing these values.
    class Meta:
        model = UserRecipeActivity
        fields = ['user', 'recipe', 'action', 'timestamp']
        read_only_fields = ['user', 'timestamp']