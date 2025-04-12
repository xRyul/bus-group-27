document.addEventListener('DOMContentLoaded', function() {
    // console.log('Energy Monitoring Dashboard Loaded');
    
    // Setup UI animations
    setupAnimations();
    
    // Get data from data attributes
    const chartDataElement = document.getElementById('chartData');
    let electricData = [];
    let gasData = [];
    let waterData = [];
    let anomaliesByType = {};
    
    try {
        electricData = JSON.parse(chartDataElement.dataset.electric || '[]');
        gasData = JSON.parse(chartDataElement.dataset.gas || '[]');
        waterData = JSON.parse(chartDataElement.dataset.water || '[]');
        anomaliesByType = JSON.parse(chartDataElement.dataset.anomalies || '{}'); 
    } catch (e) {
        console.error('Error parsing chart data:', e);
    }
    
    // Setup event listeners for dashboard controls
    setupDashboardControls();
    
    // Initialize charts only if their elements exist
    function initializeCharts() {
        // Main Chart - Energy Consumption Over Time
        const mainChartEl = document.getElementById('mainChart');
        if (mainChartEl) {
            // Helper function to prepare anomaly data for a specific type
            const prepareAnomalyData = (type) => {
                const data = Array(24).fill(null);
                if (anomaliesByType && anomaliesByType[type] && anomaliesByType[type].length > 0) {
                    anomaliesByType[type].forEach(anomaly => {
                        if (anomaly && typeof anomaly.index === 'number') {
                            // Plot anomaly point using its actual value from the backend
                            data[anomaly.index] = anomaly.value; 
                        }
                    });
                }
                return data;
            };

            const electricAnomalyData = prepareAnomalyData('electric');
            const gasAnomalyData = prepareAnomalyData('gas');
            const waterAnomalyData = prepareAnomalyData('water');
            
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
                            data: electricData,
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
                            label: 'Gas (m3)',
                            data: gasData,
                            borderColor: '#FFB300',
                            backgroundColor: 'rgba(255, 179, 0, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            fill: true,
                            pointBackgroundColor: '#FFB300',
                            pointRadius: 3,
                            pointHoverRadius: 5,
                            hidden: true
                        },
                        {
                            label: 'Water (litres)',
                            data: waterData, 
                            borderColor: '#00ACC1',
                            backgroundColor: 'rgba(0, 172, 193, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            fill: true,
                            pointBackgroundColor: '#00ACC1',
                            pointRadius: 3,
                            pointHoverRadius: 5,
                            hidden: true // Gas starts hidden
                        },
                        {
                            label: 'Electric Anomalies',
                            data: electricAnomalyData,
                            borderColor: 'transparent',
                            backgroundColor: 'transparent',
                            pointBackgroundColor: 'red',
                            pointBorderColor: 'red',
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            showLine: false,
                            pointStyle: 'triangle',
                            hidden: false
                        },
                        {
                            label: 'Gas Anomalies',
                            data: gasAnomalyData,
                            borderColor: 'transparent',
                            backgroundColor: 'transparent',
                            pointBackgroundColor: 'red',
                            pointBorderColor: 'red',
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            showLine: false,
                            pointStyle: 'triangle',
                            hidden: true
                        },
                        {
                            label: 'Water Anomalies',
                            data: waterAnomalyData,
                            borderColor: 'transparent',
                            backgroundColor: 'transparent',
                            pointBackgroundColor: 'red',
                            pointBorderColor: 'red',
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            showLine: false,
                            pointStyle: 'triangle',
                            hidden: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            titleColor: '#333',
                            bodyColor: '#333',
                            borderColor: '#ddd',
                            borderWidth: 1,
                            padding: 10,
                            boxPadding: 5,
                            usePointStyle: true,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.y !== null) {
                                        label += context.parsed.y.toFixed(1);
                                    }
                                    return label;
                                }
                            }
                        },
                        legend: {
                            display: false
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
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time of Day'
                            },
                            grid: {
                                color: 'rgba(200, 200, 200, 0.2)'
                            }
                        }
                    }
                }
            });
            
            // Toggle between chart types (line/bar)
            const toggleChartBtn = document.getElementById('toggleChartView');
            if (toggleChartBtn) {
                toggleChartBtn.addEventListener('click', function() {
                    const currentType = mainChart.config.type;
                    const newType = currentType === 'line' ? 'bar' : 'line';
                    
                    mainChart.config.type = newType;
                    mainChart.update();
                    
                    // Update button text
                    this.innerHTML = newType === 'line' 
                        ? '<i class="bi bi-bar-chart"></i> View as Bar Chart'
                        : '<i class="bi bi-graph-up"></i> View as Line Chart';
                });
            }
            
            // Export chart as image
            const downloadReportBtn = document.getElementById('downloadReportBtn');
            if (downloadReportBtn) {
                downloadReportBtn.addEventListener('click', function() {
                    const link = document.createElement('a');
                    link.download = 'energy-consumption-report.png';
                    link.href = mainChart.toBase64Image();
                    link.click();
                });
            }
            
            // Connect energy type filters to chart visibility
            document.getElementById('electricity').addEventListener('change', function() {
                mainChart.data.datasets[0].hidden = !this.checked; // Electric line
                mainChart.data.datasets[3].hidden = !this.checked; // Electric anomalies
                mainChart.update();
            });
            
            document.getElementById('gas').addEventListener('change', function() {
                mainChart.data.datasets[1].hidden = !this.checked; // Gas line
                mainChart.data.datasets[4].hidden = !this.checked; // Gas anomalies
                mainChart.update();
            });
            
            document.getElementById('water').addEventListener('change', function() {
                mainChart.data.datasets[2].hidden = !this.checked; // Water line
                mainChart.data.datasets[5].hidden = !this.checked; // Water anomalies
                mainChart.update();
            });
        }
        
        // Initialize the Energy Mix Donut Chart
        const energyMixEl = document.getElementById('energyMixChart');
        if (energyMixEl) {
            // Get the container, not just the canvas, to ensure context
            const energyMixContainer = energyMixEl.parentElement; 
            if (energyMixContainer && energyMixContainer.offsetHeight > 0) {
                const energyMixCtx = energyMixEl.getContext('2d');
                new Chart(energyMixCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Grid Electricity', 'Natural Gas', 'Solar PV', 'Other Renewables'],
                        datasets: [{
                            data: [58, 10, 25, 7],
                            backgroundColor: [
                                '#1976D2', // blue
                                '#F44336', // red
                                '#FFB300', // yellow
                                '#00BFA5'  // teal
                            ],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                titleColor: '#333',
                                bodyColor: '#333',
                                borderColor: '#ddd',
                                borderWidth: 1,
                                padding: 10,
                                boxPadding: 5,
                                usePointStyle: true,
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((acc, data) => acc + data, 0);
                                        const percentage = ((value / total) * 100).toFixed(1) + '%';
                                        return `${label}: ${percentage}`;
                                    }
                                }
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
                            '#1976D2', // primary
                            '#4CAF50', // success
                            '#00ACC1', // info
                            '#FFB300'  // warning
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            titleColor: '#333',
                            bodyColor: '#333',
                            borderColor: '#ddd',
                            borderWidth: 1,
                            padding: 10,
                            boxPadding: 5,
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((acc, data) => acc + data, 0);
                                    const percentage = ((value / total) * 100).toFixed(1) + '%';
                                    return `${label}: ${percentage}`;
                                }
                            }
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
                            '#F44336', // danger/red
                            '#FFB300', // warning/yellow
                            '#00ACC1'  // info/blue
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            titleColor: '#333',
                            bodyColor: '#333',
                            borderColor: '#ddd',
                            borderWidth: 1,
                            padding: 10,
                            boxPadding: 5,
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((acc, data) => acc + data, 0);
                                    const percentage = ((value / total) * 100).toFixed(1) + '%';
                                    return `${label}: ${value} kg CO₂e (${percentage})`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Setup dashboard controls and event listeners
    function setupDashboardControls() {
        const buildingSelector = document.getElementById('buildingSelector');
        if (buildingSelector) {
            buildingSelector.addEventListener('change', function() {
                const selectedBuildingId = this.value;
                if (selectedBuildingId) {
                    // Redirect to the same page with the selected building ID as a query parameter
                    window.location.href = `${window.location.pathname}?building_id=${selectedBuildingId}`;
                }
            });
        }
        
        // Time period radio buttons
        const timePeriodRadios = document.querySelectorAll('input[name="timePeriod"]');
        timePeriodRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                console.log('Time period changed to:', this.id);

                document.querySelectorAll('.stat-value').forEach(el => {
                    el.innerHTML = '<div class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Loading...</span></div>';
                });
                
                setTimeout(() => {
                    updateRandomStats();
                    updateEnvironmentalStats(); 
                }, 500);
            });
        });
        
        // Date range picker
        const dateRange = document.getElementById('dateRange');
        if (dateRange) {
            dateRange.addEventListener('change', function() {
                console.log('Date range changed to:', this.value);
            });
        }
        
        // Export report button
        const downloadReportBtn = document.getElementById('downloadReportBtn');
        if (downloadReportBtn) {
            downloadReportBtn.addEventListener('click', function() {
                console.log('Exporting full report...');
                alert('Generating comprehensive energy report PDF...');
            });
        }
        
        // Implement All button for recommendations
        const implementAllBtn = document.getElementById('implementAllBtn');
        if (implementAllBtn) {
            implementAllBtn.addEventListener('click', function() {
                alert('Scheduling implementation of all recommended actions');
            });
        }
        
        // Individual recommendation buttons
        const implementButtons = document.querySelectorAll('.recommendation-content .btn-outline-success');
        implementButtons.forEach(button => {
            button.addEventListener('click', function() {
                const recommendationTitle = this.closest('.recommendation-content').querySelector('h6').textContent;
                alert(`Scheduling implementation: ${recommendationTitle}`);
            });
        });
        
        const detailButtons = document.querySelectorAll('.recommendation-content .btn-outline-secondary');
        detailButtons.forEach(button => {
            button.addEventListener('click', function() {
                const recommendationTitle = this.closest('.recommendation-content').querySelector('h6').textContent;
                alert(`Showing detailed analysis for: ${recommendationTitle}`);
            });
        });
    }
    
    // Update main stats with random values
    function updateRandomStats() {
        // Total consumption
        const consumptionValue = Math.floor(Math.random() * 1000) + 1500;
        const consumptionChange = (Math.random() * 10 - 5).toFixed(1);
        document.querySelector('.stat-card.energy .stat-value').textContent = `${consumptionValue} kWh`;
        
        const consumptionChangeEl = document.querySelector('.stat-card.energy .stat-change');
        consumptionChangeEl.innerHTML = consumptionChange < 0 
            ? `<i class="bi bi-arrow-down"></i><span>${Math.abs(consumptionChange)}% from previous</span>`
            : `<i class="bi bi-arrow-up"></i><span>${consumptionChange}% from previous</span>`;
        
        consumptionChangeEl.className = consumptionChange < 0 
            ? 'stat-change positive' 
            : 'stat-change negative';
        
        // Cost
        const costValue = (consumptionValue * 0.15).toFixed(2);
        const costChange = (Math.random() * 10 - 5).toFixed(1);
        document.querySelector('.stat-card.cost .stat-value').textContent = `$${costValue}`;
        
        const costChangeEl = document.querySelector('.stat-card.cost .stat-change');
        costChangeEl.innerHTML = costChange < 0 
            ? `<i class="bi bi-arrow-down"></i><span>${Math.abs(costChange)}% from previous</span>`
            : `<i class="bi bi-arrow-up"></i><span>${costChange}% from previous</span>`;
        
        costChangeEl.className = costChange < 0 
            ? 'stat-change positive' 
            : 'stat-change negative';
        
        // Carbon
        const carbonValue = Math.floor(consumptionValue * 0.4);
        const carbonChange = (Math.random() * 10 - 5).toFixed(1);
        document.querySelector('.stat-card.carbon .stat-value').textContent = `${carbonValue} kg CO₂`;
        
        const carbonChangeEl = document.querySelector('.stat-card.carbon .stat-change');
        carbonChangeEl.innerHTML = carbonChange < 0 
            ? `<i class="bi bi-arrow-down"></i><span>${Math.abs(carbonChange)}% from previous</span>`
            : `<i class="bi bi-arrow-up"></i><span>${carbonChange}% from previous</span>`;
        
        carbonChangeEl.className = carbonChange < 0 
            ? 'stat-change positive' 
            : 'stat-change negative';
        
        // Anomalies
        const anomalyCount = Math.floor(Math.random() * 5);
        const anomalyNew = Math.floor(Math.random() * 3);
        document.querySelector('.stat-card.alert .stat-value').textContent = anomalyCount;
        
        const anomalyChangeEl = document.querySelector('.stat-card.alert .stat-change');
        anomalyChangeEl.innerHTML = `<i class="bi bi-arrow-up"></i><span>${anomalyNew} new today</span>`;
        anomalyChangeEl.className = 'stat-change negative';
    }
    
    // Update environmental stats with random values
    function updateEnvironmentalStats() {
        // Energy Use Intensity
        const intensityValue = Math.floor(Math.random() * 50) + 100;
        const intensityChange = (Math.random() * 15 - 10).toFixed(1);
        document.querySelectorAll('.stat-card').forEach((card, index) => {
            if (index < 4) return; // Skip the first row of cards
            
            const statValue = card.querySelector('.stat-value');
            const statChange = card.querySelector('.stat-change');
            
            if (index === 4) { // Energy Use Intensity
                statValue.textContent = `${intensityValue} kWh/m²/yr`;
                statChange.innerHTML = intensityChange < 0 
                    ? `<i class="bi bi-arrow-down"></i><span>${Math.abs(intensityChange)}% below target</span>`
                    : `<i class="bi bi-arrow-up"></i><span>${intensityChange}% above target</span>`;
                statChange.className = intensityChange < 0 
                    ? 'stat-change positive' 
                    : 'stat-change negative';
            } else if (index === 5) { // Renewable Energy
                const renewableValue = Math.floor(Math.random() * 20) + 20;
                const renewableTarget = 50;
                const renewableGap = renewableTarget - renewableValue;
                statValue.textContent = `${renewableValue}%`;
                statChange.innerHTML = renewableGap > 0 
                    ? `<i class="bi bi-arrow-up"></i><span>${renewableGap}% to target (${renewableTarget}%)</span>`
                    : `<i class="bi bi-check-circle"></i><span>Target achieved</span>`;
                statChange.className = renewableGap > 0 
                    ? 'stat-change negative' 
                    : 'stat-change positive';
            } else if (index === 6) { // Water Intensity
                const waterValue = Math.floor(Math.random() * 20) + 35;
                const waterChange = (Math.random() * 20 - 15).toFixed(1);
                statValue.textContent = `${waterValue} L/m²/yr`;
                statChange.innerHTML = waterChange < 0 
                    ? `<i class="bi bi-arrow-down"></i><span>${Math.abs(waterChange)}% below baseline</span>`
                    : `<i class="bi bi-arrow-up"></i><span>${waterChange}% above baseline</span>`;
                statChange.className = waterChange < 0 
                    ? 'stat-change positive' 
                    : 'stat-change negative';
            } else if (index === 7) { // BREEAM Rating - static as it doesn't change with time periods
                statValue.textContent = "Excellent";
                statChange.innerHTML = `<i class="bi bi-check-circle"></i><span>Achieved 2010</span>`;
                statChange.className = 'stat-change positive';
            }
        });
    }
    
    // Animations
    function setupAnimations() {
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    animateOnScroll.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.animate-fade-in').forEach(element => {
            animateOnScroll.observe(element);
        });
    }

    initializeCharts();
    
    // // Log anomalies for debugging
    // if (anomalies && anomalies.length > 0) {
    //     console.log('Anomalies found:', anomalies);
    // } else {
    //     console.log('No anomalies data available or invalid format');
    // }
});
