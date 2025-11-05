// ============================================================================
// MOBILE-FIRST APP LOGIC
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile app
    initializeMobileApp();
});

function initializeMobileApp() {
    // 1. Prevent bounce scrolling on iOS
    preventIOSBounce();
    
    // 2. Handle bottom sheet modals
    setupBottomSheets();
    
    // 3. Setup touch-friendly interactions
    setupTouchHandlers();
    
    // 4. Handle viewport changes
    handleViewportChanges();
    
    // 5. Initialize mobile navigation
    setupMobileNavigation();
}

// ============================================================================
// PREVENT IOS BOUNCE SCROLL
// ============================================================================

function preventIOSBounce() {
    let lastY = 0;
    
    document.addEventListener('touchstart', function(e) {
        lastY = e.touches[0].clientY;
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        const currentY = e.touches[0].clientY;
        const scrollable = e.target.closest('.scrollable, main, .modal-body, .table-responsive');
        
        if (!scrollable) {
            e.preventDefault();
        }
    }, { passive: false });
}

// ============================================================================
// BOTTOM SHEET MODALS
// ============================================================================

function showBottomSheet(content, title = '') {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    
    const modal = document.createElement('div');
    modal.className = 'modal-bottom';
    modal.innerHTML = `
        ${title ? `<div class="modal-header">
            <h5>${title}</h5>
            <button onclick="closeBottomSheet()" style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
        </div>` : ''}
        <div class="modal-body">${content}</div>
    `;
    
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
    
    // Close on backdrop click
    backdrop.addEventListener('click', closeBottomSheet);
}

function closeBottomSheet() {
    const modal = document.querySelector('.modal-bottom');
    const backdrop = document.querySelector('.modal-backdrop');
    
    if (modal) modal.remove();
    if (backdrop) backdrop.remove();
}

// Make functions global
window.showBottomSheet = showBottomSheet;
window.closeBottomSheet = closeBottomSheet;

// ============================================================================
// RETAILER MENU (More button)
// ============================================================================

function showRetailerMenu(event) {
    event.preventDefault();
    
    const menuContent = `
        <div style="padding: 8px 0;">
            <a href="/retailer/orders" style="display: block; padding: 16px 20px; color: #333; text-decoration: none; border-bottom: 1px solid #f0f0f0;">
                <i class="fas fa-history" style="width: 24px; color: #666;"></i> My Orders
            </a>
            <a href="/retailer/credit" style="display: block; padding: 16px 20px; color: #333; text-decoration: none; border-bottom: 1px solid #f0f0f0;">
                <i class="fas fa-medal" style="width: 24px; color: #666;"></i> Credit Score
            </a>
            <a href="/auth/logout" style="display: block; padding: 16px 20px; color: #dc3545; text-decoration: none;">
                <i class="fas fa-sign-out-alt" style="width: 24px;"></i> <strong>Logout</strong>
            </a>
        </div>
    `;
    
    showBottomSheet(menuContent, 'Menu');
}

window.showRetailerMenu = showRetailerMenu;

// ============================================================================
// TOUCH HANDLERS - Visual Feedback
// ============================================================================

function setupTouchHandlers() {
    document.querySelectorAll('.btn, .nav-link, .product-card, .tab-button').forEach(el => {
        el.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });
        
        el.addEventListener('touchend', function() {
            this.style.opacity = '1';
        });
        
        el.addEventListener('touchcancel', function() {
            this.style.opacity = '1';
        });
    });
}

// ============================================================================
// VIEWPORT CHANGE HANDLER
// ============================================================================

function handleViewportChanges() {
    let lastWidth = window.innerWidth;
    
    window.addEventListener('resize', function() {
        const newWidth = window.innerWidth;
        
        if (newWidth !== lastWidth) {
            // Layout changed - update if needed
            console.log('Viewport changed:', newWidth);
            lastWidth = newWidth;
        }
    });
    
    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.scrollTo(0, 0);
        }, 100);
    });
}

// ============================================================================
// MOBILE NAVIGATION
// ============================================================================

function setupMobileNavigation() {
    const navItems = document.querySelectorAll('.nav-item a');
    
    navItems.forEach(item => {
        // Smooth page transitions
        item.addEventListener('click', function(e) {
            // Add loading state if not on same page
            const href = this.getAttribute('href');
            if (href && !href.startsWith('#')) {
                document.body.style.opacity = '0.8';
                setTimeout(() => {
                    document.body.style.opacity = '1';
                }, 200);
            }
        });
    });
}

// ============================================================================
// MOBILE PRODUCT CARD INTERACTION
// ============================================================================

function setupProductCard(cardElement) {
    cardElement.addEventListener('click', function() {
        const productId = this.dataset.productId;
        if (productId) {
            // Navigate to product detail
            window.location.href = `/retailer/product/${productId}`;
        }
    });
}

// ============================================================================
// MOBILE CART MANAGEMENT
// ============================================================================

function addToCart(productId, quantity = 1) {
    fetch('/retailer/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✓ Added to cart!', 'success');
            updateCartCount();
        } else {
            showNotification(data.message || 'Error adding to cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'danger');
    });
}

