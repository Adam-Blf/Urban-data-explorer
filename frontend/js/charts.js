// Charts Definition
let housingChartInstance = null;
let servicesChartInstance = null;
let compareRadarInstance = null;

Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Outfit', sans-serif";

function initCharts() {
    // Boilerplate until we load data
}

function updateHousingChart(data) {
    const ctx = document.getElementById('housingChart').getContext('2d');
    if (housingChartInstance) housingChartInstance.destroy();

    housingChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Logements Sociaux (en dizaines)', 'Prix m² (en K€)'],
            datasets: [{
                label: 'Métriques',
                data: [
                    (data.logements_sociaux || 0) / 10, 
                    (data.prix_m2 || 0) / 1000
                ],
                backgroundColor: [
                    'rgba(244, 63, 94, 0.6)', 
                    'rgba(59, 130, 246, 0.6)'
                ],
                borderColor: [
                    '#f43f5e',
                    '#3b82f6'
                ],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            aspectRatio: 1.5,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function updateServicesChart(data) {
    const ctx = document.getElementById('servicesChart').getContext('2d');
    if (servicesChartInstance) servicesChartInstance.destroy();

    servicesChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Ecoles', 'Toilettes', 'Marchés'],
            datasets: [{
                data: [data.nb_ecoles || 0, data.nb_toilettes || 0, data.nb_marches || 0],
                backgroundColor: [
                    'rgba(52, 211, 153, 0.7)',
                    'rgba(14, 165, 233, 0.7)',
                    'rgba(245, 158, 11, 0.7)'
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            aspectRatio: 1.5,
            cutout: '60%',
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

function updateComparisonRadar(data1, data2, name1, name2) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    if (compareRadarInstance) compareRadarInstance.destroy();

    compareRadarInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Qualité de Vie', 'Mobilité', 'Culture', 'Tension Immo'],
            datasets: [
                {
                    label: name1,
                    data: [data1.indice_qdv, data1.indice_mobilite, data1.indice_culture, data1.indice_tension],
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: '#3b82f6',
                    pointBackgroundColor: '#3b82f6',
                },
                {
                    label: name2,
                    data: [data2.indice_qdv, data2.indice_mobilite, data2.indice_culture, data2.indice_tension],
                    backgroundColor: 'rgba(244, 63, 94, 0.2)',
                    borderColor: '#f43f5e',
                    pointBackgroundColor: '#f43f5e',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255,255,255,0.1)' },
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    pointLabels: { color: '#94a3b8', font: { size: 14 } },
                    ticks: { display: false, min: 0, max: 100 }
                }
            },
            plugins: {
                legend: { position: 'top', labels: { color: '#fff', font: { size: 14 } } }
            }
        }
    });
}
