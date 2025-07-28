#!/usr/bin/env python3
"""
ParkBuddy Startup Script
This script helps you start the ParkBuddy application with all necessary components.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print("❌ Redis is not running. Please start Redis first.")
        print("   On Ubuntu/Debian: sudo systemctl start redis-server")
        print("   On macOS: brew services start redis")
        print("   On Windows: Start Redis manually")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_jwt_extended', 
        'flask_caching', 'flask_mail', 'celery', 'redis'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def initialize_database():
    """Initialize the database if it doesn't exist"""
    db_path = Path("parkbuddy.db")
    if not db_path.exists():
        print("🗃️  Initializing database...")
        try:
            # Change to backend directory and run create_db.py
            original_dir = os.getcwd()
            os.chdir('backend')
            subprocess.run([sys.executable, "-c", "from create_db import *"], check=True)
            os.chdir(original_dir)
            print("✅ Database initialized successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to initialize database")
            return False
    else:
        print("✅ Database already exists")
    return True

def start_celery_worker():
    """Start Celery worker in background"""
    print("🔄 Starting Celery worker...")
    try:
        # Start worker in background
        worker_process = subprocess.Popen([
            sys.executable, "-m", "celery", "-A", "backend.app.celery", 
            "worker", "--loglevel=info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(2)
        if worker_process.poll() is None:
            print("✅ Celery worker started successfully")
            return worker_process
        else:
            print("❌ Failed to start Celery worker")
            return None
    except Exception as e:
        print(f"❌ Error starting Celery worker: {e}")
        return None

def start_celery_beat():
    """Start Celery beat for scheduled tasks"""
    print("🔄 Starting Celery beat...")
    try:
        # Start beat in background
        beat_process = subprocess.Popen([
            sys.executable, "-m", "celery", "-A", "backend.app.celery", 
            "beat", "--loglevel=info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(2)
        if beat_process.poll() is None:
            print("✅ Celery beat started successfully")
            return beat_process
        else:
            print("❌ Failed to start Celery beat")
            return None
    except Exception as e:
        print(f"❌ Error starting Celery beat: {e}")
        return None

def start_flask_app():
    """Start the Flask application"""
    print("🚀 Starting ParkBuddy application...")
    print("   Access the application at: http://localhost:5000")
    print("   Admin credentials: admin / ChangeMe123")
    print("   Press Ctrl+C to stop the application")
    
    try:
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")

def main():
    """Main startup function"""
    print("=" * 50)
    print("🚗 ParkBuddy - Vehicle Parking Management System")
    print("=" * 50)
    
    # Check prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_redis():
        sys.exit(1)
    
    if not initialize_database():
        sys.exit(1)
    
    # Start background services
    worker_process = start_celery_worker()
    beat_process = start_celery_beat()
    
    if not worker_process or not beat_process:
        print("⚠️  Some background services failed to start, but continuing...")
    
    print("\n" + "=" * 50)
    print("🎉 ParkBuddy is ready to start!")
    print("=" * 50)
    
    # Start Flask application
    try:
        start_flask_app()
    finally:
        # Cleanup background processes
        if worker_process:
            worker_process.terminate()
            print("🛑 Celery worker stopped")
        if beat_process:
            beat_process.terminate()
            print("🛑 Celery beat stopped")

if __name__ == "__main__":
    main() 