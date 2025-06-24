// Custom JavaScript for SnortAI

// WebSocket connection management
function setupWebSocket() {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onopen = () => {
        console.log('WebSocket connection established');
    };
    
    ws.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 5 seconds
        setTimeout(setupWebSocket, 5000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    return ws;
}

// Chart initialization
function initializeCharts() {
    const alertTypesChart = new Chart(document.getElementById('alertTypesChart'), {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Alert Types Distribution'
                }
            }
        }
    });

    const priorityChart = new Chart(document.getElementById('priorityChart'), {
        type: 'bar',
        data: {
            labels: ['Priority 1', 'Priority 2', 'Priority 3'],
            datasets: [{
                label: 'Alerts by Priority',
                data: [0, 0, 0],
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Alerts by Priority'
                }
            }
        }
    });

    return { alertTypesChart, priorityChart };
}

// Alert list management
function addAlertToList(alert, alertsList) {
    const alertElement = document.createElement('div');
    alertElement.className = 'alert-card bg-gray-50 p-4 rounded cursor-pointer hover:bg-gray-100 mb-4';
    alertElement.innerHTML = `
        <div class="flex justify-between items-center">
            <div>
                <span class="font-semibold">${alert.alert.alert_type}</span>
                <span class="text-sm text-gray-500 ml-2">Priority ${alert.alert.priority}</span>
            </div>
            <span class="text-sm text-gray-500">${new Date(alert.alert.timestamp).toLocaleString()}</span>
        </div>
        <p class="text-sm text-gray-600 mt-2">${alert.alert.message}</p>
    `;
    alertElement.onclick = () => showAlertDetails(alert);
    alertsList.insertBefore(alertElement, alertsList.firstChild);
}

// Modal management
function showAlertDetails(alert) {
    const modal = document.getElementById('alertModal');
    const details = document.getElementById('alertDetails');
    
    details.innerHTML = `
        <div class="grid grid-cols-2 gap-4">
            <div>
                <p class="font-semibold">Alert Type</p>
                <p>${alert.alert.alert_type}</p>
            </div>
            <div>
                <p class="font-semibold">Priority</p>
                <p>${alert.alert.priority}</p>
            </div>
            <div>
                <p class="font-semibold">Source</p>
                <p>${alert.alert.source_ip}:${alert.alert.source_port}</p>
            </div>
            <div>
                <p class="font-semibold">Destination</p>
                <p>${alert.alert.destination_ip}:${alert.alert.destination_port}</p>
            </div>
        </div>
        <div class="mt-4">
            <p class="font-semibold">Analysis</p>
            <p class="mt-2">${alert.analysis}</p>
        </div>
        <div class="mt-4">
            <p class="font-semibold">Recommendations</p>
            <ul class="list-disc list-inside mt-2">
                ${alert.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
        <div class="mt-4">
            <p class="font-semibold">Confidence Score</p>
            <div class="confidence-bar mt-2">
                <div class="confidence-bar-fill" style="width: ${alert.confidence_score * 100}%"></div>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('alertModal').classList.add('hidden');
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    const ws = setupWebSocket();
    const charts = initializeCharts();
    const alertsList = document.getElementById('alertsList');

    ws.onmessage = (event) => {
        const alert = JSON.parse(event.data);
        addAlertToList(alert, alertsList);
        updateCharts(alert, charts);
    };

    // Load initial data
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            if (stats.alert_types) {
                charts.alertTypesChart.data.labels = stats.alert_types.buckets.map(b => b.key);
                charts.alertTypesChart.data.datasets[0].data = stats.alert_types.buckets.map(b => b.doc_count);
                charts.alertTypesChart.update();
            }

            if (stats.priority_distribution) {
                charts.priorityChart.data.datasets[0].data = stats.priority_distribution.buckets.map(b => b.doc_count);
                charts.priorityChart.update();
            }
        });
}); 