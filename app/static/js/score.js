const canvas = document.getElementById('gaugeChart');
const ctx = canvas.getContext('2d');

// Green Score Gauge (Your existing code)
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
