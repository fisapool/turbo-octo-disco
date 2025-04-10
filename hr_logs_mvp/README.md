# HR Logs System MVP

A simple HR logging system for tracking employee activities, attendance, and other HR-related information.

## Features

- User authentication
- Dashboard for viewing logs
- Create new HR logs
- Track log status (pending, approved, rejected)
- Different log types (attendance, leave, performance, etc.)
- Admin dashboard with comprehensive management tools
- Real-time system health monitoring

## Requirements

- Python 3.8 or higher
- SQLite3
- Modern web browser

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the application at `http://localhost:5000`

## API Documentation

### Authentication Endpoints

- `POST /login` - User login
  - Request body: `{ "username": "string", "password": "string" }`
  - Response: `{ "message": "Login successful", "user": { "id": int, "username": "string", "role": "string" } }`

- `POST /register` - User registration
  - Request body: `{ "username": "string", "email": "string", "password": "string", "confirm_password": "string" }`
  - Response: `{ "message": "Registration successful", "user": { "id": int, "username": "string" } }`

- `GET /logout` - User logout
  - Response: `{ "message": "Logout successful" }`

### Log Management Endpoints

- `GET /api/logs` - Get all logs (admin) or user's logs
  - Response: `[{ "id": int, "log_type": "string", "description": "string", "status": "string", "timestamp": "datetime" }]`

- `POST /api/logs` - Create a new log
  - Request body: `{ "log_type": "string", "description": "string" }`
  - Response: `{ "id": int, "log_type": "string", "description": "string", "status": "pending", "timestamp": "datetime" }`

- `PUT /api/logs/<id>` - Update a log
  - Request body: `{ "description": "string" }` or `{ "status": "string", "admin_notes": "string" }` (admin only)
  - Response: Updated log object

- `DELETE /api/logs/<id>` - Delete a log
  - Response: `{ "message": "Log deleted successfully" }`

### Admin Endpoints

- `GET /api/admin/statistics` - Get system statistics
  - Response: `{ "total_users": int, "active_logs": int, "pending_approvals": int, "system_health": float }`

- `GET /api/admin/users` - Get all users
  - Response: `[{ "id": int, "username": "string", "email": "string", "role": "string", "last_login": "datetime" }]`

- `PUT /api/admin/users/<id>` - Update user details
  - Request body: `{ "username": "string", "email": "string", "role": "string" }`
  - Response: Updated user object

- `DELETE /api/admin/users/<id>` - Delete a user
  - Response: `{ "message": "User deleted successfully" }`

- `GET /api/admin/logs` - Get all logs with user details
  - Response: `[{ "id": int, "username": "string", "log_type": "string", "description": "string", "status": "string", "timestamp": "datetime", "admin_notes": "string" }]`

- `PUT /api/admin/logs/<id>` - Update log status and admin notes
  - Request body: `{ "status": "string", "admin_notes": "string" }`
  - Response: Updated log object

- `GET /api/admin/system-health` - Get system health metrics
  - Response: `{ "db_status": int, "system_resources": float }`

## User Roles and Permissions

The system implements role-based access control with the following roles:

### Admin
- Full access to all features
- Can manage users (create, update, delete)
- Can view and manage all logs
- Can update log statuses and add admin notes
- Access to system statistics and health monitoring

### Employee
- Can create and manage their own logs
- Can view their own logs
- Limited access to system features

### Manager
- Can view and manage logs for their team
- Can approve/reject logs
- Access to team statistics

## Log Status Workflow

Logs follow a defined workflow:
1. Created (Initial state: "pending")
2. Under Review (Status: "in_review")
3. Final State: "approved" or "rejected"
4. Optional: "archived" for old logs

Each status change requires appropriate permissions and is logged with timestamp and user information.

## Machine Learning Components

The system includes ML components for:

### Log Analysis
- Automated categorization of log entries
- Sentiment analysis for performance reviews
- Pattern detection for attendance anomalies

### Future ML Features
- Predictive analytics for HR trends
- Automated log status recommendations
- Employee performance predictions

## Security Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
SECRET_KEY=your-secure-secret-key
FLASK_ENV=development
DATABASE_URL=sqlite:///hr_logs.db
```

### SECRET_KEY Requirements
- Minimum length: 32 characters
- Should be randomly generated using cryptographically secure methods
- Never commit to version control
- Different for each environment (development, staging, production)
- Can be generated using: `python -c "import secrets; print(secrets.token_hex(32))"`

### Production Security Measures
- Enable HTTPS/SSL
- Implement rate limiting
- Set secure headers
- Regular security audits
- Monitor for suspicious activities
- Backup data regularly

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Admin Panel
![Admin Panel](screenshots/admin_panel.png)

### Log Creation
![Log Creation](screenshots/log_creation.png)

## Testing

The application includes unit tests and integration tests. To run the tests:

```bash
python -m pytest tests/
```

### Test Structure

- `tests/test_auth.py` - Authentication tests
- `tests/test_logs.py` - Log management tests
- `tests/test_admin.py` - Admin functionality tests
- `tests/test_api.py` - API endpoint tests

## Database

The application uses SQLite by default. The database file (`hr_logs.db`) will be created automatically when you first run the application.

## Deployment

### Local Development

1. Follow the setup instructions above
2. Set environment variables:
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
```

### Production Deployment

1. Set up a production-ready web server (e.g., Gunicorn with Nginx)
2. Configure environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=your-database-url
```

3. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t hr-logs-mvp .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key hr-logs-mvp
```

## Security Notes

- This is a beta version and should not be used in production without additional security measures
- Passwords are stored in plain text (for MVP only) - implement proper password hashing for production
- Set a proper SECRET_KEY in production environment
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Regular security audits recommended

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License 