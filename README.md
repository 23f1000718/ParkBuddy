<<<<<<< HEAD
# ParkBuddy

ParkBuddy is a smart parking management system that helps users find and reserve parking spots while allowing administrators to manage parking lots efficiently.

## Features

### User Features
- View available parking lots
- Reserve parking spots
- View reservation history
- Real-time spot availability

### Admin Features
- Manage parking lots (create, delete)
- View all parking lots
- Monitor system usage

## Setup Instructions

### Prerequisites
- Python 3.7+
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ParkBuddy
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-jwt-extended werkzeug
   ```

3. **Run the server**
   ```bash
   python run_server.py
   ```

4. **Open the application**
   - Open `index.html` in your web browser
   - Or visit `http://localhost:5000` and navigate to the static files

## Usage

### Admin Login
- **Username:** admin
- **Password:** ChangeMe123

### User Registration
Users need to register first using the API endpoint:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'
```
=======
# ParkBuddy - Vehicle Parking Management System

A comprehensive multi-user vehicle parking management application built with Flask, Vue.js, and Bootstrap.

## Features

### Core Functionalities
- **Multi-User System**: Separate interfaces for Admin and Regular Users
- **Parking Lot Management**: Create, edit, and delete parking lots with configurable spots
- **Smart Spot Allocation**: Automatic spot assignment based on availability
- **Real-time Status Tracking**: Monitor parking spot availability and occupancy
- **Cost Calculation**: Automatic billing based on parking duration
- **User Registration & Authentication**: Secure JWT-based authentication system

### Admin Features
- **Dashboard Analytics**: Comprehensive statistics and charts
- **Parking Lot Management**: Full CRUD operations for parking lots
- **User Management**: View and manage registered users
- **Spot Monitoring**: Real-time view of all parking spots and their status
- **Revenue Tracking**: Daily revenue and utilization statistics

### User Features
- **Parking Reservation**: Book available parking spots
- **Active Reservations**: View and manage current parking sessions
- **Parking History**: Complete history of all parking activities
- **Statistics Dashboard**: Personal parking analytics and charts
- **CSV Export**: Download parking history as CSV file

### Background Jobs
- **Daily Reminders**: Automated email reminders for inactive users
- **Monthly Reports**: Comprehensive activity reports sent via email
- **CSV Export**: Asynchronous CSV generation and email delivery

### Performance & Caching
- **Redis Caching**: Improved API performance with intelligent caching
- **Background Processing**: Celery-based task queue for heavy operations
- **Optimized Queries**: Efficient database queries with proper indexing

## Technology Stack

### Backend
- **Flask**: Web framework for API development
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (as per requirements)
- **Redis**: Caching and message broker
- **Celery**: Background task processing
- **JWT**: Token-based authentication
- **Flask-Mail**: Email functionality

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Bootstrap 5**: CSS framework for responsive design
- **Chart.js**: Data visualization
- **Bootstrap Icons**: Icon library

## Installation & Setup

### Prerequisites
- Python 3.8+
- Redis Server
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ParkBuddy
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Redis
Make sure Redis server is running on your system:
```bash
# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# On macOS
brew install redis
brew services start redis

# On Windows
# Download and install Redis from https://redis.io/download
```

### Step 5: Initialize Database
```bash
cd backend
python create_db.py
```

### Step 6: Configure Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/0
```

### Step 7: Start the Application

#### Start Flask Application
```bash
python run.py
```

#### Start Celery Worker (in a separate terminal)
```bash
celery -A celery_worker.celery worker --loglevel=info
```

#### Start Celery Beat (for scheduled tasks)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Usage

### Accessing the Application
1. Open your browser and navigate to `http://localhost:5000`
2. You'll see the ParkBuddy landing page with login/register options

### Admin Access
- **Username**: `admin`
- **Password**: `ChangeMe123` (as set in create_db.py)
- **Note**: Change the admin password after first login for security

### User Registration
1. Click on "Register" tab on the landing page
2. Fill in your details (Full Name, Email, Password)
3. Click "Register" to create your account
4. Login with your credentials

