// Upload.js - Handle file uploads

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const fileInfo = document.getElementById('fileInfo');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = document.getElementById('progressBar');

// Click to select file
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop handlers
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        displayFileInfo(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        displayFileInfo(e.target.files[0]);
    }
});

// Display file info
function displayFileInfo(file) {
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    fileInfo.classList.remove('d-none');
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// Handle form submit
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        alert('Veuillez sélectionner un fichier');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Show progress
        uploadProgress.classList.remove('d-none');
        updateProgress(0);

        const response = await fetch('/api/v1/upload', {
            method: 'POST',
            body: formData
        });

        updateProgress(100);

        if (response.ok) {
            const result = await response.json();
            showSuccess('Fichier uploadé avec succès!');
            resetForm();
            loadRecentUploads();
        } else {
            const error = await response.json();
            showError(error.message || 'Erreur lors de l\'upload');
        }

    } catch (error) {
        console.error('Upload error:', error);
        showError('Erreur lors de l\'upload du fichier');
    } finally {
        uploadProgress.classList.add('d-none');
    }
});

function updateProgress(percent) {
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
}

function resetForm() {
    uploadForm.reset();
    fileInfo.classList.add('d-none');
}

function showSuccess(message) {
    alert(message); // Could be replaced with toast notification
}

function showError(message) {
    alert('Erreur: ' + message);
}

// Load recent uploads
async function loadRecentUploads() {
    try {
        const response = await fetch('/api/v1/uploads/recent');
        const uploads = await response.json();

        const tbody = document.getElementById('recentUploads');

        if (uploads.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Aucun fichier uploadé</td></tr>';
            return;
        }

        tbody.innerHTML = uploads.map(upload => `
            <tr>
                <td>${upload.filename}</td>
                <td>${new Date(upload.date).toLocaleString('fr-FR')}</td>
                <td>${formatFileSize(upload.size)}</td>
                <td><span class="badge bg-success">Traité</span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteFile('${upload.filename}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading recent uploads:', error);
    }
}

// Load recent uploads on page load
document.addEventListener('DOMContentLoaded', loadRecentUploads);

// Delete file
async function deleteFile(filename) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer ${filename} ?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/uploads/${filename}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showSuccess('Fichier supprimé avec succès');
            loadRecentUploads();
        } else {
            const error = await response.json();
            showError(error.message || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showError('Erreur lors de la suppression du fichier');
    }
}
