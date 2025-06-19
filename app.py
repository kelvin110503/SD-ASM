from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json
import math # Import the math module for distance calculations

# Import our design pattern implementations
from models.user import UserFactory, GeneralUser, ServiceProvider, SystemAdmin
from models.service import ServiceRegistry, Service
from models.search import SearchService, CategorySearch, LocationSearch
from models.facade import UserInterfaceFacade
from models.observer import NotificationService, UserObserver

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize design pattern instances
service_registry = ServiceRegistry.get_instance()
notification_service = NotificationService()
user_interface_facade = UserInterfaceFacade(service_registry, notification_service)

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # general, provider, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ServiceModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    hours = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_approved = db.Column(db.Boolean, default=False)
    is_rejected = db.Column(db.Boolean, default=False)
    is_held = db.Column(db.Boolean, default=False)  # New field for hold status
    rejection_reason = db.Column(db.Text)
    hold_reason = db.Column(db.Text)  # New field for hold reason
    held_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who placed the hold
    held_at = db.Column(db.DateTime)  # When the hold was placed
    rejected_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    provider = db.relationship('User', foreign_keys=[provider_id], backref='services')
    hold_admin = db.relationship('User', foreign_keys=[held_by], backref='held_services')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service_model.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    provider_response = db.Column(db.Text)  # New field for provider responses
    response_date = db.Column(db.DateTime)  # When the response was added
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    service = db.relationship('ServiceModel', backref='reviews')
    user = db.relationship('User', backref='reviews')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifications', passive_deletes=True))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role in ['admin', 'provider']:
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Create SQLAlchemy User object (not Factory Pattern object)
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        pending_services = ServiceModel.query.filter_by(is_approved=False, is_rejected=False, is_held=False).all()
        rejected_services = ServiceModel.query.filter_by(is_rejected=True).all()
        held_services = ServiceModel.query.filter_by(is_held=True).all()
        all_services = ServiceModel.query.all()
        service_providers = User.query.filter_by(role='provider').all()
        return render_template('admin.html', pending_services=pending_services, rejected_services=rejected_services, held_services=held_services, all_services=all_services, service_providers=service_providers)
    elif current_user.role == 'provider':
        my_services = ServiceModel.query.filter_by(provider_id=current_user.id).all()
        return render_template('provider_dashboard.html', services=my_services)
    else:
        return render_template('dashboard.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    user_lat = request.args.get('user_lat', type=float)
    user_lon = request.args.get('user_lon', type=float)
    radius = request.args.get('radius', type=float)
    min_rating = request.args.get('min_rating', type=float)
    
    # Determine the base query for services based on user role
    if current_user.is_authenticated and current_user.role in ['admin', 'provider']:
        # Admins and providers can see all services (approved or not, but not held)
        base_services_query = ServiceModel.query.filter_by(is_held=False)
    else:
        # General users (and unauthenticated users) can only see approved services that are not held
        base_services_query = ServiceModel.query.filter_by(is_approved=True, is_held=False)

    # Apply keyword/category search first to the query object
    if query:
        base_services_query = base_services_query.filter(
            (ServiceModel.name.ilike(f'%{query}%')) |
            (ServiceModel.description.ilike(f'%{query}%')) |
            (ServiceModel.address.ilike(f'%{query}%'))
        )
    
    if category:
        base_services_query = base_services_query.filter_by(category=category)

    # Apply minimum rating filter
    if min_rating is not None:
        base_services_query = base_services_query.filter(ServiceModel.rating >= min_rating)

    # Execute the query to get services before applying proximity filter in Python
    services = base_services_query.all()

    # Apply proximity filter if coordinates and radius are provided
    if user_lat is not None and user_lon is not None and radius is not None:
        filtered_services = []
        for service in services:
            if service.latitude is not None and service.longitude is not None:
                distance = haversine_distance(user_lat, user_lon, service.latitude, service.longitude)
                if distance <= radius:
                    filtered_services.append(service)
        services = filtered_services

    # Use Strategy Pattern for search (this part might need re-evaluation if the search logic is now handled above)
    # For now, keeping it as is, but it might be redundant if filtering is done directly
    # if category:
    #     search_strategy = CategorySearch()
    # else:
    #     search_strategy = LocationSearch()
    # search_service = SearchService(search_strategy)
    # services = search_service.execute_search(query, base_services_query.all())
    
    # Convert services to dictionaries for JSON serialization
    services_dict = []
    for service in services:
        services_dict.append({
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'description': service.description,
            'address': service.address,
            'latitude': service.latitude,
            'longitude': service.longitude,
            'rating': service.rating,
            'is_approved': service.is_approved
        })
    
    return render_template('search.html', services=services, services_json=services_dict, query=query, category=category, user_lat=user_lat, user_lon=user_lon, radius=radius, min_rating=min_rating)

@app.route('/service/<int:service_id>')
def service_detail(service_id):
    service = ServiceModel.query.get_or_404(service_id)
    
    # Restrict general users from viewing unapproved services
    if not service.is_approved:
        if current_user.is_authenticated and current_user.role == 'general':
            flash('This service is not yet approved and cannot be viewed by general users.')
            return redirect(url_for('search'))
        elif current_user.is_authenticated and current_user.role == 'provider' and service.provider_id != current_user.id:
            flash('You can only view your own unapproved services.')
            return redirect(url_for('search'))
        elif not current_user.is_authenticated:
            flash('This service is not yet approved.')
            return redirect(url_for('search'))

    reviews = Review.query.filter_by(service_id=service_id).all()
    return render_template('service_detail.html', service=service, reviews=reviews)

@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if current_user.role != 'provider':
        flash('Only service providers can add services')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Validate coordinates
        if not latitude or not longitude:
            flash('Please select a location on the map')
            return redirect(url_for('add_service'))
        
        service = ServiceModel(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form['description'],
            address=request.form['address'],
            phone=request.form['phone'],
            email=request.form['email'],
            hours=request.form['hours'],
            latitude=latitude,
            longitude=longitude,
            provider_id=current_user.id
        )
        
        db.session.add(service)
        db.session.commit()

        # Notify all admins
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            create_notification(
                user_id=admin.id,
                message=f'New service listing submitted: {service.name} by {current_user.username}.',
                url=url_for('service_detail', service_id=service.id)
            )

        flash('Service added successfully! Pending admin approval.')
        return redirect(url_for('dashboard'))
    
    return render_template('add_service.html')

@app.route('/update_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    if current_user.role != 'provider':
        flash('Only service providers can update services')
        return redirect(url_for('dashboard'))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    # Check if the service belongs to the current provider
    if service.provider_id != current_user.id:
        flash('You can only update your own services')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Validate coordinates
        if not latitude or not longitude:
            flash('Please select a location on the map')
            return redirect(url_for('update_service', service_id=service_id))
        
        # Update service data
        service.name = request.form['name']
        service.category = request.form['category']
        service.description = request.form['description']
        service.address = request.form['address']
        service.phone = request.form['phone']
        service.email = request.form['email']
        service.hours = request.form['hours']
        service.latitude = latitude
        service.longitude = longitude
        
        # Clear rejection status since service has been updated
        service.is_rejected = False
        service.rejection_reason = None
        service.rejected_at = None
        
        # Reset approval status since content changed
        service.is_approved = False
        
        db.session.commit()

        # Notify all admins
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            create_notification(
                user_id=admin.id,
                message=f'Service listing updated: {service.name} by {current_user.username}.',
                url=url_for('service_detail', service_id=service.id)
            )

        flash('Service updated successfully! Pending admin approval.')
        return redirect(url_for('service_detail', service_id=service.id))
    
    return render_template('update_service.html', service=service)

@app.route('/add_review/<int:service_id>', methods=['POST'])
@login_required
def add_review(service_id):
    service = ServiceModel.query.get_or_404(service_id)
    
    # Check if user already reviewed this service
    existing_review = Review.query.filter_by(service_id=service_id, user_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this service')
        return redirect(url_for('service_detail', service_id=service_id))
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5)')
        return redirect(url_for('service_detail', service_id=service_id))
    
    review = Review(
        service_id=service_id,
        user_id=current_user.id,
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    
    # Update service rating
    service_reviews = Review.query.filter_by(service_id=service_id).all()
    if service_reviews:
        service.rating = sum(r.rating for r in service_reviews) / len(service_reviews)
    
    db.session.commit()

    # Notify provider - now we can use the review.id since it's been committed
    if service.provider_id:
        create_notification(
            user_id=service.provider_id,
            message=f'You received a new review for {service.name}.',
            url=url_for('service_detail', service_id=service.id, _anchor=f'review-{review.id}')
        )

    flash('Review added successfully!')
    return redirect(url_for('service_detail', service_id=service_id))

@app.route('/respond_to_review/<int:review_id>', methods=['POST'])
@login_required
def respond_to_review(review_id):
    review = Review.query.get_or_404(review_id)
    service = ServiceModel.query.get_or_404(review.service_id)
    
    # Check if current user is the service provider
    if current_user.id != service.provider_id:
        flash('You can only respond to reviews for your own services')
        return redirect(url_for('service_detail', service_id=service.id))
    
    response_text = request.form.get('response', '').strip()
    
    if not response_text:
        flash('Please provide a response')
        return redirect(url_for('service_detail', service_id=service.id))
    
    # Update the review with provider response
    review.provider_response = response_text
    review.response_date = datetime.utcnow()
    
    db.session.commit()

    # Notify review author
    if review.user_id:
        create_notification(
            user_id=review.user_id,
            message=f'Your review for {service.name} received a reply from the provider.',
            url=url_for('service_detail', service_id=service.id, _anchor=f'review-{review.id}')
        )

    flash('Response added successfully!')
    return redirect(url_for('service_detail', service_id=service.id))

@app.route('/edit_response/<int:review_id>', methods=['POST'])
@login_required
def edit_response(review_id):
    review = Review.query.get_or_404(review_id)
    service = ServiceModel.query.get_or_404(review.service_id)
    
    # Check if current user is the service provider
    if current_user.id != service.provider_id:
        flash('You can only edit responses for your own services')
        return redirect(url_for('service_detail', service_id=service.id))
    
    # Check if there's already a response
    if not review.provider_response:
        flash('No response found to edit')
        return redirect(url_for('service_detail', service_id=service.id))
    
    response_text = request.form.get('response', '').strip()
    
    if not response_text:
        flash('Please provide a response')
        return redirect(url_for('service_detail', service_id=service.id))
    
    # Update the review with new response
    review.provider_response = response_text
    review.response_date = datetime.utcnow()  # Update timestamp
    
    db.session.commit()
    flash('Response updated successfully!')
    return redirect(url_for('service_detail', service_id=service.id))

@app.route('/approve_service/<int:service_id>')
@login_required
def approve_service(service_id):
    if current_user.role != 'admin':
        flash('Only administrators can approve services')
        return redirect(url_for('dashboard'))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    # Check if service was previously rejected and hasn't been updated
    if service.is_rejected:
        flash('Cannot approve a rejected service directly. The service provider must update it first.')
        return redirect(url_for('service_detail', service_id=service_id))
    
    service.is_approved = True
    service.is_rejected = False
    service.rejection_reason = None
    service.rejected_at = None
    db.session.commit()

    # Notify provider
    if service.provider_id:
        create_notification(
            user_id=service.provider_id,
            message=f'Your service "{service.name}" has been approved and is now live.',
            url=url_for('service_detail', service_id=service.id, _anchor='service-details')
        )

    flash(f'Service "{service.name}" has been approved and is now live!')
    return redirect(url_for('service_detail', service_id=service_id))

@app.route('/reject_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def reject_service(service_id):
    if current_user.role != 'admin':
        flash('Only administrators can reject services')
        return redirect(url_for('dashboard'))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    if request.method == 'POST':
        rejection_reason = request.form.get('rejection_reason', 'No reason provided')
        
        # Mark service as rejected instead of deleting
        service.is_approved = False
        service.is_rejected = True
        service.rejection_reason = rejection_reason
        service.rejected_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notify provider
        if service.provider_id:
            create_notification(
                user_id=service.provider_id,
                message=f'Your service "{service.name}" was rejected. Reason: {service.rejection_reason}',
                url=url_for('service_detail', service_id=service.id, _anchor='rejection-notice')
            )

        flash(f'Service "{service.name}" has been rejected.')
        return redirect(url_for('service_detail', service_id=service_id))
    
    return render_template('reject_service.html', service=service)

@app.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role != 'admin':
        flash('Only administrators can delete services.')
        return redirect(url_for('dashboard'))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    # Delete associated reviews first
    Review.query.filter_by(service_id=service_id).delete()
    
    # Delete the service
    db.session.delete(service)
    db.session.commit()
    
    flash(f'Service "{service.name}" has been deleted successfully.')
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Only administrators can delete users')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account')
        return redirect(url_for('dashboard'))
    
    # Delete all services associated with this user
    services = ServiceModel.query.filter_by(provider_id=user.id).all()
    for service in services:
        db.session.delete(service)
    
    # Delete all reviews by this user
    reviews = Review.query.filter_by(user_id=user.id).all()
    for review in reviews:
        db.session.delete(review)
    
    # Delete all notifications for this user
    Notification.query.filter_by(user_id=user.id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{user.username}" and all associated data have been deleted')
    return redirect(url_for('dashboard'))

@app.route('/hold_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def hold_service(service_id):
    if current_user.role != 'admin':
        flash('Only administrators can hold services')
        return redirect(url_for('service_detail', service_id=service_id))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    if request.method == 'POST':
        hold_reason = request.form.get('hold_reason', '').strip()
        additional_details = request.form.get('additional_details', '').strip()
        
        if not hold_reason:
            flash('Please provide a reason for holding this service')
            return redirect(url_for('hold_service', service_id=service_id))
        
        # Combine reason and additional details
        full_reason = hold_reason
        if additional_details:
            full_reason += f" - {additional_details}"
        
        # Place the service on hold
        service.is_held = True
        service.hold_reason = full_reason
        service.held_by = current_user.id
        service.held_at = datetime.utcnow()
        
        db.session.commit()

        # Notify provider
        if service.provider_id:
            create_notification(
                user_id=service.provider_id,
                message=f'Your service "{service.name}" has been placed on hold. Reason: {service.hold_reason}',
                url=url_for('service_detail', service_id=service.id, _anchor='hold-notice')
            )

        flash(f'Service "{service.name}" has been placed on hold. Reason: {full_reason}')
        return redirect(url_for('service_detail', service_id=service_id))
    
    return render_template('hold_service.html', service=service)

@app.route('/unhold_service/<int:service_id>')
@login_required
def unhold_service(service_id):
    if current_user.role != 'admin':
        flash('Only administrators can remove holds from services')
        return redirect(url_for('service_detail', service_id=service_id))
    
    service = ServiceModel.query.get_or_404(service_id)
    
    if not service.is_held:
        flash('This service is not currently on hold')
        return redirect(url_for('service_detail', service_id=service_id))
    
    # Remove the hold
    service.is_held = False
    service.hold_reason = None
    service.held_by = None
    service.held_at = None
    
    db.session.commit()

    # Notify provider
    if service.provider_id:
        create_notification(
            user_id=service.provider_id,
            message=f'Your service "{service.name}" is no longer on hold and is available to users.',
            url=url_for('service_detail', service_id=service.id, _anchor='service-details')
        )

    flash(f'Service "{service.name}" has been removed from hold and is now available.')
    return redirect(url_for('service_detail', service_id=service_id))

@app.route('/api/services')
def api_services():
    services = ServiceModel.query.filter_by(is_approved=True).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'category': s.category,
        'address': s.address,
        'latitude': s.latitude,
        'longitude': s.longitude,
        'rating': s.rating
    } for s in services])

@app.route('/search_nearby')
def search_nearby():
    """Search for services near a specific location"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    max_distance = request.args.get('max_distance', 10.0, type=float)
    
    if not lat or not lng:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    # Use LocationBasedSearch strategy
    from .search import LocationBasedSearch
    search_strategy = LocationBasedSearch(lat, lng, max_distance)
    search_service = SearchService(search_strategy)
    
    services = search_service.execute_search("", ServiceModel.query.filter_by(is_approved=True).all())
    
    # Convert to JSON-serializable format
    services_data = []
    for service in services:
        service_data = {
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'description': service.description,
            'address': service.address,
            'latitude': service.latitude,
            'longitude': service.longitude,
            'rating': service.rating,
            'distance': getattr(service, 'distance_from_user', None)
        }
        services_data.append(service_data)
    
    return jsonify({
        'services': services_data,
        'user_location': {'lat': lat, 'lng': lng},
        'max_distance': max_distance
    })

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def create_notification(user_id, message, url=None):
    notification = Notification(user_id=user_id, message=message, url=url)
    db.session.add(notification)
    db.session.commit()

@app.route('/notifications')
@login_required
def notifications():
    # Mark all as read
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=current_user.notifications)

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        notifications = sorted(current_user.notifications, key=lambda n: n.created_at, reverse=True)[:10]
    else:
        notifications = []
    return dict(top_notifications=notifications)

@app.route('/notification/<int:notification_id>/mark_read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notification/<int:notification_id>/mark_unread', methods=['POST'])
@login_required
def mark_notification_unread(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    notification.is_read = False
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notification/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notifications/clear', methods=['POST'])
@login_required
def clear_notifications():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Add sample services if none exist
        if not ServiceModel.query.first():
            sample_services = [
                {
                    'name': 'Community Food Bank Malaysia',
                    'category': 'food bank',
                    'description': 'Providing food assistance to families in need across Malaysia',
                    'address': '123 Jalan Tun Razak, Kuala Lumpur, Malaysia',
                    'latitude': 3.1390,
                    'longitude': 101.6869,
                    'phone': '+60 3-1234 5678',
                    'email': 'foodbank@community.my',
                    'hours': 'Mon-Fri 9AM-5PM, Sat 10AM-2PM',
                    'is_approved': True
                },
                {
                    'name': 'Hope Shelter KL',
                    'category': 'shelter',
                    'description': 'Emergency shelter for homeless individuals in Kuala Lumpur',
                    'address': '456 Jalan Bukit Bintang, Kuala Lumpur, Malaysia',
                    'latitude': 3.1426,
                    'longitude': 101.7074,
                    'phone': '+60 3-1234 5679',
                    'email': 'hope@shelter.my',
                    'hours': '24/7',
                    'is_approved': True
                },
                {
                    'name': 'Health First Clinic Malaysia',
                    'category': 'clinic',
                    'description': 'Free medical consultations for low-income families',
                    'address': '789 Jalan Petaling, Kuala Lumpur, Malaysia',
                    'latitude': 3.1439,
                    'longitude': 101.6988,
                    'phone': '+60 3-1234 5680',
                    'email': 'health@clinic.my',
                    'hours': 'Mon-Sat 8AM-6PM',
                    'is_approved': True
                },
                {
                    'name': 'Green Earth Recycling Malaysia',
                    'category': 'recycling center',
                    'description': 'Recycling center for paper, plastic, and electronics',
                    'address': '321 Jalan Ampang, Kuala Lumpur, Malaysia',
                    'latitude': 3.1589,
                    'longitude': 101.7144,
                    'phone': '+60 3-1234 5681',
                    'email': 'green@recycling.my',
                    'hours': 'Mon-Fri 8AM-8PM, Sat-Sun 9AM-5PM',
                    'is_approved': True
                },
                {
                    'name': 'Skills Development Center Malaysia',
                    'category': 'education',
                    'description': 'Free skills training and education programs',
                    'address': '654 Jalan Sultan, Kuala Lumpur, Malaysia',
                    'latitude': 3.1457,
                    'longitude': 101.6942,
                    'phone': '+60 3-1234 5682',
                    'email': 'skills@education.my',
                    'hours': 'Mon-Fri 9AM-7PM, Sat 9AM-3PM',
                    'is_approved': True
                }
            ]
            
            for service_data in sample_services:
                service = ServiceModel(**service_data)
                db.session.add(service)
            
            db.session.commit()
            print("Sample services added to database")
    
    app.run(debug=True, port=5001) 