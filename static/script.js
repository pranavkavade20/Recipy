//Theme Toggler Functionality
var themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
var themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

// Change the icons inside the button based on previous settings
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    themeToggleLightIcon.classList.remove('hidden');
} else {
    themeToggleDarkIcon.classList.remove('hidden');
}

var themeToggleBtn = document.getElementById('theme-toggle');

themeToggleBtn.addEventListener('click', function () {

    // toggle icons inside button
    themeToggleDarkIcon.classList.toggle('hidden');
    themeToggleLightIcon.classList.toggle('hidden');

    // if set via local storage previously
    if (localStorage.getItem('color-theme')) {
        if (localStorage.getItem('color-theme') === 'light') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        }

        // if NOT set via local storage previously
    } else {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        }
    }
});

// On page load or when changing themes, best to add inline in `head` to avoid FOUC
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
} else {
    document.documentElement.classList.remove('dark')
}

// Fetch recipes from the API
function fetchRecipes() {
    fetch('http://127.0.0.1:8000/recipes/')
        .then(response => response.json())
        .then(data => {
            // Extract all recipes and similar recipes
            const allRecipes = data.all_recipes;
            const similarRecipes = data.similar_recipes;

            // Function to create recipe cards
            function createRecipeCard(recipe) {
                return `
                   <a href="/recipe_detail/${recipe.id}" target="_blank" class="block group">
                        <div class="relative overflow-hidden rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform group-hover:-translate-y-1 h-full flex flex-col bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
                            <div class="relative">
                                <img src="${recipe.image_url}" alt="${recipe.name}" class="w-full h-52 object-cover transition-transform duration-500 group-hover:scale-105" />
                                <span class="absolute top-4 right-4 px-3 py-1 text-xs font-bold rounded-full bg-green-600 text-white shadow-md">
                                    ${recipe.diet}
                                </span>
                            </div>
                            
                            <div class="p-5 flex flex-col flex-grow">
                                <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
                                    ${recipe.name.split(' ').slice(0, 6).join(' ')}
                                </h3>

                                <div class="flex flex-wrap items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                    <span class="font-medium">${recipe.cuisine}</span>
                                    <span class="text-gray-300 dark:text-gray-600">•</span>
                                    <span class="font-semibold text-orange-500">${recipe.course}</span>
                                </div>

                                <div class="flex items-center justify-between mt-4 pt-2 border-t border-gray-100 dark:border-gray-700">
                                    <span class="flex items-center gap-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
                
                                        ${recipe.prep_time}
                                    </span>
                                    
                                    <span class="text-orange-500 hover:text-orange-600 font-bold transition-colors">
                                        View Recipe &rarr;
                                    </span>
                                </div>
                            </div>
                        </div>
                    </a>
                    `;
            }

            // Insert all recipes into the 'all-recipes' section
            const allRecipesContainer = document.getElementById('all-recipes');
            allRecipesContainer.innerHTML = '';
            allRecipes.forEach(recipe => {
                allRecipesContainer.innerHTML += createRecipeCard(recipe);
            });

            // Insert similar recipes into the 'similar-recipes' section
            const similarRecipesContainer = document.getElementById('similar-recipes');
            similarRecipesContainer.innerHTML = '';
            similarRecipes.forEach(recipe => {
                similarRecipesContainer.innerHTML += createRecipeCard(recipe);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Handle recipe click and make API call
function handleRecipeClick(recipeId) {
    // Show the toast message using Toastify
    Toastify({
        text: "You clicked this recipe!",
        duration: 3000,  // Display for 3 seconds
        close: true,  // Show close button
        gravity: "bottom",  // Position at the bottom
        position: "right",  // Position at the right
        backgroundColor: "linear-gradient(to right, #00b09b, #96c93d)", // Greenish color
    }).showToast();

    // Call the API with the recipe ID
    fetch(`http://127.0.0.1:8000/activity/?recipe_id=${recipeId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Activity recorded for recipe:', recipeId);
            console.log('API response:', data);
            fetchRecipes();
        })
        .catch(error => {
            console.error('Error calling activity API:', error);
        });
}
fetchRecipes();

const openButton = document.getElementById("open-button");
const closeButton = document.getElementById("close-button");
const slideOver = document.getElementById("slide-over");
const backdrop = document.getElementById("backdrop");
const panel = document.getElementById("panel");

openButton.addEventListener("click", () => {
    slideOver.classList.remove("hidden");
    backdrop.classList.remove("opacity-0");
    panel.classList.remove("translate-x-full");
});

closeButton.addEventListener("click", () => {
    backdrop.classList.add("opacity-0");
    panel.classList.add("translate-x-full");
    setTimeout(() => slideOver.classList.add("hidden"), 500);
});