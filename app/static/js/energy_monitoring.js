document.addEventListener('DOMContentLoaded', function() {
    // Get chart data
    const chartData = getChartData();
    
    // Initialize components
    setupAnimations();
    setupDashboardControls();
    initializeCharts(chartData);
});

// Get data from data attributes
function getChartData() {
    const chartDataElement = document.getElementById('chartData');
    const data = {
        electricData: [],
        gasData: [],
        waterData: [],
        anomaliesByType: {}
    };
    
    try {
        data.electricData = JSON.parse(chartDataElement.dataset.electric || '[]');
        data.gasData = JSON.parse(chartDataElement.dataset.gas || '[]');
        data.waterData = JSON.parse(chartDataElement.dataset.water || '[]');
        data.anomaliesByType = JSON.parse(chartDataElement.dataset.anomalies || '{}'); 
    } catch (e) {
        console.error('Error parsing chart data:', e);
    }
    
    return data;
}

// Initialize all charts
function initializeCharts(chartData) {
    initMainChart(chartData);
    initEnergyMixChart();
    initSystemBreakdownChart();
    initEmissionsBreakdownChart();
}

// Initialize main energy consumption chart
function initMainChart(chartData) {
    const mainChartEl = document.getElementById('mainChart');
    if (!mainChartEl) return;
    
    const anomalyData = {
        electric: prepareAnomalyData('electric', chartData.anomaliesByType),
        gas: prepareAnomalyData('gas', chartData.anomaliesByType),
        water: prepareAnomalyData('water', chartData.anomaliesByType)
    };
    
    const mainChartCtx = mainChartEl.getContext('2d');
    const mainChart = new Chart(mainChartCtx, {
        type: 'line',
        data: {
            labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', 
                    '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', 
                    '20:00', '21:00', '22:00', '23:00'],
            datasets: [
                createDataset('Electricity (kWh)', chartData.electricData, '#4CAF50', false),
                createDataset('Gas (m3)', chartData.gasData, '#FFB300', true),
                createDataset('Water (litres)', chartData.waterData, '#00ACC1', true),
                createAnomalyDataset('Electric Anomalies', anomalyData.electric, false),
                createAnomalyDataset('Gas Anomalies', anomalyData.gas, true),
                createAnomalyDataset('Water Anomalies', anomalyData.water, true)
            ]
        },
        options: getMainChartOptions()
    });
    
    // Add event listeners for chart controls
    setupChartControls(mainChart);
}

// Prepare anomaly data
function prepareAnomalyData(type, anomaliesByType) {
    const data = Array(24).fill(null);
    if (anomaliesByType && anomaliesByType[type] && anomaliesByType[type].length > 0) {
        anomaliesByType[type].forEach(anomaly => {
            if (anomaly && typeof anomaly.index === 'number') {
                data[anomaly.index] = anomaly.value;
            }
        });
    }
    return data;
}

// Create a standard dataset
function createDataset(label, data, color, hidden) {
    return {
        label: label,
        data: data,
        borderColor: color,
        backgroundColor: color + '1A', // 1A = HEX for 10% opacity as we want alpha
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        pointBackgroundColor: color,
        pointRadius: 3,
        pointHoverRadius: 5,
        hidden: hidden
    };
}

// Create an anomaly dataset
function createAnomalyDataset(label, data, hidden) {
    return {
        label: label,
        data: data,
        borderColor: 'transparent',
        backgroundColor: 'transparent',
        pointBackgroundColor: 'red',
        pointBorderColor: 'red',
        pointRadius: 6,
        pointHoverRadius: 8,
        showLine: false,
        pointStyle: 'triangle',
        hidden: hidden
    };
}

// Main chart options
function getMainChartOptions() {
    return {
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
    };
}

// Setup controls for main chart
function setupChartControls(mainChart) {
    // Toggle chart type (line/bar)
    const toggleChartBtn = document.getElementById('toggleChartView');
    if (toggleChartBtn) {
        toggleChartBtn.addEventListener('click', function() {
            const currentType = mainChart.config.type;
            const newType = currentType === 'line' ? 'bar' : 'line';
            
            mainChart.config.type = newType;
            mainChart.update();
            
            this.innerHTML = newType === 'line' 
                ? '<i class="bi bi-bar-chart"></i> View as Bar Chart'
                : '<i class="bi bi-graph-up"></i> View as Line Chart';
        });
    }
    
    // Energy type toggles
    setupEnergyTypeToggle('electricity', 0, 3, mainChart);
    setupEnergyTypeToggle('gas', 1, 4, mainChart);
    setupEnergyTypeToggle('water', 2, 5, mainChart);
}

