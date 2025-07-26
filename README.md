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

## API Endpoints

### Authentication
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