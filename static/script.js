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
window.toggleHeart = function(btn) {
    const icon = btn.querySelector('.heart-icon');
    if (icon.getAttribute('fill') === 'none') {
        icon.setAttribute('fill', 'currentColor');
        icon.classList.add('text-primary', 'scale-125');
        btn.classList.add('bg-white', 'text-primary', 'border-white', 'shadow-lg');
        btn.classList.remove('bg-white/20', 'text-white', 'border-white/30');
        if (typeof Toastify !== 'undefined') {
            Toastify({ 
                text: "Recipe saved!", 
                duration: 2000, 
                style: { background: "#1E293B", color: "#fff", borderRadius: "100px", border: "1px solid #F97316"} 
            }).showToast();
        }
    } else {
        icon.setAttribute('fill', 'none');
        icon.classList.remove('text-primary', 'scale-125');
        btn.classList.remove('bg-white', 'text-primary', 'border-white', 'shadow-lg');
        btn.classList.add('bg-white/20', 'text-white', 'border-white/30');
    }
};

function fetchRecipes() {
    fetch('/api/recipes/')
        .then(response => response.json())
        .then(data => {
            const allRecipes = data.all_recipes || [];
            const similarRecipes = data.similar_recipes || [];

            function createRecipeCard(recipe) {
                // Null-guard every optional field — avoids showing literal "null" text
                const diet      = recipe.diet      || '';
                const cuisine   = recipe.cuisine   || '—';
                const course    = recipe.course    || '—';
                const prepTime  = recipe.prep_time || '—';

                // Image element: show the photo if available, otherwise a styled placeholder
                // The serializer field is named 'image' (not 'image_url').
                // DRF returns a full absolute URL when context={'request': request} is set.
                const imageHTML = recipe.image
                    ? `<img
                            src="${recipe.image}"
                            alt="${recipe.name}"
                            loading="lazy"
                            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                        />`
                    : `<div class="w-full h-full flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-400">
                            <svg class="w-12 h-12 mb-2 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
                            <span class="text-xs font-semibold uppercase tracking-wide">No Photo</span>
                        </div>`;

                return `
                    <a href="/detail/${recipe.id}/" target="_blank" onclick="handleRecipeClick('${recipe.id}')" class="group block outline-none h-full">
                        <div class="relative glass-panel bg-white dark:bg-[#121212] rounded-[2rem] overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_20px_40px_-20px_rgba(249,115,22,0.4)] border border-gray-100 dark:border-white/5 h-full flex flex-col">

                            <div class="relative h-72 w-full overflow-hidden bg-slate-200 dark:bg-slate-800">
                                ${imageHTML}
                                <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-70 group-hover:opacity-90 transition-opacity duration-300"></div>

                                ${diet ? `<div class="absolute top-4 left-4 flex gap-2 z-10">
                                    <span class="px-3 py-1 text-[10px] font-black uppercase tracking-widest rounded-full bg-success/90 backdrop-blur-md text-white shadow-sm border border-white/20">
                                        ${diet}
                                    </span>
                                </div>` : ''}

                                <button onclick="event.preventDefault(); window.toggleHeart(this);" class="absolute top-4 right-4 p-2.5 rounded-full bg-white/20 backdrop-blur-md text-white border border-white/30 hover:bg-white hover:text-primary transition-all duration-300 focus:outline-none z-30 group/heart hover:scale-110 hover:shadow-lg">
                                    <svg class="w-5 h-5 heart-icon transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
                                </button>

                                <div class="absolute bottom-4 right-4 translate-y-6 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 ease-out z-20">
                                    <div class="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/40 hover:scale-110 transition-transform">
                                        <svg class="w-5 h-5 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                                    </div>
                                </div>
                            </div>

                            <div class="p-6 flex flex-col flex-grow relative z-10">
                                <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2 line-clamp-2 leading-snug group-hover:text-primary transition-colors">
                                    ${recipe.name}
                                </h3>

                                <div class="flex flex-wrap items-center gap-2 text-xs font-bold text-slate-500 dark:text-slate-400 mb-4 uppercase tracking-wider">
                                    <span>${cuisine}</span>
                                    <span class="w-1 h-1 rounded-full bg-slate-300 dark:bg-white/20"></span>
                                    <span class="text-accent">${course}</span>
                                </div>

                                <div class="mt-auto pt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                                    <span class="flex items-center gap-1.5 text-sm font-bold text-slate-700 dark:text-slate-200 bg-slate-50 dark:bg-white/5 px-3 py-1 rounded-full">
                                        <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        ${prepTime}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </a>
                `;
            }

            const allRecipesContainer = document.getElementById('all-recipes');
            if (allRecipesContainer) {
                // Remove skeleton and inject elements
                allRecipesContainer.innerHTML = allRecipes.map(recipe => createRecipeCard(recipe)).join('');
            }

            const similarRecipesContainer = document.getElementById('similar-recipes');
            if (similarRecipesContainer) {
                similarRecipesContainer.innerHTML = similarRecipes.map(recipe => createRecipeCard(recipe)).join('');
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            const allRecipesContainer = document.getElementById('all-recipes');
            if (allRecipesContainer) {
                allRecipesContainer.innerHTML = '<div class="col-span-full text-center py-12 text-slate-500">Failed to load recommendations. Please try again.</div>';
            }
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

    // Use a relative URL so the app works on any host/port
    fetch(`/api/activity/?recipe_id=${recipeId}`)
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