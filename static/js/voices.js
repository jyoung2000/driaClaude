// Voice Management JavaScript

// Load voice library on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVoiceLibrary();
});

// Load voice library
async function loadVoiceLibrary() {
    const voiceLibrary = document.getElementById('voiceLibrary');
    
    try {
        const data = await apiRequest('GET', '/voices/list');
        
        if (data.voices.length === 0) {
            voiceLibrary.innerHTML = '<p class="text-muted">No voices cloned yet. Clone your first voice above!</p>';
            return;
        }
        
        voiceLibrary.innerHTML = data.voices.map(voice => `
            <div class="voice-card">
                <div class="voice-card-header">
                    <div>
                        <h3>${voice.name}</h3>
                        <p class="voice-card-meta">${voice.description || 'No description'}</p>
                        <p class="voice-card-meta">ID: ${voice.id}</p>
                        <p class="voice-card-meta">Duration: ${voice.duration.toFixed(1)}s</p>
                        <p class="voice-card-meta">Created: ${new Date(voice.created_at).toLocaleDateString()}</p>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="deleteVoice('${voice.id}', '${voice.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        voiceLibrary.innerHTML = '<p class="text-muted">Failed to load voices</p>';
        handleApiError(error);
    }
}

// Clone voice
async function cloneVoice(event) {
    event.preventDefault();
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    
    // Get form data
    const formData = new FormData();
    formData.append('name', document.getElementById('voiceName').value);
    formData.append('description', document.getElementById('voiceDescription').value || '');
    formData.append('transcript', document.getElementById('transcript').value);
    formData.append('audio_file', document.getElementById('audioFile').files[0]);
    
    // Show loading
    loadingMessage.textContent = 'Cloning voice...';
    loadingOverlay.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/voices/clone`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('apiKey') || ''}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Voice cloning failed');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Voice cloned successfully!', 'success');
            
            // Reset form
            document.getElementById('cloneForm').reset();
            
            // Reload voice library
            loadVoiceLibrary();
        }
        
    } catch (error) {
        showNotification(error.message || 'Voice cloning failed', 'error');
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

// Delete voice
async function deleteVoice(voiceId, voiceName) {
    if (!confirm(`Are you sure you want to delete the voice "${voiceName}"?`)) {
        return;
    }
    
    try {
        await apiRequest('DELETE', `/voices/${voiceId}`);
        showNotification('Voice deleted successfully', 'success');
        loadVoiceLibrary();
    } catch (error) {
        handleApiError(error);
    }
}