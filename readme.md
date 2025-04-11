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
- RESTful API endpoints with FastAPI
- OpenAPI/Swagger documentation
- Async request handling
- High-performance data processing

## Project Structure

```
├── app/                    # Main application code
│   ├── core/              # Core application logic
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
├── reports/               # Generated reports
├── scripts/               # Utility scripts
├── tests/                 # Test suite
│   ├── api/              # API tests
│   ├── ml/               # ML model tests
│   └── unit/             # Unit tests
├── alembic/              # Database migrations
├── ActiveWindowScreenshots/ # Screenshot storage
├── AppActivityLogs/        # Application activity logs
├── Recordings/            # Screen recordings
├── SynchronizedScreenshots/ # Synchronized screenshots
├── .env                   # Environment variables
├── alembic.ini           # Alembic configuration
├── requirements.txt       # Python dependencies
└── readme.md             # Project documentation
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

4. Initialize and apply database migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app:app --reload
```

The application will be available at `http://localhost:8000`

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
docker run -p 8000:8000 --env-file .env web-dashboard
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

- FastAPI 0.104.1 - Modern, fast web framework
- TensorFlow 2.14.0 - Machine learning
- OpenCV 4.8.0 - Image processing
- SQLAlchemy 2.0.20 - Database operations
- Pydantic 2.5.2 - Data validation
- Alembic 1.15.2 - Database migrations
- Uvicorn 0.24.0 - ASGI server
- Bootstrap 5 - UI components
- Chart.js - Data visualization
- Pandas 2.0.3 - Data analysis
- Scikit-learn 1.3.0 - Machine learning utilities

## API Documentation

FastAPI automatically generates interactive API documentation. When running the application locally, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Authentication
- `POST /api/v1/login` - User login
  - Request body: `{ "username": "string", "password": "string" }`
  - Response: `{ "token": "string", "user": { "id": "int", "username": "string" } }`
- `POST /api/v1/register` - User registration
- `GET /api/v1/logout` - User logout

