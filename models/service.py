"""
Singleton Pattern Implementation for Service Registry
Manages the ServiceRegistry - a centralized component for all public services
"""

from datetime import datetime
from typing import List, Optional

class Service:
    """Service entity class"""
    
    def __init__(self, name, category, description, address, provider_id):
        self.id = None
        self.name = name
        self.category = category
        self.description = description
        self.address = address
        self.latitude = None
        self.longitude = None
        self.phone = None
        self.email = None
        self.hours = None
        self.rating = 0.0
        self.provider_id = provider_id
        self.is_approved = False
        self.created_at = datetime.utcnow()
        self.reviews = []

class ServiceRegistry:
    """
    Singleton class for managing all public services
    Ensures only one instance exists throughout the application
    """
    
    _instance = None
    
    def __init__(self):
        if ServiceRegistry._instance is not None:
            raise Exception("This class is a singleton!")
        
        self.services = []
        self._observers = []
        ServiceRegistry._instance = self
    
    @staticmethod
    def get_instance():
        """Get the singleton instance of ServiceRegistry"""
        if ServiceRegistry._instance is None:
            ServiceRegistry()
        return ServiceRegistry._instance
    
    def add_service(self, service: Service) -> bool:
        """
        Add a new service to the registry
        
        Args:
            service (Service): The service to add
            
        Returns:
            bool: True if service was added successfully
        """
        if service not in self.services:
            service.id = len(self.services) + 1
            self.services.append(service)
            self._notify_observers(f"New service added: {service.name}")
            return True
        return False
    
    def remove_service(self, service_id: int) -> bool:
        """
        Remove a service from the registry
        
        Args:
            service_id (int): ID of the service to remove
            
        Returns:
            bool: True if service was removed successfully
        """
        for i, service in enumerate(self.services):
            if service.id == service_id:
                removed_service = self.services.pop(i)
                self._notify_observers(f"Service removed: {removed_service.name}")
                return True
        return False
    
    def get_service(self, service_id: int) -> Optional[Service]:
        """
        Get a service by ID
        
        Args:
            service_id (int): ID of the service to retrieve
            
        Returns:
            Service: The service if found, None otherwise
        """
        for service in self.services:
            if service.id == service_id:
                return service
        return None
    
    def get_services(self) -> List[Service]:
        """
        Get all services in the registry
        
        Returns:
            List[Service]: List of all services
        """
        return self.services.copy()
    
    def get_services_by_category(self, category: str) -> List[Service]:
        """
        Get services filtered by category
        
        Args:
            category (str): Category to filter by
            
        Returns:
            List[Service]: List of services in the specified category
        """
        return [service for service in self.services if service.category.lower() == category.lower()]
    
    def get_approved_services(self) -> List[Service]:
        """
        Get only approved services
        
        Returns:
            List[Service]: List of approved services
        """
        return [service for service in self.services if service.is_approved]
    
    def approve_service(self, service_id: int) -> bool:
        """
        Approve a service
        
        Args:
            service_id (int): ID of the service to approve
            
        Returns:
            bool: True if service was approved successfully
        """
        service = self.get_service(service_id)
        if service:
            service.is_approved = True
            self._notify_observers(f"Service approved: {service.name}")
            return True
        return False
    
    def update_service(self, service_id: int, **kwargs) -> bool:
        """
        Update service details
        
        Args:
            service_id (int): ID of the service to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if service was updated successfully
        """
        service = self.get_service(service_id)
        if service:
            for key, value in kwargs.items():
                if hasattr(service, key):
                    setattr(service, key, value)
            self._notify_observers(f"Service updated: {service.name}")
            return True
        return False
    
    def add_observer(self, observer):
        """Add an observer to be notified of changes"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, message: str):
        """Notify all observers of changes"""
        for observer in self._observers:
            if hasattr(observer, 'update'):
                observer.update(message)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about the service registry
        
        Returns:
            dict: Statistics about services
        """
        total_services = len(self.services)
        approved_services = len(self.get_approved_services())
        categories = set(service.category for service in self.services)
        
        return {
            'total_services': total_services,
            'approved_services': approved_services,
            'pending_services': total_services - approved_services,
            'categories': list(categories),
            'average_rating': sum(service.rating for service in self.services) / total_services if total_services > 0 else 0
        } 