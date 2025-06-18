/**
 * Enhanced Map functionality for Public Service Locator
 * Features: Auto-location detection, nearest service providers, distance calculations
 */

class ServiceMap {
    constructor(containerId = 'map') {
        this.containerId = containerId;
        this.map = null;
        this.markers = [];
        this.services = [];
        this.userLocation = null;
        this.userMarker = null;
        this.locationButton = null;
    }

    initialize() {
        // Initialize the map with Malaysian coordinates as default
        this.map = L.map(this.containerId).setView([3.1390, 101.6869], 8); // Malaysia coordinates

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add location control button
        this.addLocationControl();

        console.log('Enhanced map initialized with location detection for Malaysia');
    }

    addLocationControl() {
        // Create custom location control
        this.locationButton = L.Control.extend({
            options: {
                position: 'topleft'
            },
            onAdd: function(map) {
                const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                const button = L.DomUtil.create('a', 'leaflet-control-locate', container);
                button.innerHTML = '<i class="fas fa-crosshairs"></i>';
                button.title = 'Get My Location';
                button.style.width = '30px';
                button.style.height = '30px';
                button.style.lineHeight = '30px';
                button.style.textAlign = 'center';
                button.style.backgroundColor = 'white';
                button.style.border = '2px solid rgba(0,0,0,0.2)';
                button.style.borderRadius = '4px';
                button.style.cursor = 'pointer';

                button.onclick = () => {
                    this.detectUserLocation();
                }.bind(this);

                return container;
            }
        });

        this.locationButton().addTo(this.map);
    }