### User Management
- `GET /api/v1/users` - Get all users (admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user details

### Dashboard
- `GET /api/v1/dashboard` - Main dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistics

### Monitoring
- `GET /api/v1/monitoring/screenshots` - Get recent screenshots
- `GET /api/v1/monitoring/activity` - Get activity logs
- `GET /api/v1/monitoring/recordings` - Get screen recordings

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Run `alembic upgrade head` to apply migrations

2. **ML Model Loading Errors**
   - Verify model files exist in `ml/models/`
   - Check TensorFlow version compatibility
   - Ensure required dependencies are installed

3. **Authentication Problems**
   - Check JWT token expiration
   - Verify user credentials in database
   - Ensure proper CORS configuration

4. **Screen Monitoring Issues**
   - Ensure proper permissions for screen capture
   - Check disk space for screenshot storage
   - Verify OpenCV installation

### Getting Help

- Check the [FAQ](docs/FAQ.md)
- Open an issue on GitHub
- Join our [Discord community](https://discord.gg/your-invite-link)

## Security

- Passwords are hashed using bcrypt
- JWT-based authentication
- CORS protection
- Rate limiting
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

# Activity Tracker Module

This module captures keyboard and mouse events with accurate timestamps for HR analytics purposes.

## Features

- Captures keyboard press and release events
- Captures mouse movement and click events
- Thread-safe event storage
- JSON export functionality
- Real-time event tracking

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from activity_tracker import ActivityTracker

# Create an instance of the tracker
tracker = ActivityTracker()

# Start tracking
tracker.start()

# ... perform activities ...

# Get current events
events = tracker.get_events()

# Save events to a file
tracker.save_events('activity_log.json')

# Stop tracking
tracker.stop()
```

## Event Data Structure

### Keyboard Events
```json
{
    "type": "key_press" | "key_release",
    "key": "character or key name",
    "timestamp": "ISO 8601 timestamp"
}
```

### Mouse Events
```json
{
    "type": "mouse_move" | "mouse_click",
    "x": "x-coordinate",
    "y": "y-coordinate",
    "button": "button name (for clicks)",
    "pressed": "boolean (for clicks)",
    "timestamp": "ISO 8601 timestamp"
}
```

## Security and Privacy

- All data is stored locally
- No data is transmitted to external servers
- Events can be cleared using the `clear_events()` method
- Data is stored in a thread-safe manner

## License

MIT License

# Data Integration Engine

This module provides a unified interface for collecting, processing, and correlating multimodal data from various sources.

## Features

- Unified data collection from multiple sources
- Time-synchronized data storage
- Data correlation and analysis
- Comprehensive reporting
- Thread-safe operations
- Flexible data processing pipeline

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Data Integration Engine

```python
from data_integration import DataIntegrationEngine

# Initialize the engine
engine = DataIntegrationEngine()

# Add data points
engine.add_data_point(
    source="activity_tracker",
    data_type="keyboard_event",
    data={
        "key": "a",
        "action": "press"
    },
    metadata={
        "user_id": "user123",
        "application": "text_editor"
    }
)

# Get filtered data points
points = engine.get_data_points(
    source="activity_tracker",
    start_time="2024-01-01T00:00:00",
    end_time="2024-01-01T01:00:00"
)

# Export data
engine.export_data("exported_data.json")
```

### Data Processor

```python
from data_processor import DataProcessor
from datetime import timedelta

# Initialize processor with engine
processor = DataProcessor(engine)

# Process time series data
time_series = processor.process_time_series(
    source="activity_tracker",
    data_type="keyboard_event"
)

# Correlate data between sources
correlation = processor.correlate_sources(
    source1="activity_tracker",
    source2="webcam",
    time_window=timedelta(seconds=1)
)

# Generate comprehensive report
report = processor.generate_report(
    sources=["activity_tracker", "webcam"],
    start_time="2024-01-01T00:00:00",
    end_time="2024-01-01T01:00:00"
)
```

## Data Structure

### DataPoint
```python
@dataclass
class DataPoint:
    source: str          # Source identifier
    type: str           # Data type
    data: Dict[str, Any] # Actual data
    timestamp: str      # ISO 8601 timestamp
    metadata: Optional[Dict[str, Any]] = None
```

### CorrelationResult
```python
@dataclass
class CorrelationResult:
    source1: str
    source2: str
    correlation_score: float
    time_window: timedelta
    metadata: Optional[Dict[str, Any]] = None
```

## Storage Structure

```
integrated_data/
├── raw/               # Raw data storage
│   └── YYYY-MM-DD/   # Daily directories
│       └── source_type_timestamp.json
└── processed/        # Processed data storage
    └── reports/      # Generated reports
```

## Security and Privacy

- All data is stored locally
- Thread-safe operations
- No data transmission to external servers
- Flexible metadata for privacy controls
- Configurable data retention

## License

MIT License

# Documentation Generator

A comprehensive documentation generator for creating and maintaining project documentation, including user guides, API documentation, and troubleshooting guides.

## Features

- Generate user guides with customizable sections
- Create API documentation with OpenAPI specification
- Generate troubleshooting guides
- Automatic version tracking
- Markdown and YAML support
- Structured documentation hierarchy

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from docs_generator import DocumentationGenerator

# Initialize the generator
generator = DocumentationGenerator()

# Generate a user guide
generator.generate_user_guide(
    title="Getting Started",
    sections=[
        {"title": "Installation", "content": "Installation instructions..."},
        {"title": "Configuration", "content": "Configuration steps..."}
    ]
)

# Generate API documentation
generator.generate_api_docs(
    title="Data API",
    version="1.0",
    endpoints=[
        {
            "path": "/api/v1/data",
            "method": "GET",
            "description": "Retrieve data",
            "parameters": [
                {"name": "id", "type": "string", "required": True}
            ]
        }
    ]
)

# Generate a troubleshooting guide
generator.generate_troubleshooting_guide(
    title="Common Issues",
    issues=[
        {
            "title": "Connection Error",
            "symptoms": ["Cannot connect to server", "Timeout errors"],
            "solution": "Check network connection and server status"
        }
    ]
)
```

## Documentation Structure

The generator creates the following directory structure:

```
docs/
├── user_guides/          # User guides and tutorials
├── api/                  # API documentation
│   └── v1.0/            # Versioned API docs
├── troubleshooting/      # Troubleshooting guides
├── images/              # Documentation images
└── templates/           # Documentation templates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.