// Set up energy type toggle
function setupEnergyTypeToggle(id, dataIndex, anomalyIndex, chart) {
    const toggle = document.getElementById(id);
    if (toggle) {
        toggle.addEventListener('change', function() {
            chart.data.datasets[dataIndex].hidden = !this.checked;
            chart.data.datasets[anomalyIndex].hidden = !this.checked;
            chart.update();
        });
    }
}

// Initialize Energy Mix Chart
function initEnergyMixChart() {
    const energyMixEl = document.getElementById('energyMixChart');
    if (!energyMixEl) return;
    
    const energyMixContainer = energyMixEl.parentElement;
    if (!energyMixContainer || energyMixContainer.offsetHeight <= 0) {
        console.warn('Energy Mix Chart container has no height or is not visible, skipping initialization.');
        return;
    }
    
    const energyMixCtx = energyMixEl.getContext('2d');
    new Chart(energyMixCtx, {
        type: 'doughnut',
        data: {
            labels: ['Grid Electricity', 'Natural Gas', 'Solar PV', 'Other Renewables'],
            datasets: [{
                data: [58, 10, 25, 7],
                backgroundColor: ['#1976D2', '#F44336', '#FFB300', '#00BFA5'],
                borderWidth: 0
            }]
        },
        options: getPieChartOptions(true)
    });
}

// Initialize System Breakdown Chart
function initSystemBreakdownChart() {
    const chartEl = document.getElementById('systemBreakdownChart');
    if (!chartEl) return;
    
    const ctx = chartEl.getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['HVAC', 'Lighting', 'Plug Loads', 'Other'],
            datasets: [{
                data: [42, 27, 18, 13],
                backgroundColor: ['#1976D2', '#4CAF50', '#00ACC1', '#FFB300'],
                borderWidth: 0
            }]
        },
        options: getPieChartOptions()
    });
}

// Initialize Emissions Breakdown Chart
function initEmissionsBreakdownChart() {
    const chartEl = document.getElementById('emissionsBreakdownChart');
    if (!chartEl) return;
    
    const ctx = chartEl.getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Scope 1 (Direct)', 'Scope 2 (Electricity)', 'Scope 3 (Indirect)'],
            datasets: [{
                data: [210, 680, 90],
                backgroundColor: ['#F44336', '#FFB300', '#00ACC1'],
                borderWidth: 0
            }]
        },
        options: getPieChartOptions(false, true)
    });
}

// Pie/doughnut chart options
function getPieChartOptions(isDoughnut = false, isEmissions = false) {
    const options = {
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
                usePointStyle: true,
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((acc, data) => acc + data, 0);
                        const percentage = ((value / total) * 100).toFixed(1) + '%';
                        
                        if (isEmissions) {
                            return `${label}: ${value} kg CO₂e (${percentage})`;
                        }
                        return `${label}: ${percentage}`;
                    }
                }
            }
        }
    };
    
    if (isDoughnut) {
        options.cutout = '70%';
    }
    
    return options;
}

// Setup dashboard controls and event listeners
function setupDashboardControls() {
    setupBuildingSelector();
    setupTimePeriodControls();
    setupDropdownClosers();
    setupEnergyTypeDropdown();
    setupSettingsDropdown();
    setupExportFunctionality();
}

// Building selector
function setupBuildingSelector() {
    const buildingSelector = document.getElementById('buildingSelector');
    if (buildingSelector) {
        buildingSelector.addEventListener('change', function() {
            if (this.value) {
                window.location.href = `${window.location.pathname}?building_id=${this.value}`;
            }
        });
    }
}

