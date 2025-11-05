/**
 * Voice Assistant Handler
 * Supports Tamil and English voice commands using Web Speech API
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentLanguage = 'en-US';
        this.isSpeaking = false;
        
        this.initSpeechRecognition();
    }

    /**
     * Initialize Web Speech API
     */
    initSpeechRecognition() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech recognition not supported');
            return false;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configure recognition
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        this.recognition.lang = this.currentLanguage;

        return true;
    }

    /**
     * Set language (Tamil or English)
     */
    setLanguage(languageCode) {
        this.currentLanguage = languageCode;
        if (this.recognition) {
            this.recognition.lang = languageCode;
        }
    }

    /**
     * Start listening
     */
    startListening(onResult, onError) {
        if (!this.recognition) {
            if (onError) onError('Speech recognition not supported in this browser');
            return;
        }

        if (this.isListening) {
            return;
        }

        this.isListening = true;

        // Set up event handlers
        this.recognition.onstart = () => {
            console.log('Voice recognition started');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            
            console.log('Transcript:', transcript, 'Confidence:', confidence);
            
            if (onResult) {
                onResult(transcript, confidence);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            
            if (onError) {
                const errorMessages = {
                    'no-speech': 'No speech detected. Please try again.',
                    'audio-capture': 'No microphone found. Please check your microphone.',
                    'not-allowed': 'Microphone permission denied. Please allow microphone access.',
                    'network': 'Network error. Please check your connection.'
                };
                
                onError(errorMessages[event.error] || 'Speech recognition error');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            console.log('Voice recognition ended');
        };

        // Start recognition
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.isListening = false;
            if (onError) onError('Could not start speech recognition');
        }
    }

    /**
     * Stop listening
     */
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    /**
     * Speak text using Web Speech API
     */
    speak(text, languageCode = null) {
        if (this.isSpeaking) {
            this.synthesis.cancel();
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = languageCode || this.currentLanguage;
        utterance.rate = 0.9;  // Slightly slower for clarity
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Select appropriate voice
        const voices = this.synthesis.getVoices();
        const langCode = (languageCode || this.currentLanguage).split('-')[0];
        
        const voice = voices.find(v => 
            v.lang.startsWith(langCode) || v.lang.includes(langCode)
        );
        
        if (voice) {
            utterance.voice = voice;
        }

        utterance.onstart = () => {
            this.isSpeaking = true;
        };

        utterance.onend = () => {
            this.isSpeaking = false;
        };

        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isSpeaking = false;
        };

        this.synthesis.speak(utterance);
    }

    /**
     * Stop speaking
     */
    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.isSpeaking = false;
        }
    }

    /**
     * Process voice command through server
     */
    async processCommand(transcript) {
        try {
            const language = this.currentLanguage.startsWith('ta') ? 'ta' : 'en';
            
            const response = await fetch('/voice/process-speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: transcript,
                    language: language
                })
            });

            if (!response.ok) {
                throw new Error('Server error processing command');
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error processing command:', error);
            return {
                success: false,
                message: 'Error processing command'
            };
        }
    }

    /**
     * Get quick command suggestions
     */
    async getQuickCommands() {
        try {
            const response = await fetch('/voice/quick-commands');
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error fetching commands:', error);
            return { success: false, commands: [] };
        }
    }
}

/**
 * Voice Assistant UI Handler
 */
class VoiceAssistantUI {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.assistant = new VoiceAssistant();
        this.currentLanguage = 'en-US';
        
