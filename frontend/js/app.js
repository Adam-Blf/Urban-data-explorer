document.addEventListener("DOMContentLoaded", async () => {
    // 1. Initialiser UI & Maps
    initCharts();
    await initMap();
    
    // 2. Récupérer les données Globales (Indicateurs)
    globalArrondissementsData = await UrbanAPI.getIndicators();
    if (globalArrondissementsData) {
        populateSelects();
    } else {
        alert("Attention: Impossible de charger les indicateurs de l'API. Avez-vous lancé le backend ?");
    }

    // 3. Event Listeners
    document.getElementById("arrondissement-select").addEventListener("change", (e) => {
        selectArrondissement(parseInt(e.target.value));
    });

    // Changement de métrique quand on clique sur une carte KPI
    const kpiCards = document.querySelectorAll(".kpi-card");
    kpiCards.forEach((card, index) => {
        card.addEventListener("click", () => {
            const metrics = ["indice_qdv", "indice_mobilite", "indice_culture", "indice_tension"];
            updateMapMetric(metrics[index]);
            
            // Highlight
            kpiCards.forEach(c => c.style.border = "1px solid rgba(255,255,255,0.1)");
            card.style.border = `1px solid ${getComputedStyle(card.querySelector('.kpi-icon')).color}`;
        });
    });

    // Toggles de couches
    const toggles = document.querySelectorAll('.toggle-control input');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            togglePointLayer(e.target.id, e.target.checked);
        });
    });

    // Comparateur Modals
    document.getElementById("btn-compare").addEventListener("click", () => {
        document.getElementById("compare-modal").classList.remove("hidden");
        updateComparison(); // First draw
    });
    
    document.getElementById("close-compare").addEventListener("click", () => {
        document.getElementById("compare-modal").classList.add("hidden");
    });
    
    document.getElementById("compare-1").addEventListener("change", updateComparison);
    document.getElementById("compare-2").addEventListener("change", updateComparison);
    
    // Default selection
    kpiCards[0].click(); 
});

function populateSelects() {
    const mainSelect = document.getElementById("arrondissement-select");
    const c1 = document.getElementById("compare-1");
    const c2 = document.getElementById("compare-2");
    
    // Vider
    // On garde l'option 0 pour la mainSelect
    for (let i = 1; i <= 20; i++) {
        const text = `Paris ${i}e`;
        mainSelect.add(new Option(text, i));
        c1.add(new Option(text, i));
        
        const opt2 = new Option(text, i);
        if (i === 2) opt2.selected = true; // par defaut 1 vs 2
        c2.add(opt2);
    }
}

function selectArrondissement(id) {
    document.getElementById("arrondissement-select").value = id;
    
    if (id === 0) {
        updateGlobalView();
        map.flyTo({ center: CENTER_PARIS, zoom: ZOOM_PARIS });
        return;
    }
    
    // Update KPI & Charts
    const data = globalArrondissementsData[id];
    if (data) {
        updateUI(data);
    }
    
    // Zoom in map to that arrondissement feature
    if (currentGeoJSON && currentGeoJSON.features) {
        const feature = currentGeoJSON.features.find(f => f.properties.arrondissement === id);
        if (feature) {
            // Rough center based on the poly's bbox
            // (A true implementation would use turf.js, but since maplibre flyto zooms to center, we just approximate or keep zoom)
            // Lacking simple polygon center in vanilla JS without turf, we just zoom slightly.
            // On s'en passe pour cette démo, on utilise juste le flyto.
        }
    }
}

function updateGlobalView() {
    // Affiche les moyennes ou sommes globales de Paris
    if (!globalArrondissementsData) return;
    
    let sumQDv = 0, sumMob = 0, sumCul = 0, sumTen = 0;
    
    const count = Object.keys(globalArrondissementsData).length;
    for (let key in globalArrondissementsData) {
        sumQDv += globalArrondissementsData[key].indice_qdv || 0;
        sumMob += globalArrondissementsData[key].indice_mobilite || 0;
        sumCul += globalArrondissementsData[key].indice_culture || 0;
        sumTen += globalArrondissementsData[key].indice_tension || 0;
    }

    const mockData = {
        indice_qdv: Math.round(sumQDv / count),
        indice_mobilite: Math.round(sumMob / count),
        indice_culture: Math.round(sumCul / count),
        indice_tension: Math.round(sumTen / count),
        logements_sociaux: 0, // Placeholder
        prix_m2: 10500, // Moyenne
        nb_ecoles: 20,
        nb_toilettes: 15,
        nb_marches: 4
    };
    
    updateUI(mockData);
}

function updateUI(data) {
    animateCount("kpi-qdv", data.indice_qdv);
    animateCount("kpi-mob", data.indice_mobilite);
    animateCount("kpi-cul", data.indice_culture);
    animateCount("kpi-ten", data.indice_tension);
    
    document.getElementById("bar-qdv").style.width = `${data.indice_qdv}%`;
    document.getElementById("bar-mob").style.width = `${data.indice_mobilite}%`;
    document.getElementById("bar-cul").style.width = `${data.indice_culture}%`;
    document.getElementById("bar-ten").style.width = `${data.indice_tension}%`;
    
    updateHousingChart(data);
    updateServicesChart(data);
}

function updateComparison() {
    const id1 = document.getElementById("compare-1").value;
    const id2 = document.getElementById("compare-2").value;
    
    if (globalArrondissementsData && globalArrondissementsData[id1] && globalArrondissementsData[id2]) {
        updateComparisonRadar(
            globalArrondissementsData[id1], 
            globalArrondissementsData[id2],
            `Paris ${id1}e`, 
            `Paris ${id2}e`
        );
    }
}

// Helper pour animer les chiffres
function animateCount(elemId, target) {
    const el = document.getElementById(elemId);
    let start = 0;
    const duration = 1000;
    const stepTime = Math.abs(Math.floor(duration / 30));
    
    const increment = target / 30;
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            el.innerText = Math.round(target);
            clearInterval(timer);
        } else {
            el.innerText = Math.round(start);
        }
    }, stepTime);
}
