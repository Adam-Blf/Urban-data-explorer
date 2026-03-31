/**
 * Module Principal de l'Application Frontend (UI Logic)
 * Auteur : Emilien MORICE (emilien754)
 * Rôle : Gestion des interactions utilisateur, mise à jour des KPI et orchestration des composants.
 * Architecture : Event-Driven / Vanilla JS.
 */

document.addEventListener("DOMContentLoaded", async () => {
    console.log("🏙️ Urban Data Explorer : Initialisation de l'interface...");

    // 1. Initialisation des composants visuels (Cartes & Graphiques)
    initCharts();
    await initMap();
    
    // 2. Hydratation des données via l'API Gold
    // Chargement des indicateurs par arrondissement (1-20)
    globalArrondissementsData = await UrbanAPI.getIndicators();
    
    if (globalArrondissementsData) {
        console.log("✅ Données analytiques chargées avec succès.");
        populateSelects();
    } else {
        console.error("❌ Échec du chargement des données. Vérifiez si l'API FastAPI est lancée.");
        alert("Attention: Impossible de charger les indicateurs depuis l'API.");
    }

    // 3. Configuration des écouteurs d'événements (Event Listeners)

    // Sélection de l'arrondissement via le dropdown principal
    document.getElementById("arrondissement-select").addEventListener("change", (e) => {
        selectArrondissement(parseInt(e.target.value));
    });

    // Interaction thématique via les cartes KPI (Change la métrique de la carte)
    const kpiCards = document.querySelectorAll(".kpi-card");
    kpiCards.forEach((card, index) => {
        card.addEventListener("click", () => {
            const metrics = ["score_vie", "score_mob", "score_pat", "score_ten"];
            updateMapMetric(metrics[index]);
            
            // Feedback Visuel : Highlight la carte sélectionnée
            kpiCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            
            // Style dynamique basé sur l'icône
            const iconColor = getComputedStyle(card.querySelector('.kpi-icon')).color;
            kpiCards.forEach(c => c.style.borderColor = "rgba(255,255,255,0.1)");
            card.style.borderColor = iconColor;
        });
    });

    // Gestion des Toggles (Point Layers : Velib, Belib, Ecoles, etc.)
    const toggles = document.querySelectorAll('.toggle-control input');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            togglePointLayer(e.target.id, e.target.checked);
        });
    });

    // Orchestration du Comparateur (Modal)
    document.getElementById("btn-compare").addEventListener("click", () => {
        document.getElementById("compare-modal").classList.remove("hidden");
        updateComparison(); 
    });
    
    document.getElementById("close-compare").addEventListener("click", () => {
        document.getElementById("compare-modal").classList.add("hidden");
    });
    
    document.getElementById("compare-1").addEventListener("change", updateComparison);
    document.getElementById("compare-2").addEventListener("change", updateComparison);
    
    // État initial : Sélection de la première thématique (Qualité de vie)
    kpiCards[0].click(); 
});

/**
 * Remplit les menus déroulants avec les 20 arrondissements de Paris.
 */
function populateSelects() {
    const mainSelect = document.getElementById("arrondissement-select");
    const c1 = document.getElementById("compare-1");
    const c2 = document.getElementById("compare-2");
    
    for (let i = 1; i <= 20; i++) {
        const text = `Paris ${i}e`;
        mainSelect.add(new Option(text, i));
        c1.add(new Option(text, i));
        
        const opt2 = new Option(text, i);
        if (i === 18) opt2.selected = true; // Exemple par défaut : 1er vs 18e
        c2.add(opt2);
    }
}

/**
 * Met à jour l'ensemble de l'interface pour un arrondissement donné.
 * @param {number} id - Numéro de l'arrondissement (1-20).
 */
function selectArrondissement(id) {
    if (id === 0) {
        updateGlobalView();
        map.flyTo({ center: [2.3488, 48.8534], zoom: 12 });
        return;
    }
    
    const data = globalArrondissementsData[id];
    if (data) {
        updateUI(data);
        // Zoom automatique sur l'arrondissement via la carte (si nécessaire)
    }
}

/**
 * Affiche les statistiques moyennes pour tout Paris.
 */
function updateGlobalView() {
    if (!globalArrondissementsData) return;
    
    let sumQDv = 0, sumMob = 0, sumCul = 0, sumTen = 0;
    const count = Object.keys(globalArrondissementsData).length;
    
    for (let key in globalArrondissementsData) {
        sumQDv += globalArrondissementsData[key].qualite_vie || 0;
        sumMob += globalArrondissementsData[key].mobilite || 0;
        sumCul += globalArrondissementsData[key].patrimoine || 0;
        sumTen += globalArrondissementsData[key].tension || 0;
    }

    const avgData = {
        qualite_vie: Math.round(sumQDv / count),
        mobilite: Math.round(sumMob / count),
        patrimoine: Math.round(sumCul / count),
        tension: Math.round(sumTen / count),
        details: { prix_m2: 10500, logements_sociaux: 250000 }
    };
    
    updateUI(avgData);
}

/**
 * Rafraîchit les KPI et les graphiques.
 * @param {Object} data - Données Gold de l'arrondissement.
 */
function updateUI(data) {
    // Animation fluide des chiffres
    animateCount("kpi-qdv", data.qualite_vie);
    animateCount("kpi-mob", data.mobilite);
    animateCount("kpi-cul", data.patrimoine);
    animateCount("kpi-ten", data.tension);
    
    // Mise à jour des barres de progression
    document.getElementById("bar-qdv").style.width = `${data.qualite_vie}%`;
    document.getElementById("bar-mob").style.width = `${data.mobilite}%`;
    document.getElementById("bar-cul").style.width = `${data.patrimoine}%`;
    document.getElementById("bar-ten").style.width = `${data.tension}%`;
    
    // Mise à jour des graphiques Chart.js
    updateHousingChart(data);
    updateServicesChart(data);
}

/**
 * Met à jour le graphique de comparaison Radar.
 */
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

/**
 * Helper : Animation de compteur (CountUp) pour les KPI.
 */
function animateCount(elemId, target) {
    const el = document.getElementById(elemId);
    let start = 0;
    const duration = 800;
    const steps = 20;
    const stepTime = duration / steps;
    const increment = target / steps;
    
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
