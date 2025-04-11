from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from models import db, User, bcrypt
from api_routes import api
from roles import Role, admin_required, employee_required
from email_validator import validate_email, EmailNotValidError

def create_app():
    app = Flask(__name__)
    
    # Production configuration
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']  # Required in production
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hr_logs.db')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 10
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Validate input
            errors = []
            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters long')
            if not email:
                errors.append('Email is required')
            else:
                try:
                    validate_email(email)
                except EmailNotValidError:
                    errors.append('Invalid email address')
            if not password or len(password) < 8:
                errors.append('Password must be at least 8 characters long')
            if password != confirm_password:
                errors.append('Passwords do not match')

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                errors.append('Username already exists')
            if User.query.filter_by(email=email).first():
                errors.append('Email already exists')

            if errors:
                for error in errors:
                    flash(error)
                return render_template('register.html')

            # Create new user
            new_user = User(
                username=username,
                email=email,
                role=Role.EMPLOYEE  # Default role is employee
            )
            new_user.password = password  # This will be hashed automatically

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            
            if user and user.verify_password(password):
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('dashboard'))
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
        return render_template('dashboard.html')

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        return render_template('admin_dashboard.html')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role=Role.ADMIN
            )
            admin.password = os.environ['ADMIN_PASSWORD']  # Required in production
            db.session.add(admin)
            db.session.commit()
    
    # Production health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    # Testing endpoints
    @app.route('/test/rollback', methods=['POST'])
    @admin_required
    def test_rollback():
        """Endpoint to test rollback procedures"""
        app.logger.info("Rollback test initiated")
        return {'status': 'rollback test successful'}, 200

    @app.route('/test/load', methods=['POST'])
    @admin_required
    def test_load():
        """Endpoint for load testing"""
        app.logger.info("Load test initiated")
        return {'status': 'load test endpoint ready'}, 200

    @app.route('/test/alert', methods=['POST'])
    @admin_required
    def test_alert():
        """Endpoint to trigger test alerts"""
        app.logger.warning("Test alert triggered")
        return {'status': 'test alert sent'}, 200

    # Configure production logging
    if os.environ.get('FLASK_ENV') != 'development':
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'hr_logs.log'),
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('HR Logs startup')
