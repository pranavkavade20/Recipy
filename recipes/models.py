from django.db import models
from django.contrib.auth.models import User 

class Receipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)  # User who owns the recipe
    receipe_name = models.CharField(max_length=100, db_index=True)
    receipe_description = models.TextField()
    receipe_image = models.ImageField(upload_to="receipe_img/", blank=True, null=True)
    receipe_type = models.CharField(
        max_length=100, choices=(("Veg", "Veg"), ("Non-veg", "Non-veg"))
    )
    ingredients = { 
        "data" : [models.CharField(max_length=100),], 
    } 
    def __str__(self):
        return self.receipe_name

class Ingredients(models.Model):
    receipe = models.ForeignKey( Receipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredients_name = models.CharField(max_length=255)

    def __str__(self):
       return f"{self.ingredients_name} ----> ({self.receipe.receipe_name})"

class MealPlanner(models.Model):
    MEAL_TYPES = (
        ("Breakfast", "Breakfast"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
        ("Snack", "Snack"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    recipe = models.ForeignKey(Receipe, on_delete=models.CASCADE, related_name="meal_plans")
    meal_date = models.DateField()  # Date for the planned meal
    meal_time = models.TimeField(null=True, blank=True)  # Optional time of the meal
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)  # Meal type (Breakfast, Lunch, etc.)
    notes = models.TextField(blank=True, null=True)  # Optional notes for the meal

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-meal_date', 'meal_time']
        verbose_name = "Meal Planner"
        verbose_name_plural = "Meal Planners"

    def __str__(self):
        return f"{self.recipe.receipe_name} - {self.meal_type} on {self.meal_date}"

# In your app's models.py

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    # Changed to ImageField, which stores the path relative to MEDIA_ROOT
    image_url = models.ImageField(upload_to='recipe/') 
    description = models.TextField()
    cuisine = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    diet = models.CharField(max_length=100, blank=True, null=True)
    prep_time = models.CharField(max_length=50, blank=True, null=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserRecipeActivity(models.Model):
    ACTION_CHOICES = [
        ('favorite', 'Favorite'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.recipe.name}"
