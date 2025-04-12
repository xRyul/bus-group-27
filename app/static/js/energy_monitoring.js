document.addEventListener('DOMContentLoaded', function() {
    console.log('Energy Monitoring Dashboard Loaded');
    
    // Setup UI animations
    setupAnimations();
    
    // Get data from data attributes
    const chartDataElement = document.getElementById('chartData');
    let electricData = [];
    let gasData = [];
    let waterData = [];
    let anomalies = [];
    
    try {
        electricData = JSON.parse(chartDataElement.dataset.electric || '[]');
        gasData = JSON.parse(chartDataElement.dataset.gas || '[]');
        waterData = JSON.parse(chartDataElement.dataset.water || '[]');
        anomalies = JSON.parse(chartDataElement.dataset.anomalies || '[]');
    } catch (e) {
        console.error('Error parsing chart data:', e);
        // Fallback data in case of parsing error (less likely now but good practice)
        electricData = Array(24).fill(50 + Math.random() * 50); 
        gasData = Array(24).fill(30 + Math.random() * 30);
        waterData = Array(24).fill(10 + Math.random() * 10);
    }
    
    // Setup event listeners for dashboard controls
    setupDashboardControls();
    
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
            
            // Use the data fetched from the backend
            // const gasData = hourlyData.map(val => val * 0.6 + Math.random() * 10); // REMOVED SIMULATION
            // const waterData = hourlyData.map(val => val * 0.3 + Math.random() * 5); // REMOVED SIMULATION
            
            const mainChartCtx = mainChartEl.getContext('2d');
            const mainChart = new Chart(mainChartCtx, {
                type: 'line',
                data: {
                    labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', 
                             '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', 
                             '20:00', '21:00', '22:00', '23:00'],
                    datasets: [
                        {
                            label: 'Electricity (kWh)', // Assuming kWh, adjust if unit varies
                            data: electricData,       // Use electricData
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
                            label: 'Gas (m3)', // Assuming m3 based on simulation logic, adjust if unit varies
                            data: gasData,     // Use gasData
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
                            label: 'Water (litres)', // Assuming litres based on simulation logic, adjust if unit varies
                            data: waterData,     // Use waterData
                            borderColor: '#00ACC1',
                            backgroundColor: 'rgba(0, 172, 193, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            fill: true,
                            pointBackgroundColor: '#00ACC1',
                            pointRadius: 3,
                            pointHoverRadius: 5,
                            hidden: true
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
                            pointStyle: 'triangle'
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
            
            // Export chart as image - now connected to the main Export Report button
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
                mainChart.data.datasets[0].hidden = !this.checked;
                mainChart.update();
            });
            
            document.getElementById('gas').addEventListener('change', function() {
                mainChart.data.datasets[1].hidden = !this.checked;
                mainChart.update();
            });
            
            document.getElementById('water').addEventListener('change', function() {
                mainChart.data.datasets[2].hidden = !this.checked;
                mainChart.update();
            });
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
        // Building selector change event
        const buildingSelector = document.getElementById('buildingSelector');
        if (buildingSelector) {
            buildingSelector.addEventListener('change', function() {
                console.log('Building changed to:', this.value);
                // Here you would typically fetch new data for the selected building
                // and update the charts and stats
                
                // For demo purposes, just show a loading state
                document.querySelectorAll('.stat-value').forEach(el => {
                    el.innerHTML = '<div class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Loading...</span></div>';
                });
                
                // Simulate data loading
                setTimeout(() => {
                    updateRandomStats();
                }, 800);
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
                
                // Only show loading state for 500ms to avoid UI getting stuck
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
    
    // Function to update main stats with random values (for demo purposes)
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
    
    // Function to update environmental stats with random values
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
            } else if (index === 7) { // BREEAM Rating
                // Keep BREEAM rating static as it doesn't change with time periods
                statValue.textContent = "Excellent";
                statChange.innerHTML = `<i class="bi bi-check-circle"></i><span>Achieved 2010</span>`;
                statChange.className = 'stat-change positive';
            }
        });
    }
    
    
    // Setup animations
    function setupAnimations() {
        // Trigger animations when elements come into view
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    animateOnScroll.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // Apply to all animate-fade-in elements
        document.querySelectorAll('.animate-fade-in').forEach(element => {
            animateOnScroll.observe(element);
        });
    }

    initializeCharts();
    
    // Create heatmap chart for daily usage pattern
    createHeatMapChart();
    
    // Create heatmap chart for daily usage pattern
    function createHeatMapChart() {
        const heatMapCanvas = document.getElementById('heatMapChart');
        if (!heatMapCanvas) return;
        
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const hours = ['12am', '2am', '4am', '6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'];
        const data = [];
        
        // Pattern: Higher usage during working hours on weekdays, lower on weekends
        for (let day = 0; day < 7; day++) {
            for (let hour = 0; hour < 24; hour++) {
                // Calculate intensity based on patterns
                let value = 0;
                
                // Weekday pattern (Mon-Fri)
                if (day < 5) {
                    // Morning ramp-up (7-10 AM)
                    if (hour >= 7 && hour < 10) {
                        value = 30 + (hour - 7) * 20;
                    }
                    // Working hours (10 AM - 4 PM)
                    else if (hour >= 10 && hour < 16) {
                        value = 80 + Math.random() * 20;
                    }
                    // Evening ramp-down (4-7 PM)
                    else if (hour >= 16 && hour < 19) {
                        value = 70 - (hour - 16) * 20;
                    }
                    // Night (minimal usage)
                    else {
                        value = 5 + Math.random() * 10;
                    }
                } 
                // Weekend pattern (Sat-Sun)
                else {
                    // Daytime (10 AM - 6 PM)
                    if (hour >= 10 && hour < 18) {
                        value = 20 + Math.random() * 30;
                    }
                    // Night (minimal usage)
                    else {
                        value = 5 + Math.random() * 5;
                    }
                }
                
                // Add some randomness
                value = Math.min(100, Math.max(0, value + (Math.random() * 10 - 5)));
                
                // Add data point
                data.push({
                    x: hour,
                    y: day,
                    v: Math.round(value)
                });
            }
        }
        
        // Create the heatmap chart
        new Chart(heatMapCanvas, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Energy Usage',
                    data: data,
                    backgroundColor: function(context) {
                        const value = context.raw.v;
                        const alpha = Math.min(1, 0.1 + (value / 100) * 0.9);
                        return `rgba(76, 175, 80, ${alpha})`;
                    },
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    borderWidth: 1,
                    borderColor: 'rgba(0, 0, 0, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: -0.5,
                        max: 23.5,
                        ticks: {
                            stepSize: 2,
                            callback: function(value) {
                                if (value % 2 === 0 && value >= 0 && value < 24) {
                                    return hours[value / 2];
                                }
                                return '';
                            }
                        },
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    },
                    y: {
                        type: 'linear',
                        min: -0.5,
                        max: 6.5,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                if (value >= 0 && value < 7) {
                                    return days[value];
                                }
                                return '';
                            }
                        },
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Day of Week'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const data = context.raw;
                                const day = days[data.y];
                                const hour = data.x;
                                const value = data.v;
                                return `${day} at ${hour}:00 - Energy usage: ${value}%`;
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Log anomalies for debugging
    if (anomalies && anomalies.length > 0) {
        console.log('Anomalies found:', anomalies);
    } else {
        console.log('No anomalies data available or invalid format');
    }
});
