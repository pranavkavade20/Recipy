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
                        <div class="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl border border-slate-100 dark:border-slate-800 h-full flex flex-col relative">
                                
                                <div class="relative h-48 sm:h-52 w-full overflow-hidden bg-slate-100 dark:bg-slate-800 shrink-0">
                                    ${imageHTML}
                                    
                                    <div class="absolute top-3 left-3 flex flex-col gap-2">
                                        <span class="px-2.5 py-1 text-[10px] sm:text-xs font-bold uppercase tracking-wider rounded-md bg-white/95 dark:bg-slate-900/95 text-slate-900 dark:text-white shadow-sm border border-slate-200/50 dark:border-slate-700/50 backdrop-blur-sm">
                                            ${recipe.diet}
                                        </span>
                                    </div>

                                    <div class="absolute top-3 right-3 flex flex-col gap-2">
                                        <span class="px-2.5 py-1 text-[10px] sm:text-xs font-semibold tracking-wide rounded-md bg-orange-500 text-white shadow-sm backdrop-blur-sm">
                                            ${recipe.type}
                                        </span>
                                    </div>
                                </div>

                                <div class="p-4 sm:p-5 flex flex-col flex-grow">
                                    
                                    <h3 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 line-clamp-2 leading-snug group-hover:text-orange-500 transition-colors">
                                        ${recipe.name}
                                    </h3>
                                    <div class="flex items-center flex-wrap gap-2 text-[11px] sm:text-xs mb-4 font-medium tracking-wide">
                                        <span class="px-3 py-1.5 rounded-xl bg-slate-50/50 dark:bg-slate-800/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-700/50 shadow-[inset_0_1px_1px_rgba(255,255,255,0.8),0_2px_6px_rgba(0,0,0,0.04)] dark:shadow-[inset_0_1px_1px_rgba(255,255,255,0.05),0_2px_6px_rgba(0,0,0,0.2)] text-slate-700 dark:text-slate-200 transition-all hover:bg-slate-100/60 dark:hover:bg-slate-700/50">
                                            ${recipe.cuisine}
                                        </span>
                                        
                                        <span class="px-3 py-1.5 rounded-xl bg-slate-50/50 dark:bg-slate-800/40 backdrop-blur-md border border-slate-200/60 dark:border-slate-700/50 shadow-[inset_0_1px_1px_rgba(255,255,255,0.8),0_2px_6px_rgba(0,0,0,0.04)] dark:shadow-[inset_0_1px_1px_rgba(255,255,255,0.05),0_2px_6px_rgba(0,0,0,0.2)] text-slate-700 dark:text-slate-200 transition-all hover:bg-slate-100/60 dark:hover:bg-slate-700/50">
                                            ${recipe.course}
                                        </span>
                                    </div>

                                    <div class="mt-auto pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                                        <div class="flex items-center gap-1.5 text-slate-700 dark:text-slate-200 font-semibold text-sm">
                                            <svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                              ${ prepTime}
                                        </div>
                                        
                                        <span class="text-xs font-bold text-orange-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center gap-1">
                                            View <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
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