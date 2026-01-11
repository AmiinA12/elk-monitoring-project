// Dashboard.js - Load and display dashboard data

let logsChart = null;
let servicesChart = null;

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    // Auto-refresh every 30 seconds (optional)
    // setInterval(loadDashboardData, 30000);
});

async function loadDashboardData() {
    try {
        // Fetch stats from API
        const response = await fetch('/api/v1/dashboard/stats');
        const data = await response.json();

        // Update KPI cards
        updateKPIs(data.kpis || {});

        // Update charts
        updateLogsChart(data.logs_timeline || []);
        updateServicesChart(data.services_distribution || []);

        // Update recent logs table
        updateRecentLogs(data.recent_logs || []);

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Impossible de charger les données du dashboard');
    }
}

function updateKPIs(kpis) {
    document.getElementById('total-logs').textContent = kpis.total || 0;
    document.getElementById('info-count').textContent = kpis.info || 0;
    document.getElementById('warning-count').textContent = kpis.warning || 0;
    document.getElementById('error-count').textContent = kpis.error || 0;
}

function updateLogsChart(timelineData) {
    const ctx = document.getElementById('logsChart');

    if (logsChart) {
        logsChart.destroy();
    }

    const labels = timelineData.map(item => item.hour || item.timestamp);
    const infoData = timelineData.map(item => item.info || 0);
    const warningData = timelineData.map(item => item.warning || 0);
    const errorData = timelineData.map(item => item.error || 0);

    logsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'INFO',
                    data: infoData,
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'WARNING',
                    data: warningData,
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'ERROR',
                    data: errorData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateServicesChart(servicesData) {
    const ctx = document.getElementById('servicesChart');

    if (servicesChart) {
        servicesChart.destroy();
    }

    const labels = servicesData.map(item => item.service);
    const counts = servicesData.map(item => item.count);

    servicesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#0d6efd',
                    '#198754',
                    '#ffc107',
                    '#dc3545',
                    '#6c757d'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateRecentLogs(logs) {
    const tbody = document.getElementById('recent-logs');

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Aucun log disponible</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${formatTimestamp(log.timestamp || log['@timestamp'])}</td>
            <td><span class="badge badge-level-${log.level}">${log.level}</span></td>
            <td>${log.service || '-'}</td>
            <td>${truncate(log.message, 80)}</td>
        </tr>
    `).join('');
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('fr-FR');
}

function truncate(str, length) {
    if (!str) return '';
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function showError(message) {
    // Simple error display - could be enhanced with toast notifications
    console.error(message);
}