### Admin Dashboard
- **Parking Lot Management**: Create, edit, and delete parking lots
- **User Management**: View all registered users
- **Statistics**: Monitor system usage and revenue
- **Spot Monitoring**: Real-time view of parking spot status

### User Dashboard
- **Available Lots**: View and reserve parking spots
- **Active Reservations**: Manage current parking sessions
- **Parking History**: View complete parking history
- **Statistics**: Personal parking analytics
- **CSV Export**: Download parking history
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)

## API Endpoints

### Authentication
<<<<<<< HEAD
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/admin/login` - Admin login

### Common
- `GET /api/lots` - Get all parking lots (requires authentication)

### Admin Only
- `POST /api/admin/lots` - Create new parking lot
- `DELETE /api/admin/lots/<id>` - Delete parking lot

### User Only
- `POST /api/user/reserve/<lot_id>` - Reserve a spot
- `POST /api/user/release/<reservation_id>` - Release a spot
- `GET /api/user/reservations` - Get user's reservations

## Project Structure

```
ParkBuddy/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions
│   ├── models.py           # Database models
│   ├── routes/
│   │   ├── admin.py        # Admin routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── common.py       # Common routes
│   │   ├── user.py         # User routes
│   │   └── decorators.py   # Route decorators
│   ├── static/js/
│   │   ├── admin.html      # Admin dashboard
│   │   └── user.html       # User dashboard
│   └── templates/          # HTML templates (legacy)
├── index.html              # Main application entry point
├── run_server.py           # Server runner script
└── README.md
```

## Database Schema

- **Users**: User accounts and authentication
- **Admins**: Administrator accounts
- **ParkingLots**: Parking lot information
- **ParkingSpots**: Individual parking spots
- **Reservations**: User reservations and history

## Troubleshooting

1. **Server won't start**: Make sure all dependencies are installed
2. **Login fails**: Check that the server is running on port 5000
3. **Database errors**: Delete `parkbuddy.db` and restart the server
4. **CORS issues**: Make sure you're accessing the app through the correct URL

## Development Notes

This is a milestone 5 implementation with basic functionality. The system includes:
- JWT-based authentication
- Role-based access control
- RESTful API design
- Simple Vue.js frontend
- SQLite database storage

Future improvements could include:
- Real-time updates using WebSockets
- Payment integration
- Mobile app
- Advanced reporting and analytics
=======
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/admin/login` - Admin login

### Admin Endpoints
- `GET /api/admin/dashboard-stats` - Dashboard statistics
- `GET /api/admin/users` - List all users
- `GET /api/admin/lot-details/<id>` - Parking lot details
- `POST /api/lots` - Create parking lot
- `PUT /api/admin/edit-lot/<id>` - Edit parking lot
- `DELETE /api/lots/<id>` - Delete parking lot

### User Endpoints
- `GET /api/user/stats` - User statistics
- `GET /api/user/reservations` - Parking history
- `GET /api/user/active-reservations` - Active reservations
- `POST /api/user/reserve/<lot_id>` - Reserve parking spot
- `POST /api/user/release/<reservation_id>` - Release parking spot
- `POST /api/user/export-csv` - Trigger CSV export

### Common Endpoints
- `GET /api/lots` - List all parking lots

## Background Jobs

### Scheduled Tasks
- **Daily Reminders**: Sent every evening to inactive users
- **Monthly Reports**: Generated and sent on the 1st of each month

### User-Triggered Tasks
- **CSV Export**: Generated asynchronously when requested

## Database Schema

### Tables
- **users**: User accounts and information
- **admins**: Admin accounts
- **parking_lots**: Parking lot information
- **parking_spots**: Individual parking spots
- **reservations**: Parking reservations and billing

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt-based password security
- **Role-Based Access**: Separate admin and user permissions
- **Input Validation**: Comprehensive form validation
- **SQL Injection Protection**: ORM-based query protection

## Performance Optimizations

- **Redis Caching**: API response caching
- **Database Indexing**: Optimized query performance
- **Background Processing**: Heavy operations moved to background
- **Lazy Loading**: Efficient data loading strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.

---

**ParkBuddy** - Making parking management simple and efficient! 🚗💨
>>>>>>> fa507b6 (Amped up UI and milestone 6 implemented)
