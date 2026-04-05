/**
 * 🎨 Premium App UI JavaScript
 * Handles Theming, Dynamic Feed Loading, and Interactions
 */

// --- Theme Toggler Logic (Bulletproof Class-based logic) ---
const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
const themeToggleDarkIcons = document.querySelectorAll('.theme-toggle-dark-icon');
const themeToggleLightIcons = document.querySelectorAll('.theme-toggle-light-icon');

// Initialize theme on load
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
    themeToggleLightIcons.forEach(icon => icon.classList.remove('hidden'));
} else {
    document.documentElement.classList.remove('dark');
    themeToggleDarkIcons.forEach(icon => icon.classList.remove('hidden'));
}

function toggleTheme() {
    // Toggle icons visually across all buttons
    themeToggleDarkIcons.forEach(icon => icon.classList.toggle('hidden'));
    themeToggleLightIcons.forEach(icon => icon.classList.toggle('hidden'));

    // Toggle HTML class and save
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
    }
}

// Attach event listener to ALL theme buttons
themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', toggleTheme);
});


// --- Dynamic Feed Loading ---
function fetchRecipes() {
    fetch('http://127.0.0.1:8000/recipes/')
        .then(response => response.json())
        .then(data => {
            const allRecipes = data.all_recipes || [];
            const similarRecipes = data.similar_recipes || [];

            function createRecipeCard(recipe) {
                return `
                    <a href="/recipe_detail/${recipe.id}" target="_blank" onclick="handleRecipeClick('${recipe.id}')" class="group block outline-none">
                        <div class="relative glass-panel bg-white dark:bg-[#121212] rounded-[2rem] overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(249,115,22,0.3)] border border-gray-100 dark:border-white/5 h-full flex flex-col">
                            
                            <div class="relative h-64 w-full overflow-hidden bg-gray-200 dark:bg-gray-800">
                                <img 
                                    src="${recipe.image_url}" 
                                    alt="${recipe.name}" 
                                    loading="lazy"
                                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
                                />
                                <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-70 group-hover:opacity-90 transition-opacity duration-300"></div>
                                
                                <div class="absolute top-4 left-4 flex gap-2 z-10">
                                    <span class="px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-full bg-black/40 backdrop-blur-md text-white border border-white/20">
                                        ${recipe.diet}
                                    </span>
                                </div>

                                <div class="absolute bottom-4 right-4 translate-y-6 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 ease-out z-20">
                                    <div class="w-14 h-14 rounded-full bg-orange-500 flex items-center justify-center text-white shadow-lg shadow-orange-500/50 hover:scale-110 transition-transform">
                                        <svg class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="p-6 flex flex-col flex-grow relative z-10">
                                <h3 class="text-xl font-black text-gray-900 dark:text-white mb-2 line-clamp-2 leading-snug group-hover:text-orange-500 transition-colors">
                                    ${recipe.name}
                                </h3>

                                <div class="flex flex-wrap items-center gap-2 text-xs font-bold text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wider">
                                    <span>${recipe.cuisine}</span>
                                    <span class="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600"></span>
                                    <span class="text-orange-500">${recipe.course}</span>
                                </div>

                                <div class="mt-auto pt-4 border-t border-gray-100 dark:border-white/5 flex items-center justify-between">
                                    <span class="flex items-center gap-1.5 text-sm font-bold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-white/5 px-3 py-1 rounded-full">
                                        <svg class="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        ${recipe.prep_time}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </a>
                `;
            }

            const allRecipesContainer = document.getElementById('all-recipes');
            if (allRecipesContainer) {
                allRecipesContainer.innerHTML = allRecipes.map(recipe => createRecipeCard(recipe)).join('');
            }

            const similarRecipesContainer = document.getElementById('similar-recipes');
            if (similarRecipesContainer) {
                similarRecipesContainer.innerHTML = similarRecipes.map(recipe => createRecipeCard(recipe)).join('');
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function handleRecipeClick(recipeId) {
    if (typeof Toastify !== 'undefined') {
        Toastify({
            text: "Loading recipe...",
            duration: 3000,
            close: false,
            gravity: "bottom", 
            position: "center", 
            style: {
                background: "rgba(255, 255, 255, 0.1)",
                backdropFilter: "blur(16px)",
                WebkitBackdropFilter: "blur(16px)",
                color: "#fff",
                borderRadius: "100px",
                padding: "12px 24px",
                fontSize: "14px",
                fontWeight: "700",
                boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
                border: "1px solid rgba(255,255,255,0.1)",
                marginBottom: "80px"
            }
        }).showToast();
    }

    fetch(`http://127.0.0.1:8000/activity/?recipe_id=${recipeId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Activity tracked:', recipeId);
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

openButton?.addEventListener("click", () => {
    slideOver.classList.remove("hidden");
    requestAnimationFrame(() => {
        backdrop.classList.remove("opacity-0");
        panel.classList.remove("translate-x-full");
    });
});

closeButton?.addEventListener("click", () => {
    backdrop.classList.add("opacity-0");
    panel.classList.add("translate-x-full");
    setTimeout(() => slideOver.classList.add("hidden"), 500); 
});