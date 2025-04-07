document.addEventListener('DOMContentLoaded', function() {
    console.log('Energy Monitoring Dashboard Loaded');
    // Get data from data attributes
    const chartDataElement = document.getElementById('chartData');
    let hourlyData = [];
    let anomalies = [];
    
    try {
        hourlyData = JSON.parse(chartDataElement.dataset.hourly || '[]');
        anomalies = JSON.parse(chartDataElement.dataset.anomalies || '[]');
    } catch (e) {
        console.error('Error parsing chart data:', e);
        // Fallback data in case of parsing error
        hourlyData = [50, 49, 48, 46, 45, 46, 60, 80, 110, 120, 130, 140, 150, 140, 130, 120, 110, 100, 90, 80, 70, 60, 55, 53];
    }
    
    // Prepare anomaly data points
    const anomalyData = Array(24).fill(null);
    if (anomalies && anomalies.length > 0) {
        anomalies.forEach(anomaly => {
            if (anomaly && typeof anomaly.index === 'number') {
                anomalyData[anomaly.index] = anomaly.value;
            }
        });
    }
    
    // Main Chart - Energy Consumption Over Time
    const mainChartCtx = document.getElementById('mainChart').getContext('2d');
    const mainChart = new Chart(mainChartCtx, {
        type: 'line',
        data: {
            labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', 
                     '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', 
                     '20:00', '21:00', '22:00', '23:00'],
            datasets: [
                {
                    label: 'Electricity (kWh)',
                    data: hourlyData,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#4CAF50',
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: 'Anomalies',
                    data: anomalyData,
                    borderColor: 'transparent',
                    backgroundColor: 'transparent',
                    pointBackgroundColor: 'red',
                    pointBorderColor: 'red',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false,
                    pointStyle: 'circle'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 15
                    }
                },
                title: {
                    display: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Energy Consumption (kWh)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time of Day'
                    }
                }
            }
        }
    });
    
    // Log anomalies for debugging
    if (anomalies && anomalies.length > 0) {
        console.log('Anomalies found:', anomalies);
    } else {
        console.log('No anomalies found or anomalies data is invalid');
    }
    
    // Export chart as image
    document.getElementById('downloadChartBtn').addEventListener('click', function() {
        const link = document.createElement('a');
        link.download = 'energy-consumption-chart.png';
        link.href = mainChart.toBase64Image();
        link.click();
    });
});
