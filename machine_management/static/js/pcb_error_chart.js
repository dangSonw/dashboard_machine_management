document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('pcbErrorChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Data is passed from the template via Django's json_script
    const dataElement = document.getElementById('pcb-error-data');
    if (!dataElement) return;
    
    const pcbErrorStatsRaw = JSON.parse(dataElement.textContent);
    
    const labels = pcbErrorStatsRaw.map(stat => stat.label);
    const dataValues = pcbErrorStatsRaw.map(stat => stat.count);
    const percentages = pcbErrorStatsRaw.map(stat => stat.percentage);

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 1)');   // blue-500
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.2)'); // blue-600 with opacity

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Error Rate (%)',
                data: percentages,
                backgroundColor: gradient,
                borderColor: '#3b82f6',
                borderWidth: 2,
                borderRadius: 8,
                barThickness: 'flex',
                maxBarThickness: 50
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
                    titleColor: '#1e293b',
                    bodyColor: '#1e293b',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const count = dataValues[index];
                            const pct = percentages[index];
                            return `Rate: ${pct}% (${count} errors)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false,
                        display: true,
                        drawOnChartArea: true,
                        drawTicks: false,
                        borderDash: [5, 5],
                        color: 'rgba(203, 213, 225, 0.2)'
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#64748b',
                        font: {
                            size: 11,
                            family: "Open Sans",
                            style: 'normal',
                            lineHeight: 2
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        drawBorder: false,
                        display: false,
                        drawOnChartArea: false,
                        drawTicks: false
                    },
                    ticks: {
                        display: true,
                        color: '#64748b',
                        padding: 10,
                        font: {
                            size: 11,
                            family: "Open Sans",
                            style: 'normal',
                            lineHeight: 2
                        },
                    }
                }
            }
        }
    });
});
