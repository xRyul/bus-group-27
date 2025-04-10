const canvas = document.getElementById('gaugeChart');
const ctx = canvas.getContext('2d');

const scoreText = document.getElementById('greenScore').textContent;
const scoreMatch = scoreText.match(/\d+/);
const score = scoreMatch ? parseInt(scoreMatch[0], 10) : 0;
const percentage = Math.min(score / 1000, 1);

const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
gradient.addColorStop(0, '#dc3545');
gradient.addColorStop(0.33, '#ffc107');
gradient.addColorStop(0.66, '#28a745');
gradient.addColorStop(1, '#218838');

const gaugeChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    datasets: [{
      data: [percentage, 1 - percentage],
      backgroundColor: [gradient, '#e9ecef'],
      borderWidth: 0,
      cutout: '90%',
      circumference: 180,
      rotation: 270
    }]
  },
  options: {
    responsive: true,
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false }
    }
  }
});

function initializeWeeklyChart() {
    const weeklyChartEl = document.getElementById('weeklyChart');
    if (weeklyChartEl) {
        const weeklyData = [790, 815, 800, 860, 850];

        const weeklyChartCtx = weeklyChartEl.getContext('2d');
        const weeklyChart = new Chart(weeklyChartCtx, {
            type: 'line',
            data: {
                labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                datasets: [{
                    label: 'Green Score',
                    data: weeklyData,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#4CAF50',
                    pointRadius: 4,
                    pointHoverRadius: 6
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
                        usePointStyle: true,
                        callbacks: {
                            label: function(context) {
                                return `Green Score: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        Min: 750,
                        Max: 900,
                        title: {
                            display: false ,
                            text: 'Green Score'
                        },
                        grid: {
                            color: 'rgba(200, 200, 200, 0.2)'
                        }
                    },
                    x: {
                        title: {
                            display: false,
                            text: 'Weekdays'
                        },
                        grid: {
                            color: 'rgba(200, 200, 200, 0.2)'
                        }
                    }
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initializeWeeklyChart();
});
