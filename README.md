# Public Service Locator System

## Project Overview

The Public Service Locator System is a web-based platform designed to bridge the gap between communities and essential public services such as food banks, shelters, clinics, and recycling centres. This system aligns with UN Sustainable Development Goal (SDG) 10 by fostering social inclusion and reducing inequalities.

## Features

### For General Users:
- Search for public services by keyword or category
- Filter results by proximity, availability, or ratings
- View service details (address, hours, contact information)
- Submit reviews and ratings for services
- Visualize services on an interactive map
- Receive notifications about new services

### For Service Providers:
- Register and submit new service listings
- Update existing service information
- Respond to user reviews
- Manage service details

### For System Administrators:
- Approve or reject new service registrations
- Moderate user reviews for appropriateness
- Manage user accounts
- Audit service listings for accuracy

## Design Patterns Implemented

### 1. Factory Pattern
- **Purpose**: Handles instantiation of user types (GeneralUser, ServiceProvider, SystemAdmin)
- **Implementation**: `UserFactory` class creates appropriate user objects based on role

### 2. Singleton Pattern
- **Purpose**: Manages the ServiceRegistry - a centralized component for all public services
- **Implementation**: Ensures only one instance of ServiceRegistry exists throughout the application

### 3. Strategy Pattern
- **Purpose**: Provides interchangeable search strategies (CategorySearch, LocationSearch)
- **Implementation**: Allows dynamic switching between different search algorithms

### 4. Facade Pattern
- **Purpose**: Simplifies interaction with complex subsystems (SearchService, DetailService, MapService)
- **Implementation**: `UserInterfaceFacade` provides a unified interface for frontend operations

### 5. Observer Pattern
- **Purpose**: Enables real-time notifications about new services and updates
- **Implementation**: Users subscribe to updates and receive notifications when services change

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python with Flask
- **Database**: SQLite (for simplicity)
- **Maps**: Leaflet.js for interactive mapping
- **UI Framework**: Bootstrap 5

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step-by-Step Setup Instructions

#### 1. **Download/Clone the Project**
```bash
# Option 1: Download and extract the ZIP file
# Option 2: Clone with Git (if available)
git clone <repository-url>
cd "SD ASM"
```

#### 2. **Create and Activate Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3. **Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt
```

#### 4. **Initialize the Database**
```bash
# The database will be automatically created when you first run the app
# If you need to reset the database, delete the instance/services.db file
```

#### 5. **Run the Application**
```bash
# Start the Flask development server
python app.py
```

#### 6. **Access the Application**
- Open your web browser
- Navigate to: `http://localhost:5000` or `http://127.0.0.1:5000`
- The application should now be running!

### Default Admin Account
After first run, you can create an admin account through the registration page or use these default credentials:
- **Username**: admin
- **Password**: admin123
- **Role**: admin

## Project Structure

```
SD ASM/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── instance/
│   └── services.db       # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   ├── main.js       # Main JavaScript functionality
│   │   ├── map.js        # Map functionality
│   │   └── search.js     # Search functionality
│   └── images/           # Application images
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── search.html       # Service search page
│   ├── service_detail.html # Service details page
│   └── admin.html        # Admin panel
└── models/
    ├── __init__.py
    ├── user.py           # User model and Factory pattern
    ├── service.py        # Service model and Singleton pattern
    ├── search.py         # Search strategies
    ├── facade.py         # Facade pattern implementation
    └── observer.py       # Observer pattern implementation
```

## Usage Guide

### For General Users:
1. Register an account or login
2. Use the search bar to find services by keyword or category
3. Apply filters to narrow down results
4. Click on services to view detailed information
5. Submit reviews and ratings for services you've used
6. View services on the interactive map

### For Service Providers:
1. Register as a service provider
2. Submit new service listings (pending admin approval)
3. Update existing service information
4. Respond to user reviews

### For Administrators:
1. Login with admin credentials
2. Approve or reject pending service registrations
3. Moderate user reviews
4. Manage user accounts
5. Audit service listings

## Troubleshooting

### Common Issues and Solutions

#### 1. **Port Already in Use**
```bash
# Error: "Address already in use"
# Solution: Use a different port
python app.py --port 5001
# Or kill the process using port 5000
```

#### 2. **Module Not Found Errors**
```bash
# Make sure virtual environment is activated
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. **Database Issues**
```bash
# Delete the database file to reset
rm instance/services.db
# Restart the application
```

#### 4. **Permission Errors**
```bash
# On macOS/Linux, you might need to change permissions
chmod +x venv/bin/activate
```

#### 5. **Python Version Issues**
```bash
# Check Python version
python --version

# Should be 3.8 or higher
# If not, install a newer version
```

### Development Tips

#### 1. **Enable Debug Mode**
```python
# In app.py, set debug=True for development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

#### 2. **View Logs**
- Check the terminal where you ran `python app.py`
- Flask will show request logs and errors

#### 3. **Database Browser**
- Use SQLite Browser or similar tool to view `instance/services.db`
- Useful for debugging data issues

## Design Principles Applied

- **Separation of Concerns**: Clear distinction between user roles and features
- **Modularity**: Each module is independently designed
- **Reusability**: Factory and Strategy patterns promote reusable components
- **Encapsulation**: Core logic abstracted in facades and services
- **Single Responsibility Principle**: Each class has a specific role
- **Open/Closed Principle**: New service types or user roles can be added with minimal code change

## Future Enhancements

1. **Real-time Data Integration**: Connect with public agency APIs
2. **Mobile Platform Support**: iOS/Android applications
3. **Enhanced Personalization**: User preferences and recommendation algorithms
4. **Security Enhancements**: Robust data encryption and privacy-preserving techniques
5. **Machine Learning**: Route optimization and user behavior prediction
6. **Advanced Analytics**: Service usage statistics and insights

## Contributing

This is an academic project demonstrating software design patterns and principles. The code is structured to be educational and maintainable.

## License

This project is created for educational purposes as part of CSE6234 Software Design coursework. 