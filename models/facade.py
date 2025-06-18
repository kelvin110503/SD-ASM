"""
Facade Pattern Implementation for User Interface Controller
Simplifies interaction with complex subsystems (SearchService, DetailService, MapService)
"""

from typing import List, Dict, Any
from .search import SearchService, CategorySearch, LocationSearch
from .service import ServiceRegistry

class DetailService:
    """Service for retrieving detailed information about services"""
    
    def get_details(self, service) -> Dict[str, Any]:
        """
        Get detailed information about a service
        
        Args:
            service: Service object
            
        Returns:
            Dict: Detailed service information
        """
        return {
            'id': getattr(service, 'id', None),
            'name': getattr(service, 'name', ''),
            'category': getattr(service, 'category', ''),
            'description': getattr(service, 'description', ''),
            'address': getattr(service, 'address', ''),
            'phone': getattr(service, 'phone', ''),
            'email': getattr(service, 'email', ''),
            'hours': getattr(service, 'hours', ''),
            'rating': getattr(service, 'rating', 0.0),
            'latitude': getattr(service, 'latitude', None),
            'longitude': getattr(service, 'longitude', None),
            'is_approved': getattr(service, 'is_approved', False)
        }
    
    def get_service_summary(self, service) -> Dict[str, Any]:
        """
        Get summary information about a service
        
        Args:
            service: Service object
            
        Returns:
            Dict: Summary service information
        """
        return {
            'id': getattr(service, 'id', None),
            'name': getattr(service, 'name', ''),
            'category': getattr(service, 'category', ''),
            'address': getattr(service, 'address', ''),
            'rating': getattr(service, 'rating', 0.0)
        }

class MapService:
    """Service for map-related operations"""
    
    def display(self, services: List) -> Dict[str, Any]:
        """
        Prepare services for map display
        
        Args:
            services: List of services to display
            
        Returns:
            Dict: Map data with markers
        """
        markers = []
        for service in services:
            if hasattr(service, 'latitude') and hasattr(service, 'longitude'):
                if service.latitude and service.longitude:
                    markers.append({
                        'id': getattr(service, 'id', None),
                        'name': getattr(service, 'name', ''),
                        'category': getattr(service, 'category', ''),
                        'latitude': service.latitude,
                        'longitude': service.longitude,
                        'rating': getattr(service, 'rating', 0.0)
                    })
        
        return {
            'markers': markers,
            'center': self._calculate_center(markers) if markers else {'lat': 0, 'lng': 0}
        }
    
    def _calculate_center(self, markers: List) -> Dict[str, float]:
        """Calculate the center point of all markers"""
        if not markers:
            return {'lat': 0, 'lng': 0}
        
        total_lat = sum(marker['latitude'] for marker in markers)
        total_lng = sum(marker['longitude'] for marker in markers)
        
        return {
            'lat': total_lat / len(markers),
            'lng': total_lng / len(markers)
        }

class NotificationService:
    """Service for handling notifications"""
    
    def send_notification(self, message: str, user_id: int = None):
        """
        Send a notification
        
        Args:
            message (str): Notification message
            user_id (int): Target user ID (optional)
        """
        # In a real implementation, this would send actual notifications
        print(f"Notification: {message}")
        if user_id:
            print(f"Sent to user {user_id}")