// Time period controls
function setupTimePeriodControls() {
    const timePeriodButton = document.getElementById('timePeriodButton');
    const timePeriodFilters = document.querySelector('.time-period-filters');
    const timePeriodOptions = document.querySelectorAll('.time-period-option');
    const customDateOption = document.getElementById('customDateOption');
    const customDateModal = document.getElementById('customDateModal') ? 
        new bootstrap.Modal(document.getElementById('customDateModal')) : null;
    
    // Date fields for custom range
    const startDateField = document.getElementById('startDate');
    const endDateField = document.getElementById('endDate');
    const applyCustomDateBtn = document.getElementById('applyCustomDate');
    
    // Set default dates
    if (startDateField && endDateField) {
        const today = new Date();
        const nextWeek = new Date();
        nextWeek.setDate(today.getDate() + 7);
        
        startDateField.valueAsDate = today;
        endDateField.valueAsDate = nextWeek;
    }
    
    // Radio inputs
    const radioInputs = {
        day: document.getElementById('day'),
        week: document.getElementById('week'),
        month: document.getElementById('month'),
        year: document.getElementById('year'),
        custom: document.getElementById('custom')
    };
    
    // Initialize button based on current time period
    initializeTimePeriodButton(timePeriodButton, timePeriodOptions, customDateOption, radioInputs, startDateField, endDateField);
    
    // Toggle time period dropdown
    if (timePeriodButton && timePeriodFilters) {
        timePeriodButton.addEventListener('click', function(e) {
            e.preventDefault();
            timePeriodFilters.classList.toggle('active');
            // Close energy type dropdown if open
            const energyTypeFilters = document.querySelector('.energy-type-filters');
            if (energyTypeFilters) energyTypeFilters.classList.remove('active');
        });
    }
    
    // Handle time period selection
    if (timePeriodOptions) {
        timePeriodOptions.forEach(option => {
            option.addEventListener('click', function() {
                const value = this.dataset.value;
                
                // Handle custom date selection
                if (value === 'custom' && customDateModal) {
                    timePeriodFilters.classList.remove('active');
                    customDateModal.show();
                    return;
                }
                
                updateTimePeriodUI(this, timePeriodButton, timePeriodOptions, radioInputs, value);
                redirectWithTimePeriod(value);
            });
        });
    }
    
    // Apply custom date range
    if (applyCustomDateBtn) {
        applyCustomDateBtn.addEventListener('click', function() {
            applyCustomDateRange(timePeriodButton, timePeriodOptions, customDateOption, radioInputs, startDateField, endDateField, customDateModal);
        });
    }
}

// Helper functions for time period controls
function getCurrentTimePeriod() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('time_period') || 'day';
}

function getCustomDates() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        startDate: urlParams.get('start_date'),
        endDate: urlParams.get('end_date')
    };
}

function initializeTimePeriodButton(button, options, customOption, radioInputs, startDateField, endDateField) {
    if (!button) return;
    
    const currentPeriod = getCurrentTimePeriod();
    
    // Handle custom period
    if (currentPeriod === 'custom') {
        const { startDate, endDate } = getCustomDates();
        
        if (startDate && endDate) {
            // Set date fields
            if (startDateField) startDateField.value = startDate;
            if (endDateField) endDateField.value = endDate;
            
            // Format for display
            const startFormatted = new Date(startDate).toLocaleDateString('en-UK', { month: 'short', day: 'numeric' });
            const endFormatted = new Date(endDate).toLocaleDateString('en-UK', { month: 'short', day: 'numeric' });
            
            // Update UI
            button.innerHTML = `
                <i class="bi bi-calendar-range"></i>
                <span class="time-label">${startFormatted} - ${endFormatted}</span>
                <i class="bi bi-chevron-down ms-1"></i>`;
            
            options.forEach(opt => opt.classList.remove('active'));
            if (customOption) customOption.classList.add('active');
            
            if (radioInputs.custom) {
                radioInputs.custom.checked = true;
            }
            
            return;
        }
    }
    
    // For standard periods
    const periodOption = document.querySelector(`.time-period-option[data-value="${currentPeriod}"]`);
    
    if (periodOption) {
        // Update UI
        options.forEach(opt => opt.classList.remove('active'));
        periodOption.classList.add('active');
        
        button.innerHTML = `
            <i class="bi ${periodOption.dataset.icon}"></i>
            <span class="time-label">${periodOption.dataset.label}</span>
            <i class="bi bi-chevron-down ms-1"></i>`;
        
        if (radioInputs[currentPeriod]) {
            radioInputs[currentPeriod].checked = true;
        }
    }
}

