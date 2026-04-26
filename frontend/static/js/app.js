/**
 * AI Travel Planner Frontend
 * Main application logic for frontend-backend communication
 */

// ============================================================================
// CONFIGURATION
// ============================================================================
const API_BASE_URL = 'http://localhost:5000/api';
const MESSAGE_TYPES = {
    USER: 'user',
    ASSISTANT: 'assistant',
    SYSTEM: 'system',
    ERROR: 'error'
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================
const appState = {
    messages: [],
    currentParams: {
        source: null,
        dest: null,
        days: null,
        budget: null,
        preferences: null
    },
    currentItinerary: null,
    isLoading: false
};

// ============================================================================
// DOM ELEMENT REFERENCES
// ============================================================================
const elements = {
    userInput: document.getElementById('userInput'),
    sendBtn: document.getElementById('sendBtn'),
    resetBtn: document.getElementById('resetBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    messagesPanel: document.getElementById('messagesPanel'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    errorToast: document.getElementById('errorToast'),
    missingFieldsAlert: document.getElementById('missingFieldsAlert'),
    missingFieldsList: document.getElementById('missingFieldsList'),
    paramSource: document.getElementById('paramSource'),
    paramDest: document.getElementById('paramDest'),
    paramDays: document.getElementById('paramDays'),
    paramBudget: document.getElementById('paramBudget'),
    paramPreferences: document.getElementById('paramPreferences')
};

// ============================================================================
// EVENT LISTENERS SETUP
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Send button click
    elements.sendBtn.addEventListener('click', handleSendMessage);
    
    // Enter key press
    elements.userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Reset button
    if (elements.resetBtn) {
        elements.resetBtn.addEventListener('click', resetTrip);
    }
    
    // Download button
    if (elements.downloadBtn) {
        elements.downloadBtn.addEventListener('click', downloadItinerary);
    }
    
    // Check API health on load
    checkAPIHealth();
    
    // Focus on input
    elements.userInput.focus();
});

// ============================================================================
// API COMMUNICATION FUNCTIONS
// ============================================================================

/**
 * Check if the backend API is healthy
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            showError('⚠️ Backend API is not responding. Please ensure the server is running on port 5000.');
        }
    } catch (error) {
        showError('🔌 Cannot connect to backend API. Please start the server first.');
        console.error('Health check failed:', error);
    }
}

/**
 * Send message to backend and get response
 * 
 * @param {string} message - User message
 * @returns {Promise<object>} - API response
 */
async function sendChatMessage(message) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: appState.currentParams
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Chat API error:', error);
        throw error;
    }
}

/**
 * Extract intent from user message
 * 
 * @param {string} message - User message
 * @returns {Promise<object>} - Extracted parameters
 */
