Public Service Locator System - README

========================================
How to Run (and Compile) the Software
========================================

REQUIREMENTS:
-------------
- Python 3.8 or higher
- pip (Python package manager)
- (Recommended) Virtual environment tool (venv)

DEPENDENCIES:
-------------
All required Python packages are listed in requirements.txt:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- WTForms
- Werkzeug
- SQLAlchemy
- email-validator
- python-dotenv

SETUP INSTRUCTIONS:
-------------------

1. Download or Clone the Project
--------------------------------
- Download and extract the ZIP file, or clone the repository:
    git clone <repository-url>
    cd "SD ASM"

2. Create and Activate a Virtual Environment
--------------------------------------------
- On macOS/Linux:
    python3 -m venv venv
    source venv/bin/activate
- On Windows:
    python -m venv venv
    venv\Scripts\activate

3. Install Dependencies
-----------------------
    pip install -r requirements.txt

4. Initialize the Database
--------------------------
- The database (instance/services.db) is created automatically on first run.
- To reset the database, delete the file: instance/services.db

5. Run the Application
----------------------
    python app.py

6. Access the Application
-------------------------
- Open your web browser and go to:
    http://localhost:5001 or http://localhost:5000

USAGE:
------
- Register as a general user, service provider, or admin.
- General users can search, filter, and review services.
- Providers can add/update services and respond to reviews.
- Admins can approve/reject listings, moderate reviews, and manage users.

TROUBLESHOOTING:
----------------
- If you see "Address already in use", try:
    python app.py --port 5001
- If you get "Module Not Found" errors, ensure your virtual environment is activated and run:
    pip install -r requirements.txt
- To reset the database, delete instance/services.db and restart the app.

NOTES:
------
- Default admin account can be created via registration (choose "admin" as role).
- All data is stored locally in instance/services.db (SQLite).

Enjoy using the Public Service Locator System!