function updateTimePeriodUI(selectedOption, button, allOptions, radioInputs, value) {
    // Update button content
    button.innerHTML = `
        <i class="bi ${selectedOption.dataset.icon}"></i>
        <span class="time-label">${selectedOption.dataset.label}</span>
        <i class="bi bi-chevron-down ms-1"></i>`;
    
    // Update active class
    allOptions.forEach(opt => opt.classList.remove('active'));
    selectedOption.classList.add('active');
    
    // Update radio input
    if (radioInputs[value]) {
        radioInputs[value].checked = true;
        radioInputs[value].dispatchEvent(new Event('change'));
    }
    
    // Close dropdown
    const dropdown = document.querySelector('.time-period-filters');
    if (dropdown) dropdown.classList.remove('active');
}

function redirectWithTimePeriod(value, startDate, endDate) {
    let currentUrl = new URL(window.location.href);
    let searchParams = currentUrl.searchParams;
    
    searchParams.set('time_period', value);
    
    if (value === 'custom' && startDate && endDate) {
        searchParams.set('start_date', startDate);
        searchParams.set('end_date', endDate);
    } else {
        searchParams.delete('start_date');
        searchParams.delete('end_date');
    }
    
    window.location.href = currentUrl.toString();
}

function applyCustomDateRange(button, options, customOption, radioInputs, startDateField, endDateField, modal) {
    // Validate
    const startDate = startDateField.value;
    const endDate = endDateField.value;
    
    if (!startDate || !endDate) {
        alert('Please select both start and end dates.');
        return;
    }
    
    // Format for display
    const startFormatted = new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const endFormatted = new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    
    // Update button
    button.innerHTML = `
        <i class="bi bi-calendar-range"></i>
        <span class="time-label">${startFormatted} - ${endFormatted}</span>
        <i class="bi bi-chevron-down ms-1"></i>`;
    
    // Update selection
    options.forEach(opt => opt.classList.remove('active'));
    if (customOption) customOption.classList.add('active');
    if (radioInputs.custom) {
        radioInputs.custom.checked = true;
        radioInputs.custom.dispatchEvent(new Event('change'));
    }

    if (modal) modal.hide();
    redirectWithTimePeriod('custom', startDate, endDate);
}

// Close dropdowns when clicking outside
function setupDropdownClosers() {
    document.addEventListener('click', function(e) {
        // Time period dropdown
        const timePeriodFilters = document.querySelector('.time-period-filters');
        const timePeriodButton = document.getElementById('timePeriodButton');
        if (timePeriodFilters && timePeriodButton && 
            !timePeriodFilters.contains(e.target) && 
            !timePeriodButton.contains(e.target)) {
            timePeriodFilters.classList.remove('active');
        }
        
        // Energy type dropdown
        const energyTypeFilters = document.querySelector('.energy-type-filters');
        const energyTypeToggle = document.getElementById('energyTypeToggle');
        if (energyTypeFilters && energyTypeToggle && 
            !energyTypeFilters.contains(e.target) && 
            !energyTypeToggle.contains(e.target)) {
            energyTypeFilters.classList.remove('active');
        }
        
        // Settings dropdown
        const settingsDropdown = document.querySelector('.settings-dropdown');
        const settingsButton = document.getElementById('settingsButton');
        if (settingsDropdown && settingsButton && 
            !settingsDropdown.contains(e.target) && 
            !settingsButton.contains(e.target)) {
            settingsDropdown.classList.remove('active');
        }
    });
}

// Energy type dropdown
function setupEnergyTypeDropdown() {
    const energyTypeToggle = document.getElementById('energyTypeToggle');
    const energyTypeFilters = document.querySelector('.energy-type-filters');
    
    if (energyTypeToggle && energyTypeFilters) {
        energyTypeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            energyTypeFilters.classList.toggle('active');
            
            // Close other dropdowns
            const timePeriodFilters = document.querySelector('.time-period-filters');
            if (timePeriodFilters) timePeriodFilters.classList.remove('active');
            
            const settingsDropdown = document.querySelector('.settings-dropdown');
            if (settingsDropdown) settingsDropdown.classList.remove('active');
        });
    }
}

