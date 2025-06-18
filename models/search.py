"""
Strategy Pattern Implementation for Search Service
Provides interchangeable search strategies (CategorySearch, LocationSearch)
"""

from abc import ABC, abstractmethod
from typing import List
import math

class SearchStrategy(ABC):
    """Abstract base class for search strategies"""
    
    @abstractmethod
    def search(self, query: str, services: List) -> List:
        """
        Execute search using this strategy
        
        Args:
            query (str): Search query
            services (List): List of services to search through
            
        Returns:
            List: Filtered list of services
        """
        pass

class CategorySearch(SearchStrategy):
    """Search strategy for finding services by category"""
    
    def search(self, query: str, services: List) -> List:
        """
        Search services by category
        
        Args:
            query (str): Category to search for
            services (List): List of services to search through
            
        Returns:
            List: Services matching the category
        """
        if not query:
            return services
        
        query_lower = query.lower()
        return [
            service for service in services 
            if hasattr(service, 'category') and 
            query_lower in service.category.lower()
        ]

class LocationSearch(SearchStrategy):
    """Search strategy for finding services by location"""
    
    def search(self, query: str, services: List) -> List:
        """
        Search services by location/address
        
        Args:
            query (str): Location to search for
            services (List): List of services to search through
            
        Returns:
            List: Services matching the location
        """
        if not query:
            return services
        
        query_lower = query.lower()
        return [
            service for service in services 
            if hasattr(service, 'address') and 
            query_lower in service.address.lower()
        ]

class NameSearch(SearchStrategy):
    """Search strategy for finding services by name"""
    
    def search(self, query: str, services: List) -> List:
        """
        Search services by name
        
        Args:
            query (str): Name to search for
            services (List): List of services to search through
            
        Returns:
            List: Services matching the name
        """
        if not query:
            return services
        
        query_lower = query.lower()
        return [
            service for service in services 
            if hasattr(service, 'name') and 
            query_lower in service.name.lower()
        ]

class RatingSearch(SearchStrategy):
    """Search strategy for finding services by minimum rating"""
    
    def search(self, query: str, services: List) -> List:
        """
        Search services by minimum rating
        
        Args:
            query (str): Minimum rating (as string)
            services (List): List of services to search through
            
        Returns:
            List: Services with rating >= minimum
        """
        try:
            min_rating = float(query)
            return [
                service for service in services 
                if hasattr(service, 'rating') and 
                service.rating >= min_rating
            ]
        except ValueError:
            return services

class LocationBasedSearch(SearchStrategy):
    def __init__(self, user_lat: float = None, user_lng: float = None, max_distance_km: float = 10.0):
        self.user_lat = user_lat
        self.user_lng = user_lng
        self.max_distance_km = max_distance_km
    
    def search(self, query: str, services: List) -> List:
        """Search services within a certain distance from user location"""
        if not self.user_lat or not self.user_lng:
            return services
        
        nearby_services = []
        for service in services:
            if service.latitude and service.longitude:
                distance = self.calculate_distance(
                    self.user_lat, self.user_lng,
                    service.latitude, service.longitude
                )
                if distance <= self.max_distance_km:
                    # Add distance to service object for sorting
                    service.distance_from_user = distance
                    nearby_services.append(service)
        
        # Sort by distance (nearest first)
        nearby_services.sort(key=lambda x: x.distance_from_user)
        return nearby_services
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance

class CombinedSearch(SearchStrategy):
    """Search strategy that combines multiple search criteria"""
    
    def __init__(self, strategies: List[SearchStrategy]):
        self.strategies = strategies
    
    def search(self, query: str, services: List) -> List:
        """
        Search using multiple strategies
        
        Args:
            query (str): Search query
            services (List): List of services to search through
            
        Returns:
            List: Services matching any of the strategies
        """
        results = set()
        for strategy in self.strategies:
            strategy_results = strategy.search(query, services)
            results.update(strategy_results)
        
        return list(results)

class SearchService:
    """Service class that uses search strategies"""
    
    def __init__(self, strategy: SearchStrategy = None):
        """
        Initialize search service with a strategy
        
        Args:
            strategy (SearchStrategy): Initial search strategy to use
        """
        self.strategy = strategy or NameSearch()
    
    def set_strategy(self, strategy: SearchStrategy):
        """
        Change the search strategy
        
        Args:
            strategy (SearchStrategy): New strategy to use
        """
        self.strategy = strategy
    
    def execute_search(self, query: str, services: List) -> List:
        """
        Execute search using current strategy
        
        Args:
            query (str): Search query
            services (List): List of services to search through
            
        Returns:
            List: Filtered list of services
        """
        return self.strategy.search(query, services)
    
    def search_by_category(self, category: str, services: List) -> List:
        """
        Search services by category
        
        Args:
            category (str): Category to search for
            services (List): List of services to search through
            
        Returns:
            List: Services in the specified category
        """
        category_strategy = CategorySearch()
        return category_strategy.search(category, services)
    
    def search_by_location(self, location: str, services: List) -> List:
        """
        Search services by location
        
        Args:
            location (str): Location to search for
            services (List): List of services to search through
            
        Returns:
            List: Services in the specified location
        """
        location_strategy = LocationSearch()
        return location_strategy.search(location, services)
    
    def search_by_rating(self, min_rating: float, services: List) -> List:
        """
        Search services by minimum rating
        
        Args:
            min_rating (float): Minimum rating required
            services (List): List of services to search through
            
        Returns:
            List: Services with rating >= minimum
        """
        rating_strategy = RatingSearch()
        return rating_strategy.search(str(min_rating), services)
    
    def advanced_search(self, query: str, services: List, 
                       search_name: bool = True, 
                       search_category: bool = True, 
                       search_location: bool = True) -> List:
        """
        Advanced search using multiple criteria
        
        Args:
            query (str): Search query
            services (List): List of services to search through
            search_name (bool): Whether to search in service names
            search_category (bool): Whether to search in categories
            search_location (bool): Whether to search in locations
            
        Returns:
            List: Services matching any of the enabled criteria
        """
        strategies = []
        
        if search_name:
            strategies.append(NameSearch())
        if search_category:
            strategies.append(CategorySearch())
        if search_location:
            strategies.append(LocationSearch())
        
        combined_strategy = CombinedSearch(strategies)
        return combined_strategy.search(query, services) 