    detectUserLocation() {
        if (!navigator.geolocation) {
            this.showAlert('Geolocation is not supported by this browser.', 'warning');
            return;
        }

        this.showAlert('Detecting your location...', 'info');
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                this.userLocation = { lat, lng };
                
                this.setUserLocation(lat, lng);
                this.findNearestServices();
                this.showAlert('Location detected! Showing nearest services.', 'success');
            },
            (error) => {
                console.error('Error getting location:', error);
                let message = 'Unable to detect your location.';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Location access denied. Please enable location services.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Location information unavailable.';
                        break;
                    case error.TIMEOUT:
                        message = 'Location request timed out.';
                        break;
                }
                this.showAlert(message, 'error');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }

    setUserLocation(lat, lng) {
        // Remove existing user marker
        if (this.userMarker) {
            this.map.removeLayer(this.userMarker);
        }

        // Add user location marker
        this.userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'user-location-marker',
                html: '<div style="background-color: #007bff; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.3);"></div>',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            })
        }).addTo(this.map);

        // Add popup for user location
        this.userMarker.bindPopup('<strong>Your Location</strong><br>Lat: ' + lat.toFixed(6) + '<br>Lng: ' + lng.toFixed(6));

        // Center map on user location
        this.map.setView([lat, lng], 14);
    }

    findNearestServices() {
        if (!this.userLocation || !this.services.length) return;

        // Calculate distances and sort services
        const servicesWithDistance = this.services.map(service => {
            const distance = this.calculateDistance(
                this.userLocation.lat, 
                this.userLocation.lng, 
                service.latitude, 
                service.longitude
            );
            return { ...service, distance };
        }).sort((a, b) => a.distance - b.distance);

        // Show nearest services (top 5)
        const nearestServices = servicesWithDistance.slice(0, 5);
        this.displayNearestServices(nearestServices);
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.deg2rad(lat2 - lat1);
        const dLon = this.deg2rad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        const distance = R * c; // Distance in kilometers
        return distance;
    }

    deg2rad(deg) {
        return deg * (Math.PI/180);
    }

    displayNearestServices(nearestServices) {
        // Create info panel for nearest services
        let infoPanel = document.getElementById('nearest-services-panel');
        if (!infoPanel) {
            infoPanel = document.createElement('div');
            infoPanel.id = 'nearest-services-panel';
            infoPanel.className = 'nearest-services-panel';
            infoPanel.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: white;
                border: 2px solid rgba(0,0,0,0.2);
                border-radius: 8px;
                padding: 15px;
                max-width: 300px;
                max-height: 400px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            `;
            document.getElementById(this.containerId).appendChild(infoPanel);
        }

        let html = '<h6><i class="fas fa-map-marker-alt text-primary"></i> Nearest Services</h6>';
        
        nearestServices.forEach((service, index) => {
            const distanceText = service.distance < 1 ? 
                `${(service.distance * 1000).toFixed(0)}m` : 
                `${service.distance.toFixed(1)}km`;
            
            html += `
                <div class="nearest-service-item" style="margin-bottom: 10px; padding: 8px; border: 1px solid #eee; border-radius: 4px;">
                    <div style="font-weight: bold; color: #007bff;">${index + 1}. ${service.name}</div>
                    <div style="font-size: 0.9em; color: #666;">${service.category}</div>
                    <div style="font-size: 0.8em; color: #888;">
                        <i class="fas fa-ruler"></i> ${distanceText} away
                    </div>
                    <button onclick="window.open('/service/${service.id}', '_blank')" 
                            style="margin-top: 5px; padding: 2px 8px; font-size: 0.8em; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;">
                        View Details
                    </button>
                </div>
            `;
        });

        infoPanel.innerHTML = html;
    }

    addService(service) {
        if (!service.latitude || !service.longitude) {
            console.warn('Service missing coordinates:', service);
            return;
        }

        this.services.push(service);

        // Create custom icon based on service category
        const icon = this.getServiceIcon(service.category);

        const marker = L.marker([service.latitude, service.longitude], { icon })
            .addTo(this.map)
            .bindPopup(this.createServicePopup(service));

        this.markers.push(marker);

        // If user location is set, recalculate nearest services
        if (this.userLocation) {
            this.findNearestServices();
        }
    }

    getServiceIcon(category) {
        const iconColors = {
            'food bank': '#28a745',
            'shelter': '#dc3545',
            'clinic': '#17a2b8',
            'recycling center': '#ffc107',
            'education': '#6f42c1',
            'employment': '#fd7e14',
            'transportation': '#20c997',
            'other': '#6c757d'
        };

        const color = iconColors[category.toLowerCase()] || '#6c757d';

        return L.divIcon({
            className: 'service-marker',
            html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>`,
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });
    }

    createServicePopup(service) {
        const rating = service.rating ? 
            `<div style="color: #ffc107;">
                ${'★'.repeat(Math.floor(service.rating))}${'☆'.repeat(5 - Math.floor(service.rating))}
                (${service.rating.toFixed(1)})
            </div>` : 
            '<div style="color: #999;">No ratings yet</div>';

        return `
            <div style="min-width: 200px;">
                <h6 style="margin: 0 0 5px 0; color: #007bff;">${service.name}</h6>
                <div style="font-size: 0.9em; color: #666; margin-bottom: 5px;">
                    <i class="fas fa-tag"></i> ${service.category}
                </div>
                <div style="font-size: 0.8em; color: #888; margin-bottom: 5px;">
                    <i class="fas fa-map-marker-alt"></i> ${service.address}
                </div>
                ${rating}
                <div style="margin-top: 8px;">
                    <a href="/service/${service.id}" class="btn btn-sm btn-primary" style="text-decoration: none;">
                        <i class="fas fa-info-circle"></i> View Details
                    </a>
                </div>
            </div>
        `;
    }

    clearServices() {
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        this.services = [];
    }

    showAlert(message, type = 'info') {
        // Create or update alert element
        let alertDiv = document.getElementById('map-alert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.id = 'map-alert';
            alertDiv.style.cssText = `
                position: absolute;
                top: 50px;
                left: 50%;
                transform: translateX(-50%);
                padding: 10px 20px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1001;
                max-width: 300px;
                text-align: center;
            `;
            document.getElementById(this.containerId).appendChild(alertDiv);
        }

        const colors = {
            'info': '#17a2b8',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545'
        };

        alertDiv.style.backgroundColor = colors[type] || colors.info;
        alertDiv.textContent = message;

        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
    }
}

// Global map instance
let serviceMap = null;

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        serviceMap = new ServiceMap('map');
        serviceMap.initialize();
        
        // Auto-detect location if services are available
        if (window.servicesData && window.servicesData.length > 0) {
            serviceMap.services = window.servicesData;
            serviceMap.services.forEach(service => serviceMap.addService(service));
            
            // Auto-detect location after a short delay
            setTimeout(() => {
                serviceMap.detectUserLocation();
            }, 1000);
        }
    }
});

// Function to initialize map (called from templates)
function initMap() {
    if (serviceMap && window.servicesData) {
        serviceMap.clearServices();
        serviceMap.services = window.servicesData;
        serviceMap.services.forEach(service => serviceMap.addService(service));
        
        // Auto-detect location when map is initialized
        serviceMap.detectUserLocation();
    }
}

// Map utility functions
function showServiceOnMap(serviceId) {
    if (window.serviceMap) {
        // Fetch service details and show on map
        fetch(`/api/services/${serviceId}`)
            .then(response => response.json())
            .then(service => {
                window.serviceMap.clearServices();
                window.serviceMap.addService(service);
            })
            .catch(error => {
                console.error('Error loading service:', error);
            });
    }
}

function updateMapFromSearch(query) {
    if (window.serviceMap) {
        window.serviceMap.searchAndHighlight(query);
    }
} 