// Settings dropdown
function setupSettingsDropdown() {
    const settingsDropdown = document.querySelector('.settings-dropdown');
    const settingsButton = document.getElementById('settingsButton');
    
    if (settingsButton && settingsDropdown) {
        settingsButton.addEventListener('click', function(e) {
            e.stopPropagation();
            settingsDropdown.classList.toggle('active');
            
            // Close other dropdowns
            const timePeriodFilters = document.querySelector('.time-period-filters');
            if (timePeriodFilters) timePeriodFilters.classList.remove('active');
            
            const energyTypeFilters = document.querySelector('.energy-type-filters');
            if (energyTypeFilters) energyTypeFilters.classList.remove('active');
        });
        
        // Prevent closing when clicking inside dropdown menu
        const settingsDropdownMenu = settingsDropdown.querySelector('.settings-dropdown-menu');
        if (settingsDropdownMenu) {
            settingsDropdownMenu.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    }
}

// Export functionality
function setupExportFunctionality() {
    const exportSubmitBtn = document.getElementById('exportSubmitBtn');
    if (exportSubmitBtn) {
        exportSubmitBtn.addEventListener('click', handleExport);
    }
}

function handleExport() {
    const modal = document.getElementById('exportOptionsModal');
    const modalInstance = bootstrap.Modal.getInstance(modal);
    
    // Show loading state
    this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Exporting...';
    this.disabled = true;
    const exportOptions = getExportOptions();
    
    handleChartImageExport();
    
    makeExportRequest(exportOptions, this, modalInstance);
}

function getExportOptions() {
    return {
        building_id: document.getElementById('exportBuildingId').value,
        time_period: document.getElementById('exportTimePeriod').value,
        include_electric: document.getElementById('includeElectric').checked,
        include_gas: document.getElementById('includeGas').checked,
        include_water: document.getElementById('includeWater').checked,
        include_anomalies: document.getElementById('includeAnomalies').checked,
        include_summary: document.getElementById('includeSummary').checked,
        export_format: document.getElementById('exportFormat').value,
        start_date: getExportCustomDates().startDate,
        end_date: getExportCustomDates().endDate
    };
}

function getExportCustomDates() {
    const exportTimePeriod = document.getElementById('exportTimePeriod');
    const startDateEl = document.getElementById('exportStartDate');
    const endDateEl = document.getElementById('exportEndDate');
    
    if (exportTimePeriod && exportTimePeriod.value === 'custom' && startDateEl && endDateEl) {
        return {
            startDate: startDateEl.value,
            endDate: endDateEl.value
        };
    }
    
    return { startDate: null, endDate: null };
}

function handleChartImageExport() {
    const includeChartImage = document.getElementById('includeChartImage').checked;
    if (includeChartImage) {
        const mainChart = Chart.getChart('mainChart');
        if (mainChart) {
            const chartImageUrl = mainChart.toBase64Image();
            const link = document.createElement('a');
            const building_name = document.getElementById('buildingDropdown').textContent.trim().replace(/\s+/g, '_').toLowerCase();
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            link.download = `${building_name}_energy_chart_${timestamp}.png`;
            link.href = chartImageUrl;
            link.click();
        }
    }
}

function makeExportRequest(exportOptions, button, modal) {
    fetch('/export-building-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportOptions)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('text/csv')) {
            return handleCsvResponse(response);
        } else {
            return handleJsonResponse(response);
        }
    })
    .catch(error => {
        console.error('Error during export:', error);
        alert('An error occurred during export. Please try again.');
    })
    .finally(() => {
        // Reset button state
        button.innerHTML = '<i class="bi bi-download"></i> Export';
        button.disabled = false;
        
        // Close the modal
        if (modal) {
            modal.hide();
        }
    });
}

function handleCsvResponse(response) {
    return response.blob().then(blob => {
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'energy_data_export.csv';
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename=(.*)/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1].replace(/['"]/g, '');
            }
        }
        
        downloadFile(blob, filename);
    });
}

function handleJsonResponse(response) {
    return response.json().then(data => {
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        
        let building_name = "building";
        if (data.building && data.building.name) {
            building_name = data.building.name.replace(/\s+/g, '_').toLowerCase();
        }
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `${building_name}_energy_data_${timestamp}.json`;
        
        downloadFile(blob, filename);
    });
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
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
