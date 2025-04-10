# Web Dashboard Application

A modern web dashboard application with user authentication, real-time statistics, machine learning capabilities, and a beautiful UI.

![Dashboard Preview](docs/images/dashboard-preview.png)

## Features

- User authentication (login/register)
- Secure password hashing
- Role-based access control
- Real-time statistics and charts
- Machine learning integration
- Screenshot and activity monitoring
- Data synchronization
- Responsive design
- Modern UI with Bootstrap 5
- RESTful API endpoints

## Project Structure

```
├── app/                    # Main application code
│   ├── auth/              # Authentication module
│   ├── models/            # Database models
│   ├── routes/            # API routes
│   └── utils/             # Utility functions
├── data/                   # Data storage and processing
├── docs/                   # Documentation
│   └── images/            # Documentation images
├── logs/                   # Application logs
├── ml/                     # Machine learning models and utilities
│   ├── models/            # Trained models
│   ├── preprocessing/     # Data preprocessing
│   └── training/          # Training scripts
├── models/                 # Data models
├── reports/                # Generated reports
├── scripts/                # Utility scripts
├── templates/              # HTML templates
├── tests/                  # Test suite
│   ├── api/               # API tests
│   ├── ml/                # ML model tests
│   └── unit/              # Unit tests
├── ActiveWindowScreenshots/ # Screenshot storage
├── AppActivityLogs/        # Application activity logs
├── Recordings/             # Screen recordings
├── SynchronizedScreenshots/ # Synchronized screenshots
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── readme.md              # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the `SECRET_KEY` with a secure random string
- Configure other environment variables as needed

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Testing

Run the test suite using pytest:
```bash
pytest tests/
```

Specific test categories:
```bash
# Run API tests
pytest tests/api/

# Run ML model tests
pytest tests/ml/

# Run unit tests
pytest tests/unit/
```

## Deployment

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t web-dashboard .
```

2. Run the container:
```bash
docker run -p 5000:5000 --env-file .env web-dashboard
```

### Cloud Deployment

The application can be deployed on various cloud platforms:

1. **AWS Elastic Beanstalk**
```bash
eb init
eb create
```

2. **Google Cloud Run**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/web-dashboard
gcloud run deploy --image gcr.io/PROJECT_ID/web-dashboard
```

3. **Azure App Service**
```bash
az webapp up --name web-dashboard --resource-group myResourceGroup
```

## Key Technologies

- Flask 3.1.0 - Web framework
- TensorFlow 2.19.0 - Machine learning
- OpenCV 4.11.0 - Image processing
- PyAutoGUI 0.9.54 - Screen monitoring
- SQLAlchemy - Database operations
- Flask-Login - Authentication
- Bootstrap 5 - UI components
- Chart.js - Data visualization
- Pandas 2.2.3 - Data analysis
- Scikit-learn 1.6.1 - Machine learning utilities

## API Documentation

For detailed API documentation, visit our [Swagger UI](http://localhost:5000/api/docs) when running the application locally.

### Authentication
- `POST /login` - User login
  - Request body: `{ "username": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": { "id": "int", "username": "string" } }`
- `POST /register` - User registration
- `GET /logout` - User logout

### User Management
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/<id>` - Get user details
- `PUT /api/users/<id>` - Update user details

### Dashboard
- `GET /dashboard` - Main dashboard
- `GET /api/dashboard/stats` - Dashboard statistics

### Monitoring
- `GET /api/monitoring/screenshots` - Get recent screenshots
- `GET /api/monitoring/activity` - Get activity logs
- `GET /api/monitoring/recordings` - Get screen recordings

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Run `flask db upgrade` to apply migrations

2. **ML Model Loading Errors**
   - Verify model files exist in `ml/models/`
   - Check TensorFlow version compatibility
   - Ensure required dependencies are installed

3. **Authentication Problems**
   - Clear browser cookies
   - Check JWT token expiration
   - Verify user credentials in database

4. **Screen Monitoring Issues**
   - Ensure proper permissions for screen capture
   - Check disk space for screenshot storage
   - Verify OpenCV installation

### Getting Help

- Check the [FAQ](docs/FAQ.md)
- Open an issue on GitHub
- Join our [Discord community](https://discord.gg/your-invite-link)

## Security

- Passwords are hashed using Werkzeug's secure password hashing
- Session management with Flask-Login
- CSRF protection
- Secure headers
- Environment variable configuration
- Secure file storage
- Regular security audits
- Dependency vulnerability scanning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use conventional commits
- Keep dependencies updated

## License

This project is licensed under the MIT License - see the LICENSE file for details.