let map;
let marker;
let serviceData;

function initMap() {
    console.log('Initializing update service map...');
    
    if (typeof L === 'undefined') {
        console.error('Leaflet not loaded');
        alert('Map library not loaded. Please refresh the page.');
        return;
    }

    // Get service data from global variable
    if (typeof window.serviceData === 'undefined') {
        console.error('Service data not found');
        return;
    }

    serviceData = window.serviceData;
    
    // Initialize map with current service location or default to Malaysia
    const lat = serviceData.latitude || 3.1390;
    const lng = serviceData.longitude || 101.6869;
    
    map = L.map('map').setView([lat, lng], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add marker for current location if coordinates exist
    if (serviceData.latitude && serviceData.longitude) {
        marker = L.marker([lat, lng]).addTo(map);
        marker.bindPopup('Current service location').openPopup();
    }

    // Handle map clicks
    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        // Update form fields
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;
        
        // Update or create marker
        if (marker) {
            marker.setLatLng([lat, lng]);
        } else {
            marker = L.marker([lat, lng]).addTo(map);
        }
        
        marker.bindPopup('Selected location').openPopup();
        
        console.log('Location selected:', lat, lng);
        
        // Get address from coordinates using reverse geocoding
        getAddressFromCoordinates(lat, lng);
    });
}

// Function to get address from coordinates using OpenStreetMap Nominatim API
async function getAddressFromCoordinates(lat, lng) {
    try {
        console.log('Getting address for coordinates:', lat, lng);
        
        // Show loading indicator
        const addressField = document.getElementById('address');
        const originalValue = addressField.value;
        addressField.value = 'Loading address...';
        addressField.disabled = true;
        
        // Use OpenStreetMap Nominatim API for reverse geocoding
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch address');
        }
        
        const data = await response.json();
        
        if (data.display_name) {
            // Update the address field with the fetched address
            addressField.value = data.display_name;
            console.log('Address updated:', data.display_name);
        } else {
            // Fallback to coordinates if no address found
            addressField.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            console.log('No address found, using coordinates');
        }
        
        // Re-enable the field
        addressField.disabled = false;
        
    } catch (error) {
        console.error('Error getting address:', error);
        
        // Fallback to coordinates on error
        const addressField = document.getElementById('address');
        addressField.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        addressField.disabled = false;
        
        // Show user-friendly error message
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-warning alert-dismissible fade show mt-2';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            Could not automatically fetch address. Please enter the address manually.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const mapContainer = document.getElementById('map');
        mapContainer.parentNode.insertBefore(alertDiv, mapContainer.nextSibling);
    }
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing map...');
    initMap();
});

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('serviceForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const lat = document.getElementById('latitude').value;
            const lng = document.getElementById('longitude').value;
            
            if (!lat || !lng) {
                e.preventDefault();
                alert('Please select a location on the map before submitting.');
                return false;
            }
        });
    }
}); 