async function extractIntent(message) {
    try {
        const response = await fetch(`${API_BASE_URL}/extract-intent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Intent extraction error:', error);
        throw error;
    }
}

// ============================================================================
// UI UPDATE FUNCTIONS
// ============================================================================

/**
 * Add message to chat display
 * 
 * @param {string} content - Message content
 * @param {string} type - Message type (user, assistant, system, error)
 */
function addMessage(content, type = MESSAGE_TYPES.SYSTEM) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    
    const contentEl = document.createElement('div');
    contentEl.className = 'message-content';
    contentEl.innerHTML = formatMessage(content);
    
    messageEl.appendChild(contentEl);
    elements.messagesPanel.appendChild(messageEl);
    
    // Auto-scroll to bottom
    elements.messagesPanel.scrollTop = elements.messagesPanel.scrollHeight;
    
    // Store in state
    appState.messages.push({
        content: content,
        type: type,
        timestamp: new Date().toISOString()
    });
}

/**
 * Format message content (convert markdown to HTML)
 * 
 * @param {string} content - Raw message content
 * @returns {string} - Formatted HTML content
 */
function formatMessage(content) {
    // Basic markdown-like formatting
    let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    // Format lists
    formatted = formatted.replace(/^[-*] (.*?)(?=<br>|$)/gm, '<li>$1</li>');
    
    return formatted;
}

/**
 * Update parameters display in sidebar
 */
function updateParametersDisplay() {
    const params = appState.currentParams;
    
    if (elements.paramSource) elements.paramSource.textContent = params.source || '-';
    if (elements.paramDest) elements.paramDest.textContent = params.dest || '-';
    if (elements.paramDays) elements.paramDays.textContent = params.days ? `${params.days} days` : '-';
    if (elements.paramBudget) elements.paramBudget.textContent = params.budget ? `$${parseFloat(params.budget).toLocaleString()}` : '-';
    if (elements.paramPreferences) elements.paramPreferences.textContent = params.preferences || '-';
}

/**
 * Update missing fields alert
 * 
 * @param {array} missingFields - Array of missing field names
 */
function updateMissingFieldsAlert(missingFields) {
    if (!elements.missingFieldsAlert || !elements.missingFieldsList) return;
    
    if (missingFields.length === 0) {
        elements.missingFieldsAlert.classList.add('hidden');
    } else {
        elements.missingFieldsAlert.classList.remove('hidden');
        elements.missingFieldsList.innerHTML = missingFields
            .map(field => `<li>${field}</li>`)
            .join('');
    }
}

/**
 * Show loading indicator
 */
function showLoading() {
    elements.loadingIndicator.classList.remove('hidden');
    appState.isLoading = true;
    elements.sendBtn.disabled = true;
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    elements.loadingIndicator.classList.add('hidden');
    appState.isLoading = false;
    elements.sendBtn.disabled = false;
}

/**
 * Show error toast notification
 * 
 * @param {string} message - Error message
 */
function showError(message) {
    elements.errorToast.textContent = message;
    elements.errorToast.classList.remove('hidden');
    
    setTimeout(() => {
        elements.errorToast.classList.add('hidden');
    }, 5000);
}

/**
 * Display itinerary in chat
 * 
 * @param {string} itinerary - Itinerary content
 */
function displayItinerary(itinerary) {
    // Store itinerary for download
    appState.currentItinerary = itinerary;
    
    // Show itinerary in chat instead of modal
    addMessage(`📅 **Your Travel Itinerary**\n\n${itinerary}`, MESSAGE_TYPES.ASSISTANT);
}

// ============================================================================
// MAIN EVENT HANDLERS
// ============================================================================

/**
 * Handle sending user message
 */
async function handleSendMessage() {
    const message = elements.userInput.value.trim();
    
    if (!message) return;
    
    // Clear input
    elements.userInput.value = '';
    
    // Add user message to chat
    addMessage(message, MESSAGE_TYPES.USER);
    
    // Show loading
    showLoading();
    
    try {
        // Send to backend
        const response = await sendChatMessage(message);
        
        if (!response.success) {
            throw new Error(response.error || 'Unknown error');
        }
        
        // Update current parameters
        appState.currentParams = {
            ...appState.currentParams,
            ...response.parameters
        };
        updateParametersDisplay();
        
        // Handle response based on status
        if (response.status === 'complete' && response.itinerary) {
            // Show itinerary in chat
            displayItinerary(response.itinerary);
        } else if (response.status === 'incomplete') {
            // Show missing fields message
            const missingMsg = response.message || 'Please provide the missing information.';
            addMessage(missingMsg, MESSAGE_TYPES.ASSISTANT);
            updateMissingFieldsAlert(response.missing_fields);
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`❌ ${error.message}`);
        addMessage(`Error: ${error.message}`, MESSAGE_TYPES.ERROR);
    } finally {
        hideLoading();
        elements.userInput.focus();
    }
}

/**
 * Reset trip planning state
 */
function resetTrip() {
    if (confirm('Are you sure? This will clear all trip information.')) {
        appState.currentParams = {
            source: null,
            dest: null,
            days: null,
            budget: null,
            preferences: null
        };
        updateParametersDisplay();
        updateMissingFieldsAlert([]);
        elements.userInput.value = '';
        addMessage('Trip details reset. Let\'s start fresh! Tell me about your new trip.', MESSAGE_TYPES.SYSTEM);
        elements.userInput.focus();
    }
}

/**
 * Download itinerary as text file
 */
function downloadItinerary() {
    const itinerary = appState.currentItinerary;
    if (!itinerary) {
        showError('No itinerary available to download');
        return;
    }
    
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(itinerary));
    element.setAttribute('download', `itinerary_${new Date().toISOString().split('T')[0]}.txt`);
    element.style.display = 'none';
    
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Focus on input field when page loads
window.addEventListener('load', () => {
    elements.userInput.focus();
});
