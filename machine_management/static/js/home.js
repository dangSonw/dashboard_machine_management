document.addEventListener("DOMContentLoaded", function() {
    "use strict";

    // Draw Monthly Chart (Area Spline style)
    fetch('/api/stats/monthly/')
        .then(response => response.json())
        .then(res => {
            var monthlyCtx = document.getElementById('monthlyChart').getContext('2d');

            new Chart(monthlyCtx, {
                type: 'line',
                data: {
                    labels: res.labels,
                    datasets: [
                        {
                            label: "Total",
                            backgroundColor: 'rgba(99, 102, 241, 0.3)',
                            borderColor: '#6366f1',
                            pointBackgroundColor: '#6366f1',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_total,
                            pointRadius: 3,
                        },
                        {
                            label: "OK",
                            backgroundColor: 'rgba(34, 197, 94, 0.3)',
                            borderColor: '#22c55e',
                            pointBackgroundColor: '#22c55e',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_pass,
                            pointRadius: 3,
                        },
                        {
                            label: "NG",
                            backgroundColor: 'rgba(249, 115, 22, 0.3)',
                            borderColor: '#f97316',
                            pointBackgroundColor: '#f97316',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_fail,
                            pointRadius: 3,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        easing: 'easeInOutQuad',
                        duration: 520
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold",
                            },
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.08)',
                                lineWidth: 1
                            }
                        }],
                        xAxes: [{
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.05)',
                                lineWidth: 1
                            },
                            ticks: {
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold"
                            }
                        }]
                    },
                    tooltips: {
                        titleFontFamily: 'Open Sans',
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleFontColor: '#fff',
                        caretSize: 5,
                        cornerRadius: 4,
                        xPadding: 10,
                        yPadding: 10
                    }
                }
            });
        })
        .catch(err => console.error("Error fetching monthly stats:", err));

    // Real-time loop to poll PLC for Cycle time or other real-time stats
    setInterval(async function() {
        try {
            const res = await fetch('/api/plc/status/');
            const data = await res.json();
            if (data.status === 'ok') {
                const el = document.getElementById('stat_cycle_time');
                if (el) el.textContent = (data.d100 || 0) + ' ms';
            }
        } catch (err) {
            console.error("Error polling PLC status:", err);
        }
    }, 2000);
});