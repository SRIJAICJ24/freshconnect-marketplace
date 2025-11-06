/**
 * Voice Assistant for FreshConnect
 * Uses Web Speech API for voice recognition
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.initSpeechRecognition();
    }

    initSpeechRecognition() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech recognition not supported');
            this.showError('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        // Initialize recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configuration
        this.recognition.continuous = false;  // Stop after one result
        this.recognition.interimResults = true;  // Show interim results
        this.recognition.lang = 'en-IN';  // Indian English
        this.recognition.maxAlternatives = 3;

        // Event handlers
        this.recognition.onstart = () => this.onStart();
        this.recognition.onresult = (event) => this.onResult(event);
        this.recognition.onerror = (event) => this.onError(event);
        this.recognition.onend = () => this.onEnd();
    }

    start() {
        if (!this.recognition) {
            this.showError('Speech recognition not available');
            return;
        }

        try {
            this.recognition.start();
            this.isListening = true;
        } catch (e) {
            console.error('Recognition start error:', e);
            this.showError('Could not start voice recognition');
        }
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    onStart() {
        console.log('Voice recognition started');
        this.updateUI('listening');
        this.showStatus('Listening... Speak now!', 'info');
    }

    onResult(event) {
        let interimTranscript = '';
        let finalTranscript = '';

        // Process results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // Update UI with interim results
        if (interimTranscript) {
            this.updateTranscript(interimTranscript, false);
        }

        // Process final result
        if (finalTranscript) {
            this.updateTranscript(finalTranscript, true);
            this.processQuery(finalTranscript);
        }
    }

    onError(event) {
        console.error('Recognition error:', event.error);
        
        let errorMessage = 'Voice recognition error';
        switch (event.error) {
            case 'no-speech':
                errorMessage = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = 'Microphone not found. Please check your microphone.';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone access denied. Please allow microphone access.';
                break;
            case 'network':
                errorMessage = 'Network error. Please check your connection.';
                break;
            default:
                errorMessage = `Error: ${event.error}`;
        }

        this.showError(errorMessage);
        this.updateUI('idle');
    }

    onEnd() {
        console.log('Voice recognition ended');
        this.isListening = false;
        this.updateUI('idle');
    }

    async processQuery(query) {
        this.updateUI('processing');
        this.showStatus('Processing your request...', 'info');

        try {
            const response = await fetch('/voice/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (data.success) {
                // Handle different actions
                if (data.action === 'navigate') {
                    this.showStatus(data.message, 'success');
                    setTimeout(() => {
                        window.location.href = data.url;
                    }, 1000);
                } else if (data.action === 'search') {
                    this.displayResults(data);
                }
            } else {
                this.showError(data.message);
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }
                if (data.examples) {
                    this.showExamples(data.examples);
                }
            }
        } catch (error) {
            console.error('Query processing error:', error);
            this.showError('Failed to process query. Please try again.');
        }

        this.updateUI('idle');
    }

    updateUI(state) {
        const voiceBtn = document.getElementById('voiceButton');
        const voiceIcon = document.getElementById('voiceIcon');
        const voiceIndicator = document.getElementById('voiceIndicator');

        if (!voiceBtn) return;

        // Update button state
        voiceBtn.className = 'voice-btn';
        voiceIcon.className = 'fas';

        switch (state) {
            case 'listening':
                voiceBtn.classList.add('listening');
                voiceIcon.className = 'fas fa-microphone';
                if (voiceIndicator) {
                    voiceIndicator.style.display = 'block';
                }
                break;
            case 'processing':
                voiceBtn.classList.add('processing');
                voiceIcon.className = 'fas fa-spinner fa-spin';
                if (voiceIndicator) {
                    voiceIndicator.style.display = 'none';
                }
                break;
            case 'idle':
            default:
                voiceIcon.className = 'fas fa-microphone-slash';
                if (voiceIndicator) {
                    voiceIndicator.style.display = 'none';
                }
                break;
        }
    }

    updateTranscript(text, isFinal) {
        const transcriptEl = document.getElementById('voiceTranscript');
        if (transcriptEl) {
            transcriptEl.textContent = text;
            transcriptEl.className = isFinal ? 'transcript final' : 'transcript interim';
        }
    }

    displayResults(data) {
        const resultsContainer = document.getElementById('voiceResults');
        if (!resultsContainer) return;

        resultsContainer.innerHTML = '';

        // Show message
        if (data.message) {
            this.showStatus(data.message, 'success');
        }

        // Show parsed query info
        if (data.parsed_query) {
            const queryInfo = document.createElement('div');
            queryInfo.className = 'alert alert-info mb-3';
            let infoText = `Searching for: <strong>${data.parsed_query.product}</strong>`;
            if (data.parsed_query.max_price) {
                infoText += ` under ₹${data.parsed_query.max_price}`;
            }
            if (data.parsed_query.min_price) {
                infoText += ` above ₹${data.parsed_query.min_price}`;
            }
            queryInfo.innerHTML = infoText;
            resultsContainer.appendChild(queryInfo);
        }

        // Display products
        if (data.products && data.products.length > 0) {
            const productsGrid = document.createElement('div');
            productsGrid.className = 'row g-3';

            data.products.forEach(product => {
                const productCard = this.createProductCard(product);
                productsGrid.appendChild(productCard);
            });

            resultsContainer.appendChild(productsGrid);
            resultsContainer.style.display = 'block';
        }
    }

    createProductCard(product) {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6';

        col.innerHTML = `
            <div class="card product-card h-100">
                <div class="card-body">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text">
                        <strong class="text-success">₹${product.price}</strong> / ${product.unit}
                    </p>
                    ${product.category ? `<span class="badge bg-secondary mb-2">${product.category}</span>` : ''}
                    ${product.vendor ? `<p class="text-muted small mb-2">By: ${product.vendor}</p>` : ''}
                    <p class="text-muted small">Stock: ${product.stock} ${product.unit}</p>
                    <form method="POST" action="/retailer/add-to-cart/${product.id}" class="add-to-cart-form">
                        <button type="submit" class="btn btn-primary btn-sm w-100">
                            <i class="fas fa-cart-plus"></i> Add to Cart
                        </button>
                    </form>
                </div>
            </div>
        `;

        return col;
    }

    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('voiceStatus');
        if (!statusEl) return;

        statusEl.className = `alert alert-${type} fade show`;
        statusEl.textContent = message;
        statusEl.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }

    showError(message) {
        this.showStatus(message, 'danger');
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('voiceSuggestions');
        if (!container) return;

        container.innerHTML = '<h6>Did you mean:</h6>';
        const list = document.createElement('ul');
        list.className = 'list-unstyled';

        suggestions.forEach(suggestion => {
            const item = document.createElement('li');
            item.innerHTML = `<a href="#" class="suggestion-link">${suggestion}</a>`;
            item.querySelector('a').addEventListener('click', (e) => {
                e.preventDefault();
                this.processQuery(`find ${suggestion}`);
            });
            list.appendChild(item);
        });

        container.appendChild(list);
        container.style.display = 'block';
    }

    showExamples(examples) {
        const container = document.getElementById('voiceExamples');
        if (!container) return;

        container.innerHTML = '<h6>Try saying:</h6>';
        const list = document.createElement('ul');
        list.className = 'list-unstyled';

        examples.forEach(example => {
            const item = document.createElement('li');
            item.innerHTML = `<small class="text-muted"><i class="fas fa-microphone"></i> "${example}"</small>`;
            list.appendChild(item);
        });

        container.appendChild(list);
        container.style.display = 'block';
    }
}

// Initialize voice assistant when DOM is ready
let voiceAssistant;

document.addEventListener('DOMContentLoaded', function() {
    voiceAssistant = new VoiceAssistant();

    // Voice button click handler
    const voiceBtn = document.getElementById('voiceButton');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            if (voiceAssistant.isListening) {
                voiceAssistant.stop();
            } else {
                voiceAssistant.start();
            }
        });
    }

    // Help button handler
    const helpBtn = document.getElementById('voiceHelp');
    if (helpBtn) {
        helpBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                const response = await fetch('/voice/help');
                const data = await response.json();
                
                if (data.success) {
                    showVoiceHelp(data.examples, data.tips);
                }
            } catch (error) {
                console.error('Help fetch error:', error);
            }
        });
    }
});

function showVoiceHelp(examples, tips) {
    const modal = document.getElementById('voiceHelpModal');
    if (!modal) return;

    const content = document.getElementById('voiceHelpContent');
    if (!content) return;

    let html = '<h5>Voice Commands Examples:</h5>';

    // Display examples by category
    for (const [category, cmds] of Object.entries(examples)) {
        html += `<h6 class="mt-3">${category.replace('_', ' ').toUpperCase()}</h6>`;
        html += '<ul class="list-unstyled">';
        cmds.forEach(cmd => {
            html += `<li><i class="fas fa-microphone text-primary"></i> "${cmd}"</li>`;
        });
        html += '</ul>';
    }

    // Display tips
    if (tips && tips.length > 0) {
        html += '<h5 class="mt-4">Tips:</h5><ul>';
        tips.forEach(tip => {
            html += `<li>${tip}</li>`;
        });
        html += '</ul>';
    }

    content.innerHTML = html;
    
    // Show modal (Bootstrap)
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}
