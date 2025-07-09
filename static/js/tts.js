// TTS Interface JavaScript

let currentAudioUrl = null;
let recentGenerations = [];

// Load voices on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVoices();
    loadRecentGenerations();
    setupParameterListeners();
});

// Setup parameter value displays
function setupParameterListeners() {
    const params = [
        { id: 'temperature', displayId: 'tempValue' },
        { id: 'guidanceScale', displayId: 'guidanceValue' },
        { id: 'topP', displayId: 'topPValue' },
        { id: 'topK', displayId: 'topKValue' }
    ];
    
    params.forEach(param => {
        const input = document.getElementById(param.id);
        const display = document.getElementById(param.displayId);
        
        input.addEventListener('input', () => {
            display.textContent = input.value;
        });
    });
}

// Load available voices
async function loadVoices() {
    try {
        const data = await apiRequest('GET', '/voices/list');
        const select = document.getElementById('voiceSelect');
        
        // Clear existing options except default
        select.innerHTML = '<option value="">Default Voice (Random)</option>';
        
        // Add voice options
        data.voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = `${voice.name} ${voice.description ? `- ${voice.description}` : ''}`;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('Failed to load voices:', error);
    }
}

// Generate speech
async function generateSpeech() {
    const text = document.getElementById('textInput').value.trim();
    
    if (!text) {
        showNotification('Please enter some text', 'warning');
        return;
    }
    
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    
    // Disable button and show loading
    generateBtn.disabled = true;
    loadingSpinner.style.display = 'flex';
    resultsSection.style.display = 'none';
    
    try {
        // Prepare request data
        const requestData = {
            text: text,
            voice_id: document.getElementById('voiceSelect').value || null,
            temperature: parseFloat(document.getElementById('temperature').value),
            guidance_scale: parseFloat(document.getElementById('guidanceScale').value),
            top_p: parseFloat(document.getElementById('topP').value),
            top_k: parseInt(document.getElementById('topK').value)
        };
        
        // Add seed if provided
        const seed = document.getElementById('seed').value;
        if (seed) {
            requestData.seed = parseInt(seed);
        }
        
        // Generate speech
        const response = await apiRequest('POST', '/tts/generate', requestData);
        
        if (response.success) {
            // Update audio player
            const audioPlayer = document.getElementById('audioPlayer');
            const downloadBtn = document.getElementById('downloadBtn');
            const audioMetadata = document.getElementById('audioMetadata');
            
            currentAudioUrl = response.audio_url;
            audioPlayer.src = currentAudioUrl;
            downloadBtn.href = currentAudioUrl;
            downloadBtn.download = response.filename;
            
            // Display metadata
            audioMetadata.textContent = JSON.stringify(response.metadata, null, 2);
            
            // Show results
            resultsSection.style.display = 'block';
            
            // Add to recent generations
            addToRecentGenerations({
                text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
                filename: response.filename,
                url: response.audio_url,
                timestamp: new Date().toISOString()
            });
            
            showNotification('Speech generated successfully!', 'success');
        }
        
    } catch (error) {
        handleApiError(error);
    } finally {
        generateBtn.disabled = false;
        loadingSpinner.style.display = 'none';
    }
}

// Copy audio URL to clipboard
function copyAudioUrl() {
    if (currentAudioUrl) {
        const fullUrl = window.location.origin + currentAudioUrl;
        copyToClipboard(fullUrl);
    }
}

// Add to recent generations
function addToRecentGenerations(item) {
    recentGenerations.unshift(item);
    
    // Keep only last 10
    if (recentGenerations.length > 10) {
        recentGenerations = recentGenerations.slice(0, 10);
    }
    
    // Save to localStorage
    localStorage.setItem('recentGenerations', JSON.stringify(recentGenerations));
    
    // Update display
    displayRecentGenerations();
}

// Load recent generations from localStorage
function loadRecentGenerations() {
    const saved = localStorage.getItem('recentGenerations');
    if (saved) {
        recentGenerations = JSON.parse(saved);
        displayRecentGenerations();
    }
}

// Display recent generations
function displayRecentGenerations() {
    const recentList = document.getElementById('recentList');
    
    if (recentGenerations.length === 0) {
        recentList.innerHTML = '<p class="text-muted">No recent generations</p>';
        return;
    }
    
    recentList.innerHTML = recentGenerations.map(item => `
        <div class="recent-item">
            <div>
                <strong>${item.text}</strong>
                <div class="voice-card-meta">${new Date(item.timestamp).toLocaleString()}</div>
            </div>
            <div class="audio-actions">
                <button class="btn btn-sm btn-secondary" onclick="playRecentAudio('${item.url}')">
                    <i class="fas fa-play"></i>
                </button>
                <a href="${item.url}" download="${item.filename}" class="btn btn-sm btn-success">
                    <i class="fas fa-download"></i>
                </a>
            </div>
        </div>
    `).join('');
}

// Play recent audio
function playRecentAudio(url) {
    const audioPlayer = document.getElementById('audioPlayer');
    const resultsSection = document.getElementById('resultsSection');
    
    audioPlayer.src = url;
    resultsSection.style.display = 'block';
    audioPlayer.play();
}