        this.setupUI();
        this.loadQuickCommands();
    }

    setupUI() {
        // UI elements should be in the HTML template
        this.micButton = document.getElementById('micButton');
        this.languageToggle = document.getElementById('languageToggle');
        this.transcriptDisplay = document.getElementById('transcriptDisplay');
        this.responseDisplay = document.getElementById('responseDisplay');
        this.statusText = document.getElementById('statusText');
        this.resultsContainer = document.getElementById('resultsContainer');

        // Event listeners
        if (this.micButton) {
            this.micButton.addEventListener('click', () => this.toggleListening());
        }

        if (this.languageToggle) {
            this.languageToggle.addEventListener('change', (e) => {
                this.currentLanguage = e.target.checked ? 'ta-IN' : 'en-US';
                this.assistant.setLanguage(this.currentLanguage);
                this.updateLanguageDisplay();
            });
        }
    }

    toggleListening() {
        if (this.assistant.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        this.updateStatus('Listening...', 'listening');
        this.micButton.classList.add('listening');
        this.micButton.innerHTML = '<i class="fas fa-stop"></i> Stop';

        this.assistant.startListening(
            (transcript, confidence) => this.handleTranscript(transcript, confidence),
            (error) => this.handleError(error)
        );
    }

    stopListening() {
        this.assistant.stopListening();
        this.updateStatus('Click microphone to speak', 'idle');
        this.micButton.classList.remove('listening');
        this.micButton.innerHTML = '<i class="fas fa-microphone"></i> Speak';
    }

    async handleTranscript(transcript, confidence) {
        this.transcriptDisplay.innerHTML = `
            <div class="alert alert-info">
                <strong>You said:</strong> ${transcript}
                <small class="d-block">Confidence: ${(confidence * 100).toFixed(1)}%</small>
            </div>
        `;

        this.updateStatus('Processing...', 'processing');

        // Process command
        const result = await this.assistant.processCommand(transcript);

        if (result.success) {
            this.displayResults(result);
            
            // Speak response
            if (result.response && result.response.text) {
                this.assistant.speak(result.response.text, this.currentLanguage);
            }
        } else {
            this.displayError(result.message || 'Could not process command');
        }

        this.stopListening();
    }

    handleError(error) {
        this.displayError(error);
        this.stopListening();
    }

    displayResults(result) {
        const command = result.command;
        const actionResult = result.action_result;
        const response = result.response;

        // Chatbot-style response with formatting
        let html = `
            <div class="card border-success mb-3">
                <div class="card-header bg-success text-white">
                    <i class="fas fa-robot"></i> <strong>Assistant</strong>
                </div>
                <div class="card-body">
                    <p class="mb-2">${response.text}</p>
                </div>
            </div>
        `;

        // Display data based on action with chatbot-style formatting
        if (actionResult.data) {
            // PRODUCTS - Show chatbot-style with instructions
            if (actionResult.data.products && actionResult.data.products.length > 0) {
                const products = actionResult.data.products;
                
                html += `
                    <div class="card mb-3">
                        <div class="card-header bg-info text-white">
                            <i class="fas fa-shopping-basket"></i> Found ${products.length} Product(s)
                        </div>
                        <div class="card-body">
                            <p class="mb-3"><strong>Here's what I found for you:</strong></p>
                `;
                
                products.forEach((product, index) => {
                    html += `
                        <div class="border rounded p-3 mb-3 ${index === 0 ? 'border-primary' : ''}">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">
                                        <i class="fas fa-tag text-primary"></i> ${product.name}
                                        ${product.category ? `<span class="badge bg-secondary ms-2">${product.category}</span>` : ''}
                                    </h6>
                                    <p class="mb-2">
                                        <strong class="text-success fs-5">₹${product.price}</strong>
                                        <span class="text-muted">/${product.unit}</span>
                                        ${product.vendor ? `<br><small class="text-muted"><i class="fas fa-store"></i> Sold by: ${product.vendor}</small>` : ''}
                                    </p>
                                    
                                    <div class="mb-2">
                                        <strong>📋 What you can do:</strong>
                                        <ol class="mb-0 mt-1">
                                            <li>Click <strong>"View Details"</strong> to see full product information</li>
                                            <li>Click <strong>"Add to Cart"</strong> to purchase this item</li>
                                            <li>Or continue speaking for more options</li>
                                        </ol>
                                    </div>
                                </div>
                            </div>
                            
                            <hr>
                            
                            <div class="d-flex gap-2">
                                <a href="/retailer/product/${product.id}" class="btn btn-primary btn-sm flex-grow-1">
                                    <i class="fas fa-eye"></i> View Details
                                </a>
                                <button onclick="addToCartFromVoice(${product.id})" class="btn btn-success btn-sm flex-grow-1">
                                    <i class="fas fa-cart-plus"></i> Add to Cart
                                </button>
                            </div>
                            
                            <div class="mt-2">
                                <small class="text-muted">
                                    <i class="fas fa-link"></i> Direct link: 
                                    <a href="/retailer/product/${product.id}" class="text-decoration-none">
                                        /retailer/product/${product.id}
                                    </a>
                                </small>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        <div class="alert alert-light border mt-3">
                            <strong>💡 Next Steps:</strong>
                            <ul class="mb-0 mt-2">
                                <li>To order: Click "Add to Cart" on any product above</li>
                                <li>To browse more: Say "Show me more vegetables" or "What else do you have?"</li>
                                <li>To check cart: Say "Show my cart" or go to <a href="/retailer/cart">Cart Page</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
                `;
            }

            // ORDERS - Chatbot-style with instructions
            if (actionResult.data.orders && actionResult.data.orders.length > 0) {
                const orders = actionResult.data.orders;
                
                html += `
                    <div class="card mb-3">
                        <div class="card-header bg-info text-white">
                            <i class="fas fa-shopping-bag"></i> Your Recent Orders (${orders.length})
                        </div>
                        <div class="card-body">
                            <p class="mb-3"><strong>Here are your recent orders:</strong></p>
                `;
                
                orders.forEach((order, index) => {
                    const statusBadge = this.getOrderStatusBadge(order.status);
                    html += `
                        <div class="border rounded p-3 mb-3">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <h6 class="mb-1">
                                        <i class="fas fa-receipt"></i> Order #${order.id}
                                    </h6>
                                    <p class="mb-1">
                                        Status: ${statusBadge}
                                        <span class="text-muted ms-2"><strong>₹${order.total}</strong></span>
                                    </p>
                                    <small class="text-muted"><i class="fas fa-calendar"></i> ${order.date}</small>
                                </div>
                            </div>
                            
                            <div class="mb-2">
                                <strong>📋 Actions available:</strong>
                                <ol class="mb-0 mt-1">
                                    <li>Click <strong>"Track Order"</strong> to see delivery status and timeline</li>
                                    <li>View order details and items purchased</li>
                                    <li>Check estimated delivery time</li>
                                </ol>
                            </div>
                            
                            <hr>
                            
                            <div class="d-flex gap-2">
                                <a href="/track-order/${order.id}" class="btn btn-primary btn-sm flex-grow-1">
                                    <i class="fas fa-map-marker-alt"></i> Track Order
                                </a>
                                <a href="/retailer/order/${order.id}" class="btn btn-outline-secondary btn-sm flex-grow-1">
                                    <i class="fas fa-info-circle"></i> View Details
                                </a>
                            </div>
                            
                            <div class="mt-2">
                                <small class="text-muted">
                                    <i class="fas fa-link"></i> Tracking link: 
                                    <a href="/track-order/${order.id}" class="text-decoration-none">
                                        /track-order/${order.id}
                                    </a>
                                </small>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        <div class="alert alert-light border mt-3">
                            <strong>💡 Need Help?</strong>
                            <ul class="mb-0 mt-2">
                                <li>To track specific order: Say "Track order [number]"</li>
                                <li>To see all orders: Go to <a href="/retailer/orders">My Orders Page</a></li>
                                <li>Need support? Say "Contact support" or visit <a href="/reports/create">Help Center</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
                `;
            }

            // SINGLE ORDER - Chatbot-style detailed view
            if (actionResult.data.order) {
                const order = actionResult.data.order;
                const statusBadge = this.getOrderStatusBadge(order.status);
                html += `
                    <div class="card mb-3 border-primary">
                        <div class="card-header bg-primary text-white">
                            <i class="fas fa-receipt"></i> Order Details
                        </div>
                        <div class="card-body">
                            <p class="mb-3"><strong>Here's the information about your order:</strong></p>
                            
                            <div class="border rounded p-3 mb-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <p class="mb-2"><strong>Order ID:</strong> #${order.id}</p>
                                        <p class="mb-2"><strong>Status:</strong> ${statusBadge}</p>
                                        <p class="mb-2"><strong>Total Amount:</strong> <span class="text-success fs-5">₹${order.total}</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <p class="mb-2"><strong>Order Date:</strong> ${order.date}</p>
                                        ${order.items_count ? `<p class="mb-2"><strong>Total Items:</strong> ${order.items_count} item(s)</p>` : ''}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <strong>📋 What you can do:</strong>
                                <ol class="mb-0 mt-2">
                                    <li>Click <strong>"Track This Order"</strong> to see live delivery status and 4-step timeline</li>
                                    <li>View complete order details including all items</li>
                                    <li>Contact support if you have any issues</li>
                                </ol>
                            </div>
                            
                            <hr>
                            
                            <div class="d-flex gap-2 flex-wrap">
                                <a href="/track-order/${order.id}" class="btn btn-primary flex-grow-1">
                                    <i class="fas fa-map-marker-alt"></i> Track This Order
                                </a>
                                <a href="/retailer/order/${order.id}" class="btn btn-outline-info flex-grow-1">
                                    <i class="fas fa-file-alt"></i> Full Details
                                </a>
                                <a href="/retailer/orders" class="btn btn-outline-secondary flex-grow-1">
                                    <i class="fas fa-list"></i> All Orders
                                </a>
                            </div>
                            
                            <div class="mt-3">
                                <small class="text-muted">
                                    <i class="fas fa-link"></i> Quick links: 
                                    <a href="/track-order/${order.id}">Track</a> | 
                                    <a href="/retailer/order/${order.id}">Details</a> | 
                                    <a href="/reports/create">Report Issue</a>
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            }

            // HELP - Chatbot-style help menu
            if (actionResult.data.help_text) {
                html += `
                    <div class="card mb-3 border-info">
                        <div class="card-header bg-info text-white">
                            <i class="fas fa-question-circle"></i> Available Voice Commands
                        </div>
                        <div class="card-body">
                            <p class="mb-3"><strong>Here's what I can help you with:</strong></p>
                            
                            <div class="accordion" id="helpAccordion">
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#shopping">
                                            🛒 Shopping Commands
                                        </button>
                                    </h2>
                                    <div id="shopping" class="accordion-collapse collapse show">
                                        <div class="accordion-body">
                                            <ul>
                                                <li>"Order 5 kg tomatoes"</li>
                                                <li>"Show me vegetables"</li>
                                                <li>"What fruits are available?"</li>
                                                <li>"Add to cart"</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#orders">
                                            📦 Order Commands
                                        </button>
                                    </h2>
                                    <div id="orders" class="accordion-collapse collapse">
                                        <div class="accordion-body">
                                            <ul>
                                                <li>"Check my orders"</li>
                                                <li>"Track order 123"</li>
                                                <li>"Where is my order?"</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="alert alert-light border mt-3">
                                <strong>💡 Pro Tip:</strong> You can speak naturally! I understand context and can help with Tamil (தமிழ்) and English commands.
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        // If no data, show helpful chatbot-style message
        if (!actionResult.data || Object.keys(actionResult.data).length === 0) {
            if (actionResult.success) {
                html += `
                    <div class="card mb-3 border-success">
                        <div class="card-body">
                            <div class="alert alert-success mb-3">
                                <i class="fas fa-check-circle"></i> <strong>Success!</strong>
                            </div>
                            <p>${actionResult.message || 'Command executed successfully!'}</p>
                            
                            <div class="mt-3">
                                <strong>📋 What's next?</strong>
                                <ul class="mt-2">
                                    <li>Say another command to continue</li>
                                    <li>Click Quick Commands below for suggestions</li>
                                    <li>Or navigate using the links in the menu</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        this.resultsContainer.innerHTML = html;
        this.updateStatus('Ready', 'success');
    }

    getOrderStatusBadge(status) {
        const statusMap = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'primary',
            'out_for_delivery': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        };
        const color = statusMap[status.toLowerCase().replace(' ', '_')] || 'secondary';
        return `<span class="badge bg-${color}">${status}</span>`;
    }

    displayError(message) {
        const errorHtml = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> <strong>Error:</strong> ${message}
                <hr>
                <p class="mb-0"><small>Try saying:</small></p>
                <ul class="mb-0">
                    <li><small>"Order 5 kg tomatoes"</small></li>
                    <li><small>"Show me vegetables"</small></li>
                    <li><small>"Check my orders"</small></li>
                </ul>
            </div>
        `;
        
        // Show in results container
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = errorHtml;
        }
        
        // Also show in response display if available
        if (this.responseDisplay) {
            this.responseDisplay.innerHTML = errorHtml;
        }
        
        this.updateStatus('Error occurred', 'error');
    }

    updateStatus(text, state) {
        if (this.statusText) {
            this.statusText.textContent = text;
            this.statusText.className = `status-${state}`;
        }
    }

    updateLanguageDisplay() {
        const langName = this.currentLanguage.startsWith('ta') ? 'தமிழ்' : 'English';
        if (document.getElementById('currentLanguage')) {
            document.getElementById('currentLanguage').textContent = langName;
        }
    }

    async loadQuickCommands() {
        const result = await this.assistant.getQuickCommands();
        
        if (result.success && result.commands) {
            const container = document.getElementById('quickCommands');
            if (!container) return;

            const language = this.currentLanguage.startsWith('ta') ? 'ta' : 'en';
            
            container.innerHTML = '<h6>Quick Commands:</h6>';
            result.commands.forEach(cmd => {
                const text = cmd[language];
                const btn = document.createElement('button');
                btn.className = 'btn btn-outline-primary btn-sm m-1';
                btn.textContent = text;
                btn.onclick = () => this.executeQuickCommand(text);
                container.appendChild(btn);
            });
        }
    }

    async executeQuickCommand(commandText) {
        this.transcriptDisplay.innerHTML = `
            <div class="alert alert-info">
                <strong>Command:</strong> ${commandText}
            </div>
        `;
        
        this.updateStatus('Processing...', 'processing');
        
        const result = await this.assistant.processCommand(commandText);
        
        if (result.success) {
            this.displayResults(result);
            if (result.response && result.response.text) {
                this.assistant.speak(result.response.text, this.currentLanguage);
            }
        } else {
            this.displayError(result.message);
        }
        
        this.updateStatus('Ready', 'idle');
    }
}

/**
 * Helper function to add product to cart from voice command
 * This is a global function called from the dynamically generated HTML
 */
function addToCartFromVoice(productId) {
    // Show loading
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    btn.disabled = true;

    // Add to cart via API
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success
            btn.innerHTML = '<i class="fas fa-check"></i> Added!';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-success');
            
            // Show notification
            showVoiceNotification('Product added to cart!', 'success');
            
            // Update cart count if available
            const cartBadge = document.querySelector('.cart-count');
            if (cartBadge) {
                cartBadge.textContent = data.cart_count || '';
            }
            
            // Reset button after 2 seconds
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
        } else {
            btn.innerHTML = '<i class="fas fa-times"></i> Failed';
            btn.classList.add('btn-danger');
            showVoiceNotification(data.message || 'Failed to add to cart', 'error');
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.remove('btn-danger');
                btn.disabled = false;
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        btn.innerHTML = '<i class="fas fa-times"></i> Error';
        showVoiceNotification('Error adding to cart', 'error');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 2000);
    });
}

/**
 * Show notification in voice assistant
 */
function showVoiceNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-info';
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (resultsContainer) {
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show mt-2`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        resultsContainer.insertBefore(notification, resultsContainer.firstChild);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VoiceAssistant, VoiceAssistantUI };
}
