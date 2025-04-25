document.addEventListener('DOMContentLoaded', function() {
    const lineChartConfig = {
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
        ...lineChartConfig,
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
        ...lineChartConfig,
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
    
    // Create container for disk chart to control size
    const diskChartElement = document.getElementById('diskChart');
    const diskChartContainer = document.createElement('div');
    diskChartContainer.id = 'diskChart-container';
    diskChartElement.parentNode.insertBefore(diskChartContainer, diskChartElement);
    diskChartContainer.appendChild(diskChartElement);
    
    
    const diskChart = new Chart(document.getElementById('diskChart'), {
        type: 'pie',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [0, 100], // Initial data (will be updated)
                backgroundColor: ['#f59e0b', '#e5e7eb'],
                borderColor: ['#f59e0b', '#e5e7eb'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, 
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 10 
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Create refresh mask
    const dashboardContainer =  document.body;
    const refreshMask = document.createElement('div');
    refreshMask.className = 'refresh-mask';
    refreshMask.innerHTML = `
        <div class="refresh-content">
            <div class="refresh-spinner"></div>
            <div class="refresh-text">Refreshing data...</div>
        </div>
    `;
    dashboardContainer.appendChild(refreshMask);
    
    // Add CSS for the refresh mask and charts
    const style = document.createElement('style');
    style.textContent = `
        .refresh-mask {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease-in-out;
        }
        .refresh-mask.active {
            opacity: 1;
            pointer-events: all;
        }
        .refresh-content {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .refresh-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        .refresh-text {
            font-size: 14px;
            color: #4b5563;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Disk chart size control */
        #diskChart {
            max-width: 200px;
            max-height: 200px;
            margin: 0 auto; /* Center the chart */
        }
        #diskChart-container {
            position: relative;
            height: 200px;
            width: 100%;
        }
    `;
    document.head.appendChild(style);
    
    // Function to show/hide refresh mask
    function toggleRefreshMask(show) {
        if (show) {
            refreshMask.classList.add('active');
        } else {
            refreshMask.classList.remove('active');
        }
    }
    
    // Function to format the timestamp for display
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
    
    // Function to initialize charts with historical data
    function initializeCharts() {
        toggleRefreshMask(true);
        
        fetch('http://127.0.0.1:7000/historical/api/metrics/')
            .then(response => response.json())
            .then(data => {
                // Sort data by timestamp (oldest first)
                data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                
                // Process historical data
                data.forEach(metric => {
                    const timeLabel = formatTimestamp(metric.timestamp);
                    
                    chartData.labels.push(timeLabel);
                    chartData.cpuData.push(Math.min(metric.cpu_usage, 100)); // Cap at 100% for display
                    chartData.memoryData.push(metric.memory_percent);
                    chartData.diskData.push(metric.disk_percent);
                });
                
                // Limit chart data points
                if (chartData.labels.length > 20) {
                    const overflow = chartData.labels.length - 20;
                    chartData.labels = chartData.labels.slice(overflow);
                    chartData.cpuData = chartData.cpuData.slice(overflow);
                    chartData.memoryData = chartData.memoryData.slice(overflow);
                    chartData.diskData = chartData.diskData.slice(overflow);
                }
                
                // Update line charts
                cpuChart.update();
                memoryChart.update();
                
                // Update pie chart with latest disk usage
                if (chartData.diskData.length > 0) {
                    const latestDiskUsage = chartData.diskData[chartData.diskData.length - 1];
                    diskChart.data.datasets[0].data = [
                        latestDiskUsage,
                        100 - latestDiskUsage
                    ];
                    diskChart.update();
                }
                
                toggleRefreshMask(false);
            })
            .catch(error => {
                console.error('Error fetching historical metrics:', error);
                toggleRefreshMask(false);
            });
    }
    
    // Function to update charts with new data
    function updateCharts() {
        toggleRefreshMask(true);
        
        fetch('http://127.0.0.1:7000/historical/api/metrics/')
            .then(response => response.json())
            .then(data => {
                // Get the most recent metric
                const latestMetric = data.reduce((latest, current) => {
                    const latestTime = new Date(latest.timestamp);
                    const currentTime = new Date(current.timestamp);
                    return currentTime > latestTime ? current : latest;
                });
                
                // Format the timestamp
                const timeLabel = formatTimestamp(latestMetric.timestamp);
                
                // Check if this is a new timestamp before adding
                if (chartData.labels.length === 0 || timeLabel !== chartData.labels[chartData.labels.length - 1]) {
                    // Update line charts data
                    chartData.labels.push(timeLabel);
                    chartData.cpuData.push(Math.min(latestMetric.cpu_usage, 100));
                    chartData.memoryData.push(latestMetric.memory_percent);
                    chartData.diskData.push(latestMetric.disk_percent);
                    
                    // Limit chart data points for line charts
                    if (chartData.labels.length > 20) {
                        chartData.labels.shift();
                        chartData.cpuData.shift();
                        chartData.memoryData.shift();
                        chartData.diskData.shift();
                    }
                    
                    // Update line charts
                    cpuChart.update();
                    memoryChart.update();
                    
                    // Update pie chart with latest disk usage
                    diskChart.data.datasets[0].data = [
                        latestMetric.disk_percent,
                        100 - latestMetric.disk_percent
                    ];
                    diskChart.update();
                }
                
                toggleRefreshMask(false);
            })
            .catch(error => {
                console.error('Error fetching metrics:', error);
                toggleRefreshMask(false);
            });
    }
    
    // Track last update time to ensure the refresh mask shows for at least 500ms
    let lastUpdateStartTime = 0;
    
    // Wrapper function to ensure refresh mask is visible for a minimum duration
    function scheduledUpdate() {
        lastUpdateStartTime = Date.now();
        updateCharts();
    }
    
    // Initialize with historical data
    initializeCharts();
    
    // Create a refresh interval indicator
    const refreshIndicator = document.createElement('div');
    refreshIndicator.className = 'refresh-indicator';
    refreshIndicator.innerHTML = 'Last updated: Never';
    dashboardContainer.appendChild(refreshIndicator);
    
    // Add CSS for the refresh indicator
    style.textContent += `
        .refresh-indicator {
            position: absolute;
            top: 128px;
            right: 168px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #4b5563;
        }
    `;
    
    // Start periodic updates every 10 seconds
    setInterval(() => {
        scheduledUpdate();
        refreshIndicator.innerHTML = 'Last updated: ' + new Date().toLocaleTimeString();
    }, 10000);
});