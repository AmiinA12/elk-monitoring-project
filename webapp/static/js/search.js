// Search.js - Handle search functionality

const searchForm = document.getElementById('searchForm');
const resultsCard = document.getElementById('resultsCard');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsBody = document.getElementById('resultsBody');
const resultCount = document.getElementById('resultCount');
const pagination = document.getElementById('pagination');

let currentPage = 1;
let currentResults = [];

// Handle search form submit
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    currentPage = 1;
    await performSearch();
});

// Reset button
document.getElementById('resetBtn').addEventListener('click', () => {
    searchForm.reset();
    resultsCard.style.display = 'none';
});

// Export button
document.getElementById('exportBtn').addEventListener('click', () => {
    exportToCSV(currentResults);
});

async function performSearch() {
    const query = document.getElementById('searchQuery').value;
    const level = document.getElementById('levelFilter').value;
    const service = document.getElementById('serviceFilter').value;
    const dateRange = document.getElementById('dateRange').value;

    try {
        // Show loading
        resultsCard.style.display = 'block';
        loadingSpinner.classList.remove('d-none');
        resultsBody.innerHTML = '';

        // Build query parameters
        const params = new URLSearchParams({
            q: query,
            level: level,
            service: service,
            date_range: dateRange,
            page: currentPage,
            size: 50
        });

        const response = await fetch(`/api/v1/search?${params}`);
        const data = await response.json();

        currentResults = data.results || [];

        // Hide loading
        loadingSpinner.classList.add('d-none');

        // Display results
        displayResults(currentResults);
        updatePagination(data.total || 0, 50);

    } catch (error) {
        console.error('Search error:', error);
        loadingSpinner.classList.add('d-none');
        showError('Erreur lors de la recherche');
    }
}

function displayResults(results) {
    resultCount.textContent = results.length;

    if (results.length === 0) {
        resultsBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucun résultat trouvé</td></tr>';
        return;
    }

    resultsBody.innerHTML = results.map((log, index) => `
        <tr>
            <td>${formatTimestamp(log.timestamp || log['@timestamp'])}</td>
            <td><span class="badge badge-level-${log.level}">${log.level}</span></td>
            <td>${log.service || '-'}</td>
            <td>${truncate(log.message, 60)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showLogDetail(${index})">
                    <i class="bi bi-eye"></i> Détails
                </button>
            </td>
        </tr>
    `).join('');
}

function showLogDetail(index) {
    const log = currentResults[index];
    const modal = new bootstrap.Modal(document.getElementById('logDetailModal'));
    document.getElementById('logDetailContent').textContent = JSON.stringify(log, null, 2);
    modal.show();
}

function updatePagination(total, pageSize) {
    const totalPages = Math.ceil(total / pageSize);

    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Précédent</a>
    </li>`;

    // Page numbers
    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
            <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
        </li>`;
    }

    // Next button
    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Suivant</a>
    </li>`;

    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    performSearch();
}

function exportToCSV(results) {
    if (results.length === 0) {
        alert('Aucun résultat à exporter');
        return;
    }

    // Create CSV content
    const headers = ['Timestamp', 'Level', 'Service', 'Message'];
    const rows = results.map(log => [
        log.timestamp || log['@timestamp'],
        log.level,
        log.service || '',
        log.message
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(field => `"${field}"`).join(',') + '\n';
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_export_${new Date().getTime()}.csv`;
    a.click();
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
    alert('Erreur: ' + message);
}

// History Handling
async function loadSearchHistory() {
    const historyContainer = document.getElementById('searchHistory');
    try {
        const response = await fetch('/api/v1/search/history');
        const history = await response.json();

        if (history.length === 0) {
            historyContainer.innerHTML = '<div class="text-muted text-center p-3">Aucune recherche récente</div>';
            return;
        }

        historyContainer.innerHTML = history.map(item => `
            <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
               onclick="runHistorySearch('${item.query || ''}', '${item.level || ''}', '${item.service || ''}')">
                <div>
                    <span class="fw-bold">${item.query || 'Tout'}</span>
                    <small class="text-muted ms-2">
                        ${item.level ? `<span class="badge bg-secondary">${item.level}</span>` : ''}
                        ${item.service ? `<span class="badge bg-info">${item.service}</span>` : ''}
                    </small>
                </div>
                <div class="text-end">
                    <span class="badge bg-light text-dark border">${item.results_count} résultats</span>
                    <small class="text-muted d-block">${formatTimestamp(item.date)}</small>
                </div>
            </a>
        `).join('');

    } catch (error) {
        console.error('Error loading history:', error);
        historyContainer.innerHTML = '<div class="text-danger text-center">Erreur de chargement</div>';
    }
}

function runHistorySearch(query, level, service) {
    document.getElementById('searchQuery').value = query;
    document.getElementById('levelFilter').value = level;
    document.getElementById('serviceFilter').value = service;

    // Trigger search
    performSearch();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Load history on start
document.addEventListener('DOMContentLoaded', loadSearchHistory);
