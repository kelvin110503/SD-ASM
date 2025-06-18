"""
Observer Pattern Implementation for Notification System
Enables real-time notifications about new services and updates
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class Observer(ABC):
    """Abstract base class for observers"""
    
    @abstractmethod
    def update(self, message: str, data: Any = None):
        """
        Update method called when subject notifies observers
        
        Args:
            message (str): Notification message
            data (Any): Additional data (optional)
        """
        pass

class UserObserver(Observer):
    """Observer for user notifications"""
    
    def __init__(self, user_id: int, username: str, email: str):
        """
        Initialize user observer
        
        Args:
            user_id (int): User ID
            username (str): Username
            email (str): Email address
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.notifications = []
    
    def update(self, message: str, data: Any = None):
        """
        Handle notification update
        
        Args:
            message (str): Notification message
            data (Any): Additional data
        """
        notification = {
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow(),
            'read': False
        }
        
        self.notifications.append(notification)
        print(f"Notification for {self.username}: {message}")
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get user notifications
        
        Args:
            unread_only (bool): Whether to return only unread notifications
            
        Returns:
            List: List of notifications
        """
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return self.notifications
    
    def mark_as_read(self, notification_index: int):
        """
        Mark a notification as read
        
        Args:
            notification_index (int): Index of notification to mark as read
        """
        if 0 <= notification_index < len(self.notifications):
            self.notifications[notification_index]['read'] = True
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()

class ServiceObserver(Observer):
    """Observer for service-related notifications"""
    
    def __init__(self, service_id: int, service_name: str):
        """
        Initialize service observer
        
        Args:
            service_id (int): Service ID
            service_name (str): Service name
        """
        self.service_id = service_id
        self.service_name = service_name
        self.updates = []
    
    def update(self, message: str, data: Any = None):
        """
        Handle service update notification
        
        Args:
            message (str): Update message
            data (Any): Additional data
        """
        update = {
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow()
        }
        
        self.updates.append(update)
        print(f"Service update for {self.service_name}: {message}")

class NotificationService:
    """Service for managing notifications and observers"""
    
    def __init__(self):
        """Initialize notification service"""
        self.observers = []
        self.notification_history = []
    
    def add_observer(self, observer: Observer):
        """
        Add an observer to the notification service
        
        Args:
            observer (Observer): Observer to add
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: Observer):
        """
        Remove an observer from the notification service
        
        Args:
            observer (Observer): Observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, message: str, data: Any = None):
        """
        Notify all observers with a message
        
        Args:
            message (str): Message to send to observers
            data (Any): Additional data
        """
        # Record notification in history
        notification_record = {
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow(),
            'observer_count': len(self.observers)
        }
        self.notification_history.append(notification_record)
        
        # Notify all observers
        for observer in self.observers:
            observer.update(message, data)
    
    def notify_new_service(self, service):
        """
        Notify observers about a new service
        
        Args:
            service: Service object
        """
        message = f"New service added: {service.name}"
        data = {
            'service_id': getattr(service, 'id', None),
            'service_name': getattr(service, 'name', ''),
            'category': getattr(service, 'category', ''),
            'address': getattr(service, 'address', '')
        }
        self.notify_observers(message, data)
    
    def notify_service_approved(self, service):
        """
        Notify observers about a service approval
        
        Args:
            service: Service object
        """
        message = f"Service approved: {service.name}"
        data = {
            'service_id': getattr(service, 'id', None),
            'service_name': getattr(service, 'name', ''),
            'status': 'approved'
        }
        self.notify_observers(message, data)
    
    def notify_service_updated(self, service):
        """
        Notify observers about a service update
        
        Args:
            service: Service object
        """
        message = f"Service updated: {service.name}"
        data = {
            'service_id': getattr(service, 'id', None),
            'service_name': getattr(service, 'name', ''),
            'status': 'updated'
        }
        self.notify_observers(message, data)
    
    def notify_new_review(self, review, service):
        """
        Notify observers about a new review
        
        Args:
            review: Review object
            service: Service object
        """
        message = f"New review for {service.name}"
        data = {
            'service_id': getattr(service, 'id', None),
            'service_name': getattr(service, 'name', ''),
            'review_id': getattr(review, 'id', None),
            'rating': getattr(review, 'rating', 0)
        }
        self.notify_observers(message, data)
    
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """
        Get notification history
        
        Returns:
            List: Notification history
        """
        return self.notification_history
    
    def get_observer_count(self) -> int:
        """
        Get number of active observers
        
        Returns:
            int: Number of observers
        """
        return len(self.observers)
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history.clear()

class EmailNotificationObserver(Observer):
    """Observer that sends email notifications"""
    
    def __init__(self, email_service=None):
        """
        Initialize email notification observer
        
        Args:
            email_service: Email service instance (optional)
        """
        self.email_service = email_service
        self.sent_emails = []
    
    def update(self, message: str, data: Any = None):
        """
        Send email notification
        
        Args:
            message (str): Notification message
            data (Any): Additional data
        """
        # In a real implementation, this would send actual emails
        email_record = {
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow(),
            'sent': True
        }
        
        self.sent_emails.append(email_record)
        print(f"Email notification sent: {message}")
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """
        Get list of sent emails
        
        Returns:
            List: Sent email records
        """
        return self.sent_emails

class SMSNotificationObserver(Observer):
    """Observer that sends SMS notifications"""
    
    def __init__(self, sms_service=None):
        """
        Initialize SMS notification observer
        
        Args:
            sms_service: SMS service instance (optional)
        """
        self.sms_service = sms_service
        self.sent_sms = []
    
    def update(self, message: str, data: Any = None):
        """
        Send SMS notification
        
        Args:
            message (str): Notification message
            data (Any): Additional data
        """
        # In a real implementation, this would send actual SMS
        sms_record = {
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow(),
            'sent': True
        }
        
        self.sent_sms.append(sms_record)
        print(f"SMS notification sent: {message}")
    
    def get_sent_sms(self) -> List[Dict[str, Any]]:
        """
        Get list of sent SMS
        
        Returns:
            List: Sent SMS records
        """
        return self.sent_sms 