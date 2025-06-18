"""
Factory Pattern Implementation for User Creation
Handles instantiation of user types (GeneralUser, ServiceProvider, SystemAdmin)
"""

from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash

class User(ABC):
    """Abstract base class for all user types"""
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.created_at = None
    
    @abstractmethod
    def get_role(self):
        """Return the role of the user"""
        pass
    
    @abstractmethod
    def get_permissions(self):
        """Return the permissions for this user type"""
        pass

class GeneralUser(User):
    """General user who can search, view, and review services"""
    
    def get_role(self):
        return 'general'
    
    def get_permissions(self):
        return [
            'search_services',
            'view_service_details',
            'submit_reviews',
            'view_map'
        ]

class ServiceProvider(User):
    """Service provider who can register and manage services"""
    
    def get_role(self):
        return 'provider'
    
    def get_permissions(self):
        return [
            'search_services',
            'view_service_details',
            'submit_reviews',
            'view_map',
            'register_services',
            'update_services',
            'respond_to_reviews'
        ]

class SystemAdmin(User):
    """System administrator with full access"""
    
    def get_role(self):
        return 'admin'
    
    def get_permissions(self):
        return [
            'search_services',
            'view_service_details',
            'submit_reviews',
            'view_map',
            'register_services',
            'update_services',
            'respond_to_reviews',
            'approve_services',
            'reject_services',
            'moderate_reviews',
            'manage_users',
            'audit_listings'
        ]

class UserFactory:
    """Factory class for creating user objects based on role"""
    
    def create_user(self, role, username, email, password):
        """
        Create a user object based on the specified role
        
        Args:
            role (str): The role of the user ('general', 'provider', 'admin')
            username (str): Username for the account
            email (str): Email address
            password (str): Password for the account
            
        Returns:
            User: Appropriate user object based on role
            
        Raises:
            ValueError: If an invalid role is provided
        """
        if role == 'general':
            return GeneralUser(username, email, password)
        elif role == 'provider':
            return ServiceProvider(username, email, password)
        elif role == 'admin':
            return SystemAdmin(username, email, password)
        else:
            raise ValueError(f"Invalid role type: {role}")
    
    def get_available_roles(self):
        """Return list of available user roles"""
        return ['general', 'provider', 'admin']
    
    def validate_role(self, role):
        """Validate if a role is supported"""
        return role in self.get_available_roles() 