class UserInterfaceFacade:
    """
    Facade class that simplifies interaction with complex subsystems
    Provides a unified interface for frontend operations
    """
    
    def __init__(self, service_registry: ServiceRegistry, notification_service: NotificationService):
        """
        Initialize the facade with required services
        
        Args:
            service_registry: Service registry instance
            notification_service: Notification service instance
        """
        self.service_registry = service_registry
        self.notification_service = notification_service
        self.search_service = SearchService()
        self.detail_service = DetailService()
        self.map_service = MapService()
    
    def search_and_display(self, query: str, category: str = None) -> Dict[str, Any]:
        """
        Search for services and prepare them for display
        
        Args:
            query (str): Search query
            category (str): Optional category filter
            
        Returns:
            Dict: Search results with detailed information and map data
        """
        # Get all services from registry
        all_services = self.service_registry.get_services()
        
        # Apply search strategy based on category
        if category:
            from .search import CategorySearch
            self.search_service.set_strategy(CategorySearch())
            search_query = category
        else:
            from .search import LocationSearch
            self.search_service.set_strategy(LocationSearch())
            search_query = query
        
        # Execute search
        filtered_services = self.search_service.execute_search(search_query, all_services)
        
        # Get detailed information for each service
        detailed_services = []
        for service in filtered_services:
            details = self.detail_service.get_details(service)
            detailed_services.append(details)
        
        # Prepare map data
        map_data = self.map_service.display(filtered_services)
        
        return {
            'services': detailed_services,
            'map_data': map_data,
            'query': query,
            'category': category,
            'total_results': len(detailed_services)
        }
    
    def get_service_details(self, service_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific service
        
        Args:
            service_id (int): ID of the service
            
        Returns:
            Dict: Detailed service information
        """
        service = self.service_registry.get_service(service_id)
        if service:
            return self.detail_service.get_details(service)
        return None
    
    def get_map_data(self, services: List = None) -> Dict[str, Any]:
        """
        Get map data for services
        
        Args:
            services (List): List of services (if None, uses all approved services)
            
        Returns:
            Dict: Map data
        """
        if services is None:
            services = self.service_registry.get_approved_services()
        
        return self.map_service.display(services)
    
    def add_service(self, service_data: Dict[str, Any]) -> bool:
        """
        Add a new service through the facade
        
        Args:
            service_data (Dict): Service data
            
        Returns:
            bool: True if service was added successfully
        """
        from .service import Service
        
        service = Service(
            name=service_data.get('name'),
            category=service_data.get('category'),
            description=service_data.get('description'),
            address=service_data.get('address'),
            provider_id=service_data.get('provider_id')
        )
        
        # Set additional properties
        for key, value in service_data.items():
            if hasattr(service, key):
                setattr(service, key, value)
        
        success = self.service_registry.add_service(service)
        
        if success:
            self.notification_service.send_notification(f"New service added: {service.name}")
        
        return success
    
    def approve_service(self, service_id: int) -> bool:
        """
        Approve a service through the facade
        
        Args:
            service_id (int): ID of the service to approve
            
        Returns:
            bool: True if service was approved successfully
        """
        success = self.service_registry.approve_service(service_id)
        
        if success:
            service = self.service_registry.get_service(service_id)
            self.notification_service.send_notification(f"Service approved: {service.name}")
        
        return success
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about services
        
        Returns:
            Dict: Service statistics
        """
        return self.service_registry.get_statistics()
    
    def search_by_multiple_criteria(self, query: str, 
                                  search_name: bool = True,
                                  search_category: bool = True,
                                  search_location: bool = True) -> Dict[str, Any]:
        """
        Advanced search using multiple criteria
        
        Args:
            query (str): Search query
            search_name (bool): Whether to search in names
            search_category (bool): Whether to search in categories
            search_location (bool): Whether to search in locations
            
        Returns:
            Dict: Search results with detailed information
        """
        all_services = self.service_registry.get_services()
        
        from .search import SearchService, NameSearch, CategorySearch, LocationSearch
        
        search_service = SearchService()
        filtered_services = search_service.advanced_search(
            query, all_services, search_name, search_category, search_location
        )
        
        detailed_services = []
        for service in filtered_services:
            details = self.detail_service.get_details(service)
            detailed_services.append(details)
        
        map_data = self.map_service.display(filtered_services)
        
        return {
            'services': detailed_services,
            'map_data': map_data,
            'query': query,
            'total_results': len(detailed_services)
        } 