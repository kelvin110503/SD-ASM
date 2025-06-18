/**
 * Main JavaScript for Public Service Locator System
 * Demonstrates design patterns and provides general functionality
 */

// Global variables
let currentUser = null;
let notifications = [];

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Public Service Locator System initialized');
    
    // Initialize components
    initializeNotifications();
    initializeSearchFunctionality();
    initializeFormValidation();
    initializeAnimations();

    // Notification actions (mark as read/unread, delete, clear)
    document.querySelectorAll('.notification-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const id = this.getAttribute('data-id');
            const markReadBtn = this.closest('li').querySelector('.mark-read-btn');
            const isRead = markReadBtn.getAttribute('data-read') === '1';
            
            // Only mark as read if it's currently unread
            if (!isRead) {
                fetch(`/notification/${id}/mark_read`, {method: 'POST'})
                    .then(res => res.json())
                    .then(data => {
                        if(data.success) {
                            // Update the mark-read button
                            markReadBtn.setAttribute('data-read', '1');
                            markReadBtn.innerHTML = '<i class="fas fa-envelope-open-text text-secondary"></i>';
                            
                            // Remove bold class from parent li
                            const parent = this.closest('li');
                            if (parent) {
                                parent.classList.remove('fw-bold');
                            }
                            
                            // Update notification count badge
                            updateNotificationCount();
                        }
                    });
            }
        });
    });

    // Mark as read/unread
    document.querySelectorAll('.mark-read-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const id = btn.getAttribute('data-id');
            const isRead = btn.getAttribute('data-read') === '1';
            fetch(`/notification/${id}/${isRead ? 'mark_unread' : 'mark_read'}`, {method: 'POST'})
                .then(res => res.json())
                .then(data => {
                    if(data.success) {
                        // Toggle data-read
                        btn.setAttribute('data-read', isRead ? '0' : '1');
                        // Toggle icon
                        btn.innerHTML = isRead
                            ? '<i class="fas fa-envelope text-primary"></i>'
                            : '<i class="fas fa-envelope-open-text text-secondary"></i>';
                        // Toggle bold class on parent li
                        const parent = btn.closest('li');
                        if (parent) {
                            parent.classList.toggle('fw-bold', !isRead);
                        }
                        // Update notification count badge
                        updateNotificationCount();
                    }
                });
        });
    });
    // Delete notification
    document.querySelectorAll('.delete-notification-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const id = btn.getAttribute('data-id');
            fetch(`/notification/${id}/delete`, {method: 'POST'})
                .then(res => res.json())
                .then(data => { 
                    if(data.success) {
                        // Remove the notification item from the dropdown
                        const notificationItem = btn.closest('li');
                        if (notificationItem) {
                            notificationItem.remove();
                        }
                        // Update notification count badge
                        updateNotificationCount();
                    }
                });
        });
    });
    // Clear all notifications
    document.querySelectorAll('.clear-notifications-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if(confirm('Clear all notifications?')) {
                fetch('/notifications/clear', {method: 'POST'})
                    .then(res => res.json())
                    .then(data => { 
                        if(data.success) {
                            // Clear all notification items from dropdown
                            const dropdown = document.querySelector('#notificationDropdown + .dropdown-menu');
                            if (dropdown) {
                                const items = dropdown.querySelectorAll('li:not(.dropdown-header):not(:last-child):not(:nth-last-child(2))');
                                items.forEach(item => item.remove());
                                // Add "No notifications" message
                                const noNotifications = document.createElement('li');
                                noNotifications.innerHTML = '<span class="dropdown-item text-muted">No notifications</span>';
                                dropdown.insertBefore(noNotifications, dropdown.querySelector('.dropdown-divider'));
                            }
                            // Update notification count badge
                            updateNotificationCount();
                        }
                    });
            }
        });
    });
});

/**
 * Initialize notification system (Observer Pattern demonstration)
 */
function initializeNotifications() {
    console.log('Initializing notification system (Observer Pattern)');
    
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

/**
 * Show notification (Observer Pattern implementation)
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Log notification (Observer Pattern)
    console.log(`Notification sent: ${message} (${type})`);
}

/**
 * Initialize search functionality (Strategy Pattern demonstration)
 */
function initializeSearchFunctionality() {
    console.log('Initializing search functionality (Strategy Pattern)');
    
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = document.getElementById('q')?.value;
            const category = document.getElementById('category')?.value;
            
            console.log(`Search strategy selected: ${category ? 'Category' : 'Location'} search`);
            console.log(`Search query: ${query}`);
        });
    }
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    console.log('Initializing form validation');
    
    // Registration form validation
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password')?.value;
            const email = document.getElementById('email')?.value;
            
            if (password && password.length < 6) {
                e.preventDefault();
                showNotification('Password must be at least 6 characters long', 'warning');
                return false;
            }
            
            if (email && !isValidEmail(email)) {
                e.preventDefault();
                showNotification('Please enter a valid email address', 'warning');
                return false;
            }
            
            console.log('Form validation passed (Factory Pattern will create user)');
        });
    }
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    console.log('Initializing animations');
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add slide-in animations to sections
    const sections = document.querySelectorAll('.row');
    sections.forEach((section, index) => {
        if (index % 2 === 0) {
            section.classList.add('slide-in-left');
        } else {
            section.classList.add('slide-in-right');
        }
    });
}

/**
 * Email validation helper
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to update notification count badge
function updateNotificationCount() {
    const badge = document.querySelector('#notificationDropdown .badge');
    const unreadNotifications = document.querySelectorAll('.mark-read-btn[data-read="0"]');
    const count = unreadNotifications.length;
    
    if (count > 0) {
        if (badge) {
            badge.textContent = count;
        } else {
            // Create badge if it doesn't exist
            const notificationLink = document.querySelector('#notificationDropdown');
            const newBadge = document.createElement('span');
            newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
            newBadge.textContent = count;
            notificationLink.appendChild(newBadge);
        }
    } else {
        // Remove badge if count is 0
        if (badge) {
            badge.remove();
        }
    }
}

// Removed problematic global exports from here, as patterns.js handles global exposure. 