/**
 * Camera Handler for Product Recognition
 * Handles webcam access, capture, and AI analysis
 */

class CameraHandler {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.stream = null;
        this.isStreaming = false;
    }

    /**
     * Start camera stream
     */
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use back camera on mobile
                }
            });

            this.video.srcObject = this.stream;
            this.isStreaming = true;

            return { success: true };
        } catch (error) {
            console.error('Error accessing camera:', error);
            return {
                success: false,
                message: 'Could not access camera. Please check permissions.'
            };
        }
    }

    /**
     * Stop camera stream
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
            this.isStreaming = false;
        }
    }

    /**
     * Capture image from video stream
     * Returns base64 encoded image
     */
    captureImage() {
        if (!this.isStreaming) {
            return null;
        }

        // Set canvas size to match video
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;

        // Draw video frame to canvas
        const context = this.canvas.getContext('2d');
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

        // Convert to base64
        return this.canvas.toDataURL('image/jpeg', 0.9);
    }

    /**
     * Capture and analyze product
     */
    async captureAndAnalyze() {
        const imageData = this.captureImage();
        
        if (!imageData) {
            return {
                success: false,
                message: 'No image captured'
            };
        }

        try {
            const response = await fetch('/vision/analyze-product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error analyzing image:', error);
            return {
                success: false,
                message: 'Error analyzing image'
            };
        }
    }

    /**
     * Quality check on captured image
     */
    async captureAndCheckQuality() {
        const imageData = this.captureImage();
        
        if (!imageData) {
            return {
                success: false,
                message: 'No image captured'
            };
        }

        try {
            const response = await fetch('/vision/quality-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Error in quality check:', error);
            return {
                success: false,
                message: 'Error in quality check'
            };
        }
    }
}

/**
 * Auto-fill product form with AI-identified data
 */
function fillProductForm(productInfo) {
    // Fill product name
    if (productInfo.product_name && document.getElementById('product_name')) {
        document.getElementById('product_name').value = productInfo.product_name;
    }

    // Fill category
    if (productInfo.category && document.getElementById('category')) {
        const categorySelect = document.getElementById('category');
        for (let option of categorySelect.options) {
            if (option.value.toLowerCase() === productInfo.category.toLowerCase()) {
                categorySelect.value = option.value;
                break;
            }
        }
    }

    // Fill description
    if (productInfo.description && document.getElementById('description')) {
        document.getElementById('description').value = productInfo.description;
    }

    // Fill unit
    if (productInfo.unit && document.getElementById('unit')) {
        document.getElementById('unit').value = productInfo.unit;
    }

    // Suggest price (if there's a price field)
    if (productInfo.suggested_price_range && document.getElementById('price')) {
        // Extract middle of range (e.g., "40-60" -> 50)
        const range = productInfo.suggested_price_range.split('-');
        if (range.length === 2) {
            const avgPrice = (parseInt(range[0]) + parseInt(range[1])) / 2;
            document.getElementById('price').value = avgPrice;
        }
    }

    // Show confidence level
    if (productInfo.confidence) {
        showNotification(`Product identified with ${productInfo.confidence} confidence!`, 
                        productInfo.confidence === 'High' ? 'success' : 'warning');
    }

    // Show quality assessment if available
    if (productInfo.quality_assessment) {
        const qualityColors = {
            'Excellent': 'success',
            'Good': 'info',
            'Fair': 'warning',
            'Poor': 'danger'
        };
        const color = qualityColors[productInfo.quality_assessment] || 'info';
        showNotification(`Quality: ${productInfo.quality_assessment}`, color);
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CameraHandler, fillProductForm, showNotification };
}
