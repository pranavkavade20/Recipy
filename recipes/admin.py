from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, Ingredient, RecipeVideo, MealPlanner, UserRecipeActivity


# 1. Setup Inlines for seamless related-model editing
class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1  # Number of empty rows to display
    classes = ('collapse',) # Keeps the UI clean by making it collapsible

class RecipeVideoInline(admin.StackedInline):
    model = RecipeVideo
    extra = 0
    fields = ('title', 'external_url', 'raw_video_file', 'hls_stream_url', 'thumbnail')
    classes = ('collapse',)

# 2. Register the main Recipe Admin
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # -- List View Settings --
    list_display = (
        'name', 
        'author', 
        'recipe_type', 
        'tag', 
        'cuisine', 
        'created_at', 
        'image_preview'
    )
    list_filter = ('tag', 'recipe_type', 'cuisine', 'course', 'diet', 'created_at')
    search_fields = ('name', 'description', 'cuisine', 'author__username', 'author__email')
    
    # Performance optimization: Reduces database hits when displaying the author
    list_select_related = ('author',)
    
    # Use raw_id_fields or autocomplete_fields for ForeignKeys to prevent 
    # loading thousands of users into a single dropdown in production.
    raw_id_fields = ('author',)
    
    # Make 'tag' readonly because your model's save() method forcefully overwrites it. 
    # If it's editable, admins will get confused when their manual changes are reverted.
    readonly_fields = ('tag', 'created_at', 'updated_at', 'image_preview')

    # -- Detail View Settings (Fieldsets) --
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'author', 'description', 'instructions')
        }),
        ('Categorization', {
            'fields': ('recipe_type', 'cuisine', 'course', 'diet', 'prep_time')
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
        }),
        ('System & Status', {
            'fields': ('tag', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Hide system fields by default
        }),
    )

    inlines = [IngredientInline, RecipeVideoInline]

    # -- Custom Methods --
    @admin.display(description='Preview')
    def image_preview(self, obj):
        """Generates a small thumbnail preview of the recipe image in the admin grid."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', 
                obj.image.url
            )
        return format_html('<span style="color: #999;">No Image</span>')

# (Optional) If you ever want to manage Videos or Ingredients independently of Recipes:
@admin.register(RecipeVideo)
class RecipeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipe', 'created_at')
    search_fields = ('title', 'recipe__name')
    list_select_related = ('recipe',)
    raw_id_fields = ('recipe',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipe')
    search_fields = ('name', 'recipe__name')
    list_select_related = ('recipe',)
    raw_id_fields = ('recipe',)

@admin.register(MealPlanner)
class MealPlannerAdmin(admin.ModelAdmin):
    # -- List View Settings --
    list_display = ('user', 'recipe', 'meal_date', 'meal_time', 'meal_type')
    list_filter = ('meal_type', 'meal_date')
    
    # Adds a clickable date drill-down breadcrumb bar at the top of the admin list
    date_hierarchy = 'meal_date' 
    
    search_fields = ('user__username', 'user__email', 'recipe__name', 'notes')
    
    # Performance optimization for ForeignKeys
    list_select_related = ('user', 'recipe')
    raw_id_fields = ('user', 'recipe')
    
    readonly_fields = ('created_at',)

    # -- Detail View Settings --
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'recipe')
        }),
        ('Scheduling', {
            'fields': ('meal_date', 'meal_time', 'meal_type')
        }),
        ('Details', {
            'fields': ('notes', 'created_at')
        }),
    )

@admin.register(UserRecipeActivity)
class UserRecipeActivityAdmin(admin.ModelAdmin):
    # -- List View Settings --
    list_display = ('user', 'action', 'recipe', 'timestamp')
    list_filter = ('action', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('user__username', 'user__email', 'recipe__name')
    
    # Performance optimization for ForeignKeys
    list_select_related = ('user', 'recipe')
    raw_id_fields = ('user', 'recipe')

    # -- Data Integrity (Immutability) --
    # User activities are telemetry/analytics logs. Admins should NEVER be able 
    # to manually add, edit, or tamper with this data, as it ruins metrics.
    
    def has_add_permission(self, request):
        """Prevent creation of fake activity logs via the admin panel."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing of existing activity logs."""
        return False

    def get_readonly_fields(self, request, obj=None):
        """Dynamically make all fields read-only for view-only purposes."""
        return [f.name for f in self.model._meta.fields]