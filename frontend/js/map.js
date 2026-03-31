let map;
let globalArrondissementsData = null;
let currentGeoJSON = { type: "FeatureCollection", features: [] };
let activeMetric = "indice_qdv"; // Métrique par defaut
const ZOOM_PARIS = 11.5;
const CENTER_PARIS = [2.3488, 48.8534];

const COLORS = {
    "indice_qdv": ['#064e3b', '#10b981'],
    "indice_mobilite": ['#0c4a6e', '#0ea5e9'],
    "indice_culture": ['#78350f', '#f59e0b'],
    "indice_tension": ['#7f1d1d', '#ef4444']
};

async function initMap() {
    // Style MapLibre vide de base avec des tuiles OSM sombres via CARTO
    map = new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: CENTER_PARIS,
        zoom: ZOOM_PARIS,
        pitch: 45, // Vue légèrement penchée
        attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-left');

    map.on('load', async () => {
        // Charger le GeoJSON des arrondissements depuis l'API
        const geojsonData = await UrbanAPI.getArrondissementsGeoJSON();
        currentGeoJSON = geojsonData;

        map.addSource('arrondissements', {
            type: 'geojson',
            data: currentGeoJSON
        });

        // Couche de remplissage (Choroplèthe)
        map.addLayer({
            id: 'arrondissements-fill',
            type: 'fill',
            source: 'arrondissements',
            paint: {
                'fill-color': getChoroplethStyle(activeMetric),
                'fill-opacity': [
                    'case',
                    ['boolean', ['feature-state', 'hover'], false],
                    0.8,
                    0.6
                ]
            }
        });

        // Lignes de bordures
        map.addLayer({
            id: 'arrondissements-line',
            type: 'line',
            source: 'arrondissements',
            paint: {
                'line-color': 'rgba(255,255,255,0.3)',
                'line-width': 1
            }
        });

        setupMapInteractions();
        updateGlobalView(); // Initialiser la vue globale
    });
}

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

function updateMapMetric(metricName) {
    activeMetric = metricName;
    if (map.getLayer('arrondissements-fill')) {
        map.setPaintProperty('arrondissements-fill', 'fill-color', getChoroplethStyle(metricName));
    }
}

let hoveredStateId = null;

function setupMapInteractions() {
    // Hover
    map.on('mousemove', 'arrondissements-fill', (e) => {
        if (e.features.length > 0) {
            // Mettre le curseur
            map.getCanvas().style.cursor = 'pointer';
            
            // Feature_state hover
            const feature = e.features[0];
            const arrId = feature.properties.arrondissement;
            
            if (hoveredStateId !== null) {
                map.setFeatureState(
                    { source: 'arrondissements', id: hoveredStateId },
                    { hover: false }
                );
            }
            // Attention: maplibre a besoin d'un id unique
            // Si pas d'id natif, on s'arrange
            hoveredStateId = feature.id || arrId;
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

    // Click => Selection Sidebar
    map.on('click', 'arrondissements-fill', (e) => {
        if (e.features.length > 0) {
            const arrId = e.features[0].properties.arrondissement;
            selectArrondissement(arrId);
        }
    });
}

// ---- Layers Toggles ----
const POINT_LAYERS = {
    'layer-velib': { dataset: 'velib', color: '#38bdf8', icon: 'bicycle' },
    'layer-belib': { dataset: 'belib', color: '#a855f7', icon: 'bolt' },
    'layer-ecoles': { dataset: 'ecoles', color: '#fbbf24', icon: 'school' },
    'layer-monuments': { dataset: 'monuments_historiques', color: '#f87171', icon: 'monument' },
    'layer-social': { dataset: 'logements_sociaux', color: '#f43f5e', icon: 'home' }
};

async function togglePointLayer(layerId, isChecked) {
    const config = POINT_LAYERS[layerId];
    if (!config) return;

    if (isChecked) {
        if (!map.getSource(layerId)) {
            const data = await UrbanAPI.getDatasetGeoJSON(config.dataset);
            if (!data) return;
            map.addSource(layerId, { type: 'geojson', data: data });
            
            map.addLayer({
                id: `${layerId}-circles`,
                type: 'circle',
                source: layerId,
                paint: {
                    'circle-radius': 4,
                    'circle-color': config.color,
                    'circle-opacity': 0.8,
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#000'
                }
            });
            
            // Popups
            map.on('click', `${layerId}-circles`, (e) => {
                const props = e.features[0].properties;
                new maplibregl.Popup()
                    .setLngLat(e.lngLat)
                    .setHTML(`<h4>${props.nom || props.adresse || 'Inconnu'}</h4>`)
                    .addTo(map);
            });
            map.on('mouseenter', `${layerId}-circles`, () => map.getCanvas().style.cursor = 'pointer');
            map.on('mouseleave', `${layerId}-circles`, () => map.getCanvas().style.cursor = '');
        } else {
            map.setLayoutProperty(`${layerId}-circles`, 'visibility', 'visible');
        }
    } else {
        if (map.getLayer(`${layerId}-circles`)) {
            map.setLayoutProperty(`${layerId}-circles`, 'visibility', 'none');
        }
    }
}
