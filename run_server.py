#!/usr/bin/env python3
"""
ParkBuddy Server Runner
Run this file to start the ParkBuddy backend server
"""

import os
import sys
from backend.app import create_app
from backend.extensions import db

def setup_database():
    """Initialize the database with tables and admin user"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        from backend.models import Admin
        admin = Admin.query.filter_by(username='admin').first()
        
        if not admin:
            # Create default admin user
            admin = Admin(username='admin')
            admin.set_password('ChangeMe123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created (username: admin, password: ChangeMe123)")
        else:
            print("✅ Admin user already exists")
            
        print("✅ Database setup complete")

def main():
    """Main function to run the server"""
    print("🚀 Starting ParkBuddy Server...")
    
    # Setup database
    setup_database()
    
    # Create and run the app
    app = create_app()
    
    print("🌐 Server running at: http://localhost:5000")
    print("📱 Open index.html in your browser to access the app")
    print("👤 Admin login: username=admin, password=ChangeMe123")
    print("📝 Create user accounts through the registration endpoint")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()