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
        icon.classList.add('text-orange-500', 'scale-110');
        btn.classList.add('bg-white/90', 'dark:bg-bg-slate-800 /90', 'border-slate-200', 'dark:border-white/20', 'shadow-md');
        btn.classList.remove('bg-black/20', 'text-white', 'border-white/30');
        
        // Premium Apple-style Notification
        if (typeof Toastify !== 'undefined') {
            Toastify({ 
                text: "Recipe saved!", 
                duration: 2500, 
                gravity: "top",
                position: "center",
                style: { 
                    background: "rgba(255, 255, 255, 0.8)", 
                    backdropFilter: "blur(20px)",
                    WebkitBackdropFilter: "blur(20px)",
                    color: "#0f172a", 
                    borderRadius: "100px", 
                    border: "1px solid rgba(255, 255, 255, 0.4)",
                    boxShadow: "0 10px 40px -10px rgba(0,0,0,0.1)",
                    fontWeight: "700",
                    fontSize: "14px",
                    padding: "12px 24px",
                    marginTop: "80px"
                } 
            }).showToast();
        }
    } else {
        icon.setAttribute('fill', 'none');
        icon.classList.remove('text-orange-500', 'scale-110');
        btn.classList.remove('bg-white/90', 'dark:bg-bg-slate-800 /90', 'border-slate-200', 'dark:border-white/20', 'shadow-md');
        btn.classList.add('bg-black/20', 'text-white', 'border-white/30');
    }
};

function fetchRecipes() {
    fetch('/api/recipes/')
        .then(response => response.json())
        .then(data => {
            const allRecipes = data.all_recipes || [];

            function createRecipeCard(recipe) {
                // Null-guard every optional field — avoids showing literal "null" text
                const diet      = recipe.diet      || '';
                const cuisine   = recipe.cuisine   || '—';
                const course    = recipe.course    || '—';
                const prepTime  = recipe.prep_time || '—';

                // Image element: show the photo if available, otherwise a styled placeholder
                const imageHTML = recipe.image
                    ? `<img
                            src="${recipe.image}"
                            alt="${recipe.name}"
                            loading="lazy"
                            class="w-full h-full object-cover transition-transform duration-1000 ease-out group-hover:scale-105"
                        />`
                    : `<div class="w-full h-full flex flex-col items-center justify-center bg-slate-100 dark:bg-bg-slate-800  text-slate-400">
                            <svg class="w-10 h-10 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                            </svg>
                            <span class="text-[10px] font-black uppercase tracking-widest">No Photo</span>
                        </div>`;

                return `
                    <a href="/detail/${recipe.id}/" target="_blank" onclick="handleRecipeClick('${recipe.id}')" class="group block outline-none h-full">
                        <div class="relative dark:bg-bg-slate-800 backdrop-blur-xl rounded-[2rem] overflow-hidden transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-[0_20px_40px_-10px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_20px_40px_-10px_rgba(0,0,0,0.5)] border border-slate-200/60 dark:border-white/5 h-full flex flex-col group-hover:border-slate-300 dark:group-hover:border-white/10">

                            <div class="relative h-64 sm:h-72 w-full overflow-hidden bg-slate-200 dark:bg-slate-800 rounded-t-[2rem]">
                                ${imageHTML}
                                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-500 pointer-events-none"></div>

                                ${diet ? `<div class="absolute top-4 left-4 flex gap-2 z-10">
                                    <span class="px-3 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-full bg-black/30 backdrop-blur-md text-white shadow-sm border border-white/20">
                                        ${diet}
                                    </span>
                                </div>` : ''}

                                <button onclick="event.preventDefault(); window.toggleHeart(this);" class="absolute top-4 right-4 p-2.5 rounded-full bg-black/20 backdrop-blur-md text-white border border-white/30 hover:bg-white/90 hover:text-orange-500 transition-all duration-300 focus:outline-none z-30 group/heart hover:scale-110 shadow-sm">
                                    <svg class="w-4 h-4 sm:w-5 sm:h-5 heart-icon transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
                                </button>
                                
                                <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-20 pointer-events-none">
                                    <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-md border border-white/30 flex items-center justify-center text-white shadow-xl transform scale-75 group-hover:scale-100 transition-transform duration-500 ease-out">
                                        <svg class="w-5 h-5 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                                    </div>
                                </div>
                            </div>

                            <div class="p-5 sm:p-6 flex flex-col flex-grow relative z-10 bg-gradient-to-b from-white/50 to-white/10 dark:from-white/5 dark:to-transparent">
                                <h3 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white mb-2 line-clamp-2 leading-tight tracking-tight group-hover:text-orange-500 transition-colors duration-300">
                                    ${recipe.name}
                                </h3>

                                <div class="flex flex-wrap items-center gap-2 text-[10px] sm:text-xs font-black text-slate-400 dark:text-slate-500 mb-4 uppercase tracking-widest">
                                    <span>${cuisine}</span>
                                    <span class="w-1 h-1 rounded-full bg-slate-300 dark:bg-white/20"></span>
                                    <span class="text-orange-500 dark:text-orange-400">${course}</span>
                                </div>

                                <div class="mt-auto pt-4 flex items-center justify-between border-t border-slate-200/50 dark:border-white/5">
                                    <span class="flex items-center gap-1.5 text-xs font-bold text-slate-600 dark:text-slate-300 bg-white/80 dark:bg-white/10 shadow-sm border border-slate-200/50 dark:border-white/5 px-3 py-1.5 rounded-full">
                                        <svg class="w-3.5 h-3.5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
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
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            const allRecipesContainer = document.getElementById('all-recipes');
            if (allRecipesContainer) {
                allRecipesContainer.innerHTML = '<div class="col-span-full text-center py-12 text-sm font-medium text-slate-500 bg-white/50 dark:bg-bg-slate-800 /50 backdrop-blur-xl rounded-[2rem] border border-slate-200 dark:border-white/5">Failed to load recommendations. Please try again.</div>';
            }
        });
}

function handleRecipeClick(recipeId) {
    if (typeof Toastify !== 'undefined') {
        Toastify({
            text: "Loading recipe...",
            duration: 3000,
            close: false,
            gravity: "top", 
            position: "center", 
            style: {
                background: "rgba(15, 23, 42, 0.85)", // Dark premium backdrop
                backdropFilter: "blur(20px)",
                WebkitBackdropFilter: "blur(20px)",
                color: "#fff",
                borderRadius: "100px",
                padding: "12px 24px",
                fontSize: "14px",
                fontWeight: "700",
                boxShadow: "0 20px 40px -10px rgba(0,0,0,0.3)",
                border: "1px solid rgba(255,255,255,0.1)",
                marginTop: "80px"
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