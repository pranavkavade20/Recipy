# recipes_app/management/commands/import_recipes.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
# Assuming you have already set up your Recipe model in recipes_app.models
from recipes.models import Recipe 

class Command(BaseCommand):
    help = 'Imports recipe data from recipes.csv, generating sequential local image paths (1.jpg, 2.jpg, etc.).'

    def add_arguments(self, parser):
        # Optional: Allow the user to specify the path to the CSV file
        parser.add_argument('csv_file', type=str, nargs='?', default='recipes.csv', help='The path to the recipes.csv file.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        if not os.path.exists(csv_file_path):
            raise CommandError(f"CSV file not found at: {csv_file_path}")

        self.stdout.write(self.style.NOTICE(f"Loading data from {csv_file_path}..."))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                recipes_to_create = []
                # START COUNT at 1 to match 1.jpg, 2.jpg, etc.
                recipe_count = 1 
                total_imported = 0

                for row in reader:
                    # Skip rows without a name or that are empty
                    if not row.get('name', '').strip():
                        continue

                    # 1. GENERATE THE SEQUENTIAL FILENAME
                    # The image name is derived from the counter: 1.jpg, 2.jpg, etc.
                    # We assume all images are .jpg. If they are .png, change this line.
                    local_image_filename = f"{recipe_count}.jpg"
                    
                    # ImageField stores the path relative to MEDIA_ROOT + upload_to='recipe/'
                    local_image_path = f"recipe/{local_image_filename}"
                    
                    # 2. Clean up data (ingredients/instructions)
                    cleaned_ingredients = row.get('ingredients', '').strip().replace('\t', '').replace('\n', ' ')
                    cleaned_instructions = row.get('instructions', '').strip().replace('\t', '').replace('\n', ' ')

                    # 3. Create the Recipe object
                    recipe = Recipe(
                        name=row.get('name', '').strip(),
                        # Populating the ImageField with the sequential file path
                        image=local_image_path, 
                        description=row.get('description', '').strip(),
                        cuisine=row.get('cuisine', '').strip(),
                        course=row.get('course', '').strip(),
                        diet=row.get('diet', '').strip() if row.get('diet') else None,
                        prep_time=row.get('prep_time', '').strip(),
                        ingredients=cleaned_ingredients,
                        instructions=cleaned_instructions,
                    )
                    recipes_to_create.append(recipe)
                    
                    # Increment the counter for the next row/image
                    recipe_count += 1
                    total_imported += 1

                # 4. Bulk create all recipes for better performance
                Recipe.objects.bulk_create(recipes_to_create)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {total_imported} Recipe records, assigning sequential image names (1.jpg, 2.jpg, ...).'))

        except Exception as e:
            raise CommandError(f'Error during import: {e}')