// Search page JavaScript with comprehensive debugging
console.log('=== search.js loaded successfully ===');

let map;
let markers = [];

function initializeMap() {
    console.log('=== initializeMap called ===');
    
    if (typeof L === 'undefined') {
        console.error('Leaflet (L) is not defined. Ensure Leaflet library is loaded.');
        alert('Map library not loaded. Please refresh the page.');
        return;
    }

    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.error('Map container div with ID "map" not found!');
        return;
    }

    if (map) {
        console.log('Map already initialized. Invalidating size.');
        map.invalidateSize();
        return;
    }

    try {
        console.log('Creating new Leaflet map instance...');
        map = L.map('map').setView([34.0522, -118.2437], 10); // Default to LA area
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        console.log('Map tile layer added successfully.');
        window.mapInitialized = true;
        
    } catch (e) {
        console.error('Error initializing map:', e);
        alert('Error initializing map: ' + e.message);
    }
}

function addMarkersToMap(services) {
    console.log('=== addMarkersToMap called with', services.length, 'services ===');
    
    if (!map) {
        console.error('Map not initialized. Cannot add markers.');
        return;
    }

    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    services.forEach((service, index) => {
        if (service.latitude && service.longitude) {
            try {
                const marker = L.marker([service.latitude, service.longitude])
                    .addTo(map)
                    .bindPopup(`
                        <b>${service.name}</b><br>
                        ${service.address}<br>
                        <a href="/service/${service.id}" class="btn btn-sm btn-primary">Details</a>
                    `);
                markers.push(marker);
                console.log(`Added marker ${index + 1}: ${service.name}`);
            } catch (e) {
                console.error(`Error adding marker for service ${service.name}:`, e);
            }
        } else {
            console.warn(`Service "${service.name}" missing coordinates.`);
        }
    });

    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds());
        console.log('Map bounds fitted to markers.');
    } else {
        console.log('No markers to add.');
    }
}

function getCurrentLocation() {
    console.log('=== getCurrentLocation called ===');
    
    if (!navigator.geolocation) {
        console.error('Geolocation not supported');
        alert('Geolocation is not supported by your browser.');
        return;
    }

    console.log('Requesting current position...');
    navigator.geolocation.getCurrentPosition(
        function(position) {
            console.log('Geolocation success:', position.coords);
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Update form fields
            const latInput = document.getElementById('user_lat');
            const lonInput = document.getElementById('user_lon');
            if (latInput) latInput.value = lat;
            if (lonInput) lonInput.value = lon;
            
            console.log('Location fields updated:', lat, lon);
            alert(`Location obtained: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
        },
        function(error) {
            console.error('Geolocation error:', error);
            let errorMessage = 'Error getting location: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Permission denied. Please allow location access.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Request timed out.';
                    break;
                default:
                    errorMessage += error.message;
            }
            alert(errorMessage);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
}

function switchToListView() {
    console.log('=== switchToListView called ===');
    const listContent = document.getElementById('listViewContent');
    const mapContent = document.getElementById('mapViewContent');
    const listBtn = document.getElementById('listView');
    const mapBtn = document.getElementById('mapView');
    
    if (listContent && mapContent && listBtn && mapBtn) {
        listContent.style.display = 'block';
        mapContent.style.display = 'none';
        listBtn.classList.add('active');
        mapBtn.classList.remove('active');
        console.log('Switched to list view');
    } else {
        console.error('View toggle elements not found');
    }
}

function switchToMapView() {
    console.log('=== switchToMapView called ===');
    const listContent = document.getElementById('listViewContent');
    const mapContent = document.getElementById('mapViewContent');
    const listBtn = document.getElementById('listView');
    const mapBtn = document.getElementById('mapView');
    
    if (listContent && mapContent && listBtn && mapBtn) {
        listContent.style.display = 'none';
        mapContent.style.display = 'block';
        listBtn.classList.remove('active');
        mapBtn.classList.add('active');
        
        // Initialize map if needed
        if (!window.mapInitialized) {
            console.log('Initializing map for first time...');
            initializeMap();
        } else if (map) {
            console.log('Map already initialized, invalidating size...');
            map.invalidateSize();
        }
        
        console.log('Switched to map view');
    } else {
        console.error('View toggle elements not found');
    }
}

function centerMapOnUser() {
    console.log('=== centerMapOnUser called ===');
    if (!map) {
        console.error('Map not initialized');
        return;
    }
    
    if (!navigator.geolocation) {
        alert('Geolocation not supported');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            map.setView([lat, lon], 15);
            console.log('Map centered on user location:', lat, lon);
        },
        function(error) {
            console.error('Error getting location for map centering:', error);
            alert('Could not get your location to center the map.');
        }
    );
}

function showAllServicesOnMap() {
    console.log('=== showAllServicesOnMap called ===');
    const servicesDataElement = document.getElementById('services-data');
    if (servicesDataElement) {
        const services = JSON.parse(servicesDataElement.dataset.services);
        addMarkersToMap(services);
    } else {
        console.error('Services data element not found');
    }
}

function resetMapView() {
    console.log('=== resetMapView called ===');
    if (map) {
        map.setView([34.0522, -118.2437], 10);
        console.log('Map view reset');
    }
}

// Main initialization function
function initializeSearchPage() {
    console.log('=== Search page initialization started ===');
    
    // Get DOM elements
    const getGeolocationBtn = document.getElementById('getGeolocationBtn');
    const listViewBtn = document.getElementById('listView');
    const mapViewBtn = document.getElementById('mapView');
    const findNearMeBtn = document.getElementById('findNearMeBtn');
    const showAllServicesBtn = document.getElementById('showAllServicesBtn');
    const resetMapBtn = document.getElementById('resetMapBtn');
    
    console.log('DOM elements found:', {
        getGeolocationBtn: !!getGeolocationBtn,
        listViewBtn: !!listViewBtn,
        mapViewBtn: !!mapViewBtn,
        findNearMeBtn: !!findNearMeBtn,
        showAllServicesBtn: !!showAllServicesBtn,
        resetMapBtn: !!resetMapBtn
    });
    
    // Attach event listeners
    if (getGeolocationBtn) {
        console.log('Attaching click listener to getGeolocationBtn');
        getGeolocationBtn.addEventListener('click', getCurrentLocation);
    }
    
    if (listViewBtn) {
        console.log('Attaching click listener to listViewBtn');
        listViewBtn.addEventListener('click', switchToListView);
    }
    
    if (mapViewBtn) {
        console.log('Attaching click listener to mapViewBtn');
        mapViewBtn.addEventListener('click', switchToMapView);
    }
    
    if (findNearMeBtn) {
        console.log('Attaching click listener to findNearMeBtn');
        findNearMeBtn.addEventListener('click', centerMapOnUser);
    }
    
    if (showAllServicesBtn) {
        console.log('Attaching click listener to showAllServicesBtn');
        showAllServicesBtn.addEventListener('click', showAllServicesOnMap);
    }
    
    if (resetMapBtn) {
        console.log('Attaching click listener to resetMapBtn');
        resetMapBtn.addEventListener('click', resetMapView);
    }
    
    console.log('=== Search page initialization completed ===');
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - calling initializeSearchPage');
    initializeSearchPage();
}); 