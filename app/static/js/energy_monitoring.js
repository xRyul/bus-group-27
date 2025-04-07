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
    
    // Function to initialize charts only if their elements exist
    function initializeCharts() {
        // Main Chart - Energy Consumption Over Time
        const mainChartEl = document.getElementById('mainChart');
        if (mainChartEl) {
            // Prepare anomaly data points
            const anomalyData = Array(24).fill(null);
            if (anomalies && anomalies.length > 0) {
                anomalies.forEach(anomaly => {
                    if (anomaly && typeof anomaly.index === 'number') {
                        anomalyData[anomaly.index] = anomaly.value;
                    }
                });
            }
            
            const mainChartCtx = mainChartEl.getContext('2d');
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
            
            // Export chart as image if the button exists
            const downloadBtn = document.getElementById('downloadChartBtn');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', function() {
                    const link = document.createElement('a');
                    link.download = 'energy-consumption-chart.png';
                    link.href = mainChart.toBase64Image();
                    link.click();
                });
            }
        }
        
        // Initialize the Energy Mix Donut Chart
        const energyMixEl = document.getElementById('energyMixChart');
        if (energyMixEl) {
            // Get the container, not just the canvas, to ensure context
            const energyMixContainer = energyMixEl.parentElement; 
            if (energyMixContainer && energyMixContainer.offsetHeight > 0) { // Check container visibility/height
                const energyMixCtx = energyMixEl.getContext('2d');
                new Chart(energyMixCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Grid Electricity', 'Natural Gas', 'Solar PV', 'Other Renewables'],
                        datasets: [{
                            data: [58, 10, 25, 7],
                            backgroundColor: [
                                '#36a2eb', // blue
                                '#ff6384', // red
                                '#ffcd56', // yellow
                                '#4bc0c0'  // teal
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false, // <<< CHANGED HERE
                        // aspectRatio: 2, // <<< REMOVED or commented out
                        cutout: '70%',
                        plugins: {
                            legend: {
                                position: 'right'
                            }
                        }
                    }
                });
            } else {
                console.warn('Energy Mix Chart container has no height or is not visible, skipping initialization.');
            }
        }

        // Initialize the System Breakdown Chart
        const systemBreakdownEl = document.getElementById('systemBreakdownChart');
        if (systemBreakdownEl) {
            const systemBreakdownCtx = systemBreakdownEl.getContext('2d');
            new Chart(systemBreakdownCtx, {
                type: 'pie',
                data: {
                    labels: ['HVAC', 'Lighting', 'Plug Loads', 'Other'],
                    datasets: [{
                        data: [42, 27, 18, 13],
                        backgroundColor: [
                            '#007bff', // primary
                            '#28a745', // success
                            '#17a2b8', // info
                            '#ffc107'  // warning
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Initialize Emissions Breakdown Chart
        const emissionsBreakdownEl = document.getElementById('emissionsBreakdownChart');
        if (emissionsBreakdownEl) {
            const emissionsBreakdownCtx = emissionsBreakdownEl.getContext('2d');
            new Chart(emissionsBreakdownCtx, {
                type: 'pie',
                data: {
                    labels: ['Scope 1 (Direct)', 'Scope 2 (Electricity)', 'Scope 3 (Indirect)'],
                    datasets: [{
                        data: [210, 680, 90],
                        backgroundColor: [
                            '#dc3545', // danger/red
                            '#ffc107', // warning/yellow
                            '#17a2b8'  // info/blue
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
    
    // Initialize all charts - this will only create charts if their elements exist
    initializeCharts();
    
    // Log anomalies for debugging
    if (anomalies && anomalies.length > 0) {
        console.log('Anomalies found:', anomalies);
    } else {
        console.log('No anomalies data available or invalid format');
    }
});