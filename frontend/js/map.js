/**
 * Module de Gestion Cartographique (MapLibre GL JS)
 * Auteur : Emilien MORICE (emilien754)
 * Rôle : Initialisation de la carte, gestion des couches (Fill/Line/Points) 
 *        et rendu des choroplèthes thématiques.
 */

let map;
let globalArrondissementsData = null;
let currentGeoJSON = { type: "FeatureCollection", features: [] };
let activeMetric = "score_vie"; // Métrique par défaut liée au bouton actif
const ZOOM_PARIS = 11.2;
const CENTER_PARIS = [2.3488, 48.8534];

// Palettes de couleurs thématiques (Gradients HSL optimisés pour mode sombre)
const COLORS = {
    "score_vie": ['#064e3b', '#10b981'], // Vert -> Nature/Santé
    "score_mob": ['#0c4a6e', '#0ea5e9'], // Bleu -> Technologie/Transport
    "score_pat": ['#78350f', '#f59e0b'], // Ambre -> Culture/Histoire
    "score_ten": ['#7f1d1d', '#ef4444']  // Rouge -> Alerte/Tension
};

/**
 * Initialise le moteur de rendu cartographique.
 * Charge le fond de carte "Carto Dark Matter" et les données Gold.
 */
async function initMap() {
    console.log("🗺️ Initialisation de la carte MapLibre...");
    
    map = new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: CENTER_PARIS,
        zoom: ZOOM_PARIS,
        pitch: 20, // Inclinaison légère pour l'effet 3D
        attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-left');

    map.on('load', async () => {
        // Récupération des polygones enrichis via l'API Gold
        const geojsonData = await UrbanAPI.getArrondissementsGeoJSON();
        currentGeoJSON = geojsonData;

        map.addSource('arrondissements', {
            type: 'geojson',
            data: currentGeoJSON,
            generateId: true // Nécessaire pour le feature-state
        });

        // 1. Couche Choroplèthe (Remplissage dynamique selon le score)
        map.addLayer({
            id: 'arrondissements-fill',
            type: 'fill',
            source: 'arrondissements',
            paint: {
                'fill-color': getChoroplethStyle(activeMetric),
                'fill-opacity': [
                    'case',
                    ['boolean', ['feature-state', 'hover'], false],
                    0.85, // Opacité augmentée au survol
                    0.55
                ]
            }
        });

        // 2. Couche Bordures (Délimitation des quartiers)
        map.addLayer({
            id: 'arrondissements-line',
            type: 'line',
            source: 'arrondissements',
            paint: {
                'line-color': 'rgba(255,255,255,0.25)',
                'line-width': 1.2
            }
        });

        setupMapInteractions();
        updateGlobalView(); // Premier rendu de la sidebar (Vue Paris entier)
    });
}

/**
 * Génère l'expression de style MapLibre pour l'interpolation de couleur.
 * @param {string} metric - La propriété du GeoJSON à visualiser.
 */
function getChoroplethStyle(metric) {
    const colorStops = COLORS[metric] || ['#1e293b', '#94a3b8'];
    return [
        'interpolate',
        ['linear'],
        ['get', metric],
        0, colorStops[0],
        100, colorStops[1]
    ];
}

/**
 * Change la thématique visuelle de la carte.
 * @param {string} metricName - Nom de la métrique (ex: score_vie).
 */
function updateMapMetric(metricName) {
    activeMetric = metricName;
    if (map.getLayer('arrondissements-fill')) {
        map.setPaintProperty('arrondissements-fill', 'fill-color', getChoroplethStyle(metricName));
    }
}

let hoveredStateId = null;

/**
 * Configure les événements de souris (Hover, Click, Popups).
 */
function setupMapInteractions() {
    // Effet de survol (Hover)
    map.on('mousemove', 'arrondissements-fill', (e) => {
        if (e.features.length > 0) {
            map.getCanvas().style.cursor = 'crosshair';
            
            if (hoveredStateId !== null) {
                map.setFeatureState(
                    { source: 'arrondissements', id: hoveredStateId },
                    { hover: false }
                );
            }
            
            hoveredStateId = e.features[0].id;
            map.setFeatureState(
                { source: 'arrondissements', id: hoveredStateId },
                { hover: true }
            );
        }
    });

    map.on('mouseleave', 'arrondissements-fill', () => {
        map.getCanvas().style.cursor = '';
        if (hoveredStateId !== null) {
            map.setFeatureState(
                { source: 'arrondissements', id: hoveredStateId },
                { hover: false }
            );
        }
        hoveredStateId = null;
    });

    // Sélection d'un quartier au clic
    map.on('click', 'arrondissements-fill', (e) => {
        if (e.features.length > 0) {
            const arrNum = e.features[0].properties.num_arr;
            // Transformation en entier car l'API attend un nombre 1-20
            selectArrondissement(parseInt(arrNum));
        }
    });
}

// Configuration des couches de points (Layer Toggling Logic)
const POINT_LAYERS = {
    'layer-velib': { dataset: 'velib', color: '#10b981' },
    'layer-belib': { dataset: 'belib', color: '#a855f7' },
    'layer-ecoles': { dataset: 'ecoles', color: '#fbbf24' },
    'layer-monuments': { dataset: 'monuments_historiques', color: '#f87171' },
    'layer-social': { dataset: 'logements_sociaux', color: '#ec4899' }
};

/**
 * Active ou désactive l'affichage d'un type de service sur la carte.
 * @param {string} layerId - ID HTML du control toggle.
 * @param {boolean} isChecked - État du checkbox.
 */
async function togglePointLayer(layerId, isChecked) {
    const config = POINT_LAYERS[layerId];
    if (!config) return;

    if (isChecked) {
        if (!map.getSource(layerId)) {
            // Lazy-loading des données depuis l'API Silver
            const data = await UrbanAPI.getDatasetGeoJSON(config.dataset);
            if (!data) return;
            map.addSource(layerId, { type: 'geojson', data: data });
            
            map.addLayer({
                id: `${layerId}-dots`,
                type: 'circle',
                source: layerId,
                paint: {
                    'circle-radius': 4.5,
                    'circle-color': config.color,
                    'circle-opacity': 0.9,
                    'circle-stroke-width': 1.5,
                    'circle-stroke-color': '#000'
                }
            });
            
            // Interaction Popup sur les points
            map.on('click', `${layerId}-dots`, (e) => {
                const p = e.features[0].properties;
                new maplibregl.Popup({ closeButton: false, className: 'glass-popup' })
                    .setLngLat(e.lngLat)
                    .setHTML(`<div class="popup-content"><strong>${p.nom || p.adresse || 'Service'}</strong></div>`)
                    .addTo(map);
            });

            map.on('mouseenter', `${layerId}-dots`, () => map.getCanvas().style.cursor = 'pointer');
            map.on('mouseleave', `${layerId}-dots`, () => map.getCanvas().style.cursor = '');
        } else {
            map.setLayoutProperty(`${layerId}-dots`, 'visibility', 'visible');
        }
    } else {
        if (map.getLayer(`${layerId}-dots`)) {
            map.setLayoutProperty(`${layerId}-dots`, 'visibility', 'none');
        }
    }
}
