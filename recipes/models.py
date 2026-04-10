from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Recipe(models.Model):
    TAG_CHOICES = (
                ('Premium', 'Premium'), 
                ('Normal', 'Normal')
            )
    TYPE_CHOICES = (
        ("Veg", "Veg"), 
        ("Non-veg", "Non-veg")
        )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    image = models.ImageField(upload_to="recipe_images/", blank=True, null=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='Normal')
    
    recipe_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Veg')
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    diet = models.CharField(max_length=100, blank=True, null=True)
    prep_time = models.CharField(max_length=50, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.author or (self.author and self.author.is_superuser):
            self.tag = 'Premium'
        else:
            self.tag = 'Normal'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.tag}]"

class RecipeVideo(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')
    title = models.CharField(max_length=255, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, help_text="Provide a YouTube or Vimeo URL")
    raw_video_file = models.FileField(
        upload_to='recipe_videos/raw/', 
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi'])]
    )
    hls_stream_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='recipe_videos/thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for {self.recipe.name}"

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,null=True, blank=True, related_name="ingredients")
    name = models.CharField(max_length=255)

    def __str__(self):
       return f"{self.name} ({self.recipe.name})"

class MealPlanner(models.Model):
    MEAL_TYPES = (
        ("Breakfast", "Breakfast"), 
        ("Lunch", "Lunch"), 
        ("Dinner", "Dinner"), 
        ("Snack", "Snack")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,null=True, blank=True, related_name="meal_plans")
    meal_date = models.DateField()
    meal_time = models.TimeField(null=True, blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-meal_date', 'meal_time']
        verbose_name = "Meal Planner"
        verbose_name_plural = "Meal Planners"

class UserRecipeActivity(models.Model):
    ACTION_CHOICES = [('favorite', 'Favorite'), ('view', 'View')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)