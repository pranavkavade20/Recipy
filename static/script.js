document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Toggler Logic ---
    const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
    const themeToggleDarkIcons = document.querySelectorAll('.theme-toggle-dark-icon');
    const themeToggleLightIcons = document.querySelectorAll('.theme-toggle-light-icon');

    // Initialize theme
    if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        themeToggleLightIcons.forEach(icon => icon.classList.remove('hidden'));
    } else {
        document.documentElement.classList.remove('dark');
        themeToggleDarkIcons.forEach(icon => icon.classList.remove('hidden'));
    }

    function toggleTheme() {
        themeToggleDarkIcons.forEach(icon => icon.classList.toggle('hidden'));
        themeToggleLightIcons.forEach(icon => icon.classList.toggle('hidden'));

        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        }
    }

    themeToggleBtns.forEach(btn => btn.addEventListener('click', toggleTheme));

    // --- Dynamic Feed Loading ---
    function fetchRecipes() {
        const allRecipesContainer = document.getElementById('all-recipes');
        if (!allRecipesContainer) return; // Exit if not on feed page

        fetch('/api/recipes/')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                const allRecipes = data.all_recipes || [];

                function createRecipeCard(recipe) {
                    const diet = recipe.diet || '';
                    const prepTime = recipe.prep_time || '—';
                    const imageHTML = recipe.image
                        ? `<img src="${recipe.image}" alt="${recipe.name}" loading="lazy" class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105" />`
                        : `<div class="w-full h-full flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-400">
                              <span class="text-xs font-semibold uppercase tracking-wider">No Photo</span>
                           </div>`;

                    return `
                        <a href="/detail/${recipe.id}/" target="_blank" onclick="window.handleRecipeClick('${recipe.id}')" class="group block h-full outline-none focus:ring-2 focus:ring-orange-500 rounded-2xl">
                            <div class="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-lg border border-slate-200 dark:border-slate-800 h-full flex flex-col">
                                <div class="relative h-48 w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
                                    ${imageHTML}
                                    ${diet ? `<div class="absolute top-3 left-3">
                                        <span class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md bg-white/90 dark:bg-slate-900/90 text-slate-900 dark:text-white backdrop-blur shadow-sm border border-slate-200 dark:border-slate-700">
                                            ${diet}
                                        </span>
                                    </div>` : ''}
                                </div>
                                <div class="p-5 flex flex-col flex-grow">
                                    <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2 line-clamp-2 leading-snug group-hover:text-orange-500 transition-colors">
                                        ${recipe.name}
                                    </h3>
                                    <div class="mt-auto pt-4 flex items-center justify-between border-t border-slate-100 dark:border-slate-800">
                                        <span class="text-xs font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                            ${prepTime}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </a>
                    `;
                }

                allRecipesContainer.innerHTML = allRecipes.map(recipe => createRecipeCard(recipe)).join('');
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                allRecipesContainer.innerHTML = '<div class="col-span-full text-center py-12 text-sm text-slate-500 border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl">Failed to load recipes. Please refresh.</div>';
            });
    }

    fetchRecipes();
});

// --- Global Functions (Attached to window for inline HTML onclicks) ---
window.handleRecipeClick = function(recipeId) {
    if (typeof Toastify !== 'undefined') {
        Toastify({
            text: "Loading recipe...",
            duration: 2000,
            gravity: "bottom", 
            position: "right", 
            style: {
                background: "#0f172a",
                color: "#fff",
                borderRadius: "8px",
                padding: "12px 20px",
                fontSize: "14px",
                fontWeight: "500",
                boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)",
            }
        }).showToast();
    }

    fetch(`/api/activity/?recipe_id=${recipeId}`)
        .catch(error => console.error('Error tracking activity:', error));
};