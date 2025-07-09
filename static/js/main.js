// Main JavaScript file for driaClaude

// API Base URL
const API_BASE = '/api/v1';

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    if (error.response) {
        error.response.json().then(data => {
            showNotification(data.detail || 'An error occurred', 'error');
        }).catch(() => {
            showNotification('An error occurred', 'error');
        });
    } else {
        showNotification('Network error. Please try again.', 'error');
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// Get API headers
function getApiHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Add auth header if needed
    const apiKey = localStorage.getItem('apiKey');
    if (apiKey) {
        headers['Authorization'] = `Bearer ${apiKey}`;
    }
    
    return headers;
}

// Make API request
async function apiRequest(method, endpoint, data = null) {
    const options = {
        method: method,
        headers: getApiHeaders()
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    
    if (!response.ok) {
        throw { response };
    }
    
    return response.json();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Add notification styles
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 0.375rem;
            color: white;
            font-weight: 500;
            z-index: 9999;
            transition: opacity 0.3s;
            max-width: 400px;
        }
        .notification-info {
            background-color: #3b82f6;
        }
        .notification-success {
            background-color: #10b981;
        }
        .notification-error {
            background-color: #ef4444;
        }
        .notification-warning {
            background-color: #f59e0b;
        }
    `;
    document.head.appendChild(style);
});