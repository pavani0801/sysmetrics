// Dashboard Client-side Charting
document.addEventListener('DOMContentLoaded', function() {
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Usage (%)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    // Initialize chart data storage
    const chartData = {
        labels: [],
        cpuData: [],
        memoryData: [],
        diskData: []
    };

    // Create Chart.js instances
    const cpuChart = new Chart(document.getElementById('cpuChart'), {
        ...chartConfig,
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'CPU Usage',
                data: chartData.cpuData,
                backgroundColor: '#6366f1',
                borderColor: '#6366f1',
                fill: false,
                pointRadius: 0
            }]
        }
    });

    const memoryChart = new Chart(document.getElementById('memoryChart'), {
        ...chartConfig,
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Memory Usage',
                data: chartData.memoryData,
                backgroundColor: '#10b981',
                borderColor: '#10b981',
                fill: false,
                pointRadius: 0
            }]
        }
    });

    const diskChart = new Chart(document.getElementById('diskChart'), {
        ...chartConfig,
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Disk Usage',
                data: chartData.diskData,
                backgroundColor: '#f59e0b',
                borderColor: '#f59e0b',
                fill: false,
                pointRadius: 0
            }]
        }
    });

    // Update charts periodically
    function updateCharts() {
        fetch('/metrics/')  //  another endpoint to get real-time metrics
            .then(response => response.json())
            .then(metrics => {
                const now = new Date();
                const timeLabel = now.toLocaleTimeString();

                // Update chart data
                chartData.labels.push(timeLabel);
                chartData.cpuData.push(metrics.cpu.overall_usage);
                chartData.memoryData.push(metrics.memory.percent_used);

                // Calculate average disk usage
                const averageDiskUsage = metrics.disk.partitions.reduce((sum, partition) => 
                    sum + partition.percent_used, 0) / metrics.disk.partitions.length;
                chartData.diskData.push(averageDiskUsage);

                // Limit chart data points
                if (chartData.labels.length > 20) {
                    chartData.labels.shift();
                    chartData.cpuData.shift();
                    chartData.memoryData.shift();
                    chartData.diskData.shift();
                }

                // Update charts
                cpuChart.update();
                memoryChart.update();
                diskChart.update();
            })
            .catch(error => console.error('Error fetching metrics:', error));
    }

    // Start periodic updates
    setInterval(updateCharts, 2000);
});