function updateCartCount() {
    fetch('/retailer/api/cart-count')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.cart-count-badge');
            if (badge) {
                badge.textContent = data.count;
                if (data.count > 0) {
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Error updating cart count:', error));
}

// Make functions global
window.addToCart = addToCart;
window.updateCartCount = updateCartCount;

// ============================================================================
// NOTIFICATIONS - Mobile Toast
// ============================================================================

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 16px;
        right: 16px;
        padding: 16px;
        border-radius: 8px;
        background: ${type === 'success' ? '#28a745' : type === 'danger' ? '#dc3545' : '#17a2b8'};
        color: white;
        z-index: 2000;
        animation: slideUp 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
        font-weight: 500;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

window.showNotification = showNotification;

// ============================================================================
// SWIPE GESTURES (Optional)
// ============================================================================

function setupSwipeGestures(element, callbacks = {}) {
    let startX = 0;
    let startY = 0;
    
    element.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    element.addEventListener('touchend', (e) => {
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const diffX = endX - startX;
        const diffY = endY - startY;
        
        if (Math.abs(diffX) > Math.abs(diffY)) {
            if (diffX > 50 && callbacks.swipeRight) callbacks.swipeRight();
            if (diffX < -50 && callbacks.swipeLeft) callbacks.swipeLeft();
        }
    });
}

window.setupSwipeGestures = setupSwipeGestures;

// ============================================================================
// QUANTITY SELECTOR - Mobile Friendly
// ============================================================================

function createQuantitySelector(initialValue = 1, minValue = 1) {
    const container = document.createElement('div');
    container.style.cssText = 'display: flex; align-items: center; gap: 8px; background: #f5f5f5; border-radius: 8px; padding: 4px; width: fit-content;';
    
    const decreaseBtn = document.createElement('button');
    decreaseBtn.className = 'qty-btn';
    decreaseBtn.textContent = '−';
    decreaseBtn.style.cssText = 'width: 36px; height: 36px; border: none; background: none; font-size: 18px; cursor: pointer;';
    
    const input = document.createElement('input');
    input.type = 'number';
    input.className = 'qty-input';
    input.value = initialValue;
    input.min = minValue;
    input.style.cssText = 'width: 50px; text-align: center; border: none; background: none; font-size: 16px;';
    
    const increaseBtn = document.createElement('button');
    increaseBtn.className = 'qty-btn';
    increaseBtn.textContent = '+';
    increaseBtn.style.cssText = 'width: 36px; height: 36px; border: none; background: none; font-size: 18px; cursor: pointer;';
    
    decreaseBtn.addEventListener('click', () => {
        const currentValue = parseInt(input.value) || minValue;
        if (currentValue > minValue) {
            input.value = currentValue - 1;
            input.dispatchEvent(new Event('change'));
        }
    });
    
    increaseBtn.addEventListener('click', () => {
        const currentValue = parseInt(input.value) || minValue;
        input.value = currentValue + 1;
        input.dispatchEvent(new Event('change'));
    });
    
    container.appendChild(decreaseBtn);
    container.appendChild(input);
    container.appendChild(increaseBtn);
    
    return container;
}

window.createQuantitySelector = createQuantitySelector;

// ============================================================================
// INSTALL APP PROMPT (Optional - for PWA)
// ============================================================================

let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button
    const installBtn = document.querySelector('.install-app-btn');
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.addEventListener('click', () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                }
                deferredPrompt = null;
            });
        });
    }
});

// ============================================================================
// DROPDOWN TOGGLE
// ============================================================================

document.addEventListener('click', function(e) {
    // Close all dropdowns when clicking outside
    if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    }
    
    // Toggle dropdown
    if (e.target.closest('[data-bs-toggle="dropdown"]')) {
        e.preventDefault();
        const menu = e.target.closest('.dropdown').querySelector('.dropdown-menu');
        if (menu) {
            menu.classList.toggle('show');
        }
    }
});

// ============================================================================
// ALERT DISMISS
// ============================================================================

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-close')) {
        const alert = e.target.closest('.alert');
        if (alert) {
            alert.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }
    }
});

// ============================================================================
// DEBUGGING - Log device info
// ============================================================================

function logDeviceInfo() {
    console.log('=== FreshConnect Mobile App ===');
    console.log('Device Info:');
    console.log('Width:', window.innerWidth);
    console.log('Height:', window.innerHeight);
    console.log('Viewport:', document.documentElement.clientWidth + 'x' + document.documentElement.clientHeight);
    console.log('User Agent:', navigator.userAgent);
    console.log('Is Mobile:', /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
    console.log('Touch Support:', 'ontouchstart' in window);
}

logDeviceInfo();

// ============================================================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ============================================================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================================================
// BACK BUTTON HANDLING
// ============================================================================

window.addEventListener('popstate', function(event) {
    // Handle back button navigation if needed
    console.log('Back button pressed');
});

// ============================================================================
// PREVENT DOUBLE TAP ZOOM ON IOS
// ============================================================================

let lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);
