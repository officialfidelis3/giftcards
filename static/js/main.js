/**
 * GiftCard Store - Main JavaScript
 * Handles client-side functionality for the gift card affiliate website
 */

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the main application
 */
function initializeApp() {
    initializeSearch();
    initializeAnimations();
    initializeTooltips();
    initializeLazyLoading();
    initializeFormEnhancements();
    initializeAnalytics();
    
    // Show page content with animation
    document.body.classList.add('loaded');
}

/**
 * Enhanced search functionality
 */
function initializeSearch() {
    const searchForms = document.querySelectorAll('form[action*="search"]');
    
    searchForms.forEach(form => {
        const searchInput = form.querySelector('input[name="q"]');
        const searchBtn = form.querySelector('button[type="submit"]');
        
        if (searchInput && searchBtn) {
            // Add search suggestions (if needed in future)
            searchInput.addEventListener('input', debounce(handleSearchInput, 300));
            
            // Enhanced form submission
            form.addEventListener('submit', function(e) {
                const query = searchInput.value.trim();
                
                if (!query) {
                    e.preventDefault();
                    showNotification('Please enter a search term', 'warning');
                    searchInput.focus();
                    return;
                }
                
                // Add loading state
                searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
                searchBtn.disabled = true;
            });
        }
    });
}

/**
 * Handle search input changes
 */
function handleSearchInput(event) {
    const query = event.target.value.trim();
    
    // Could implement search suggestions here
    if (query.length >= 2) {
        // Future: Show search suggestions dropdown
        console.log('Search query:', query);
    }
}

/**
 * Initialize scroll-triggered animations
 */
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe cards and sections
    const animationTargets = document.querySelectorAll('.card, .feature-card, .contact-method');
    animationTargets.forEach(target => {
        observer.observe(target);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

/**
 * Initialize lazy loading for images
 */
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

/**
 * Enhance forms with better UX
 */
function initializeFormEnhancements() {
    // Contact form enhancements
    const contactForm = document.querySelector('#contact form');
    if (contactForm) {
        enhanceContactForm(contactForm);
    }
    
    // Newsletter forms (if any) - placeholder for future enhancement
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    // newsletterForms.forEach(enhanceNewsletterForm);
    
    // Admin forms
    const adminForms = document.querySelectorAll('.admin-form');
    adminForms.forEach(enhanceAdminForm);
}

/**
 * Enhance contact form
 */
function enhanceContactForm(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Add real-time validation
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        if (!validateForm(form)) {
            e.preventDefault();
            return;
        }
        
        // Add loading state
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
            submitBtn.disabled = true;
        }
    });
}

/**
 * Validate individual form field
 */
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError(event);
    
    // Validation rules
    let isValid = true;
    let errorMessage = '';
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    } else if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    } else if (fieldName === 'message' && value && value.length < 10) {
        isValid = false;
        errorMessage = 'Message must be at least 10 characters long';
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

/**
 * Clear field error
 */
function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('is-invalid');
    
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    fields.forEach(field => {
        const fieldValid = validateField({ target: field });
        if (!fieldValid) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Initialize basic analytics tracking
 */
function initializeAnalytics() {
    // Track page views (could be enhanced with Google Analytics)
    trackPageView();
    
    // Track affiliate link clicks
    const affiliateLinks = document.querySelectorAll('a[href*="affiliate-redirect"]');
    affiliateLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const productId = this.href.split('/').pop();
            trackAffiliateClick(productId);
        });
    });
    
    // Track search usage
    const searchForms = document.querySelectorAll('form[action*="search"]');
    searchForms.forEach(form => {
        form.addEventListener('submit', function() {
            const query = form.querySelector('input[name="q"]').value;
            trackSearch(query);
        });
    });
}

/**
 * Track page view
 */
function trackPageView() {
    const page = window.location.pathname;
    console.log('Page view:', page);
    
    // Could send to analytics service
    // Example: gtag('event', 'page_view', { page_path: page });
}

/**
 * Track affiliate click
 */
function trackAffiliateClick(productId) {
    console.log('Affiliate click tracked:', productId);
    
    // Could send to analytics service
    // Example: gtag('event', 'affiliate_click', { product_id: productId });
}

/**
 * Track search
 */
function trackSearch(query) {
    console.log('Search tracked:', query);
    
    // Could send to analytics service
    // Example: gtag('event', 'search', { search_term: query });
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Utility function to truncate text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
            top: elementPosition - offset,
            behavior: 'smooth'
        });
    }
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        showNotification('Failed to copy text', 'error');
    }
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Enhanced admin form functionality
 */
function enhanceAdminForm(form) {
    // Auto-save draft functionality (for longer forms)
    if (form.classList.contains('auto-save')) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                saveDraft(form);
            }, 1000));
        });
        
        // Load draft on page load
        loadDraft(form);
    }
    
    // Confirm navigation away from unsaved changes
    let hasUnsavedChanges = false;
    
    form.addEventListener('input', () => {
        hasUnsavedChanges = true;
    });
    
    form.addEventListener('submit', () => {
        hasUnsavedChanges = false;
    });
    
    window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

/**
 * Save form draft to localStorage
 */
function saveDraft(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`draft_${form.id}`, JSON.stringify(data));
}

/**
 * Load form draft from localStorage
 */
function loadDraft(form) {
    const draftData = localStorage.getItem(`draft_${form.id}`);
    
    if (draftData) {
        try {
            const data = JSON.parse(draftData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            
            showNotification('Draft loaded', 'info');
        } catch (error) {
            console.error('Error loading draft:', error);
        }
    }
}

/**
 * Clear form draft
 */
function clearDraft(formId) {
    localStorage.removeItem(`draft_${formId}`);
}

// Export functions for use in other scripts
window.GiftCardStore = {
    showNotification,
    copyToClipboard,
    scrollToElement,
    formatCurrency,
    truncateText,
    debounce,
    trackAffiliateClick,
    trackSearch
};
