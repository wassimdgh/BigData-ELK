from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flasgger import Swagger

# Charger les variables d'environnement
load_dotenv()

def create_app():
    """Factory pour créer l'application Flask"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True') == 'True'
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 100000000))
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days
    
    # Session configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_NAME'] = 'session'
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow localhost
    app.config['REMEMBER_COOKIE_DURATION'] = 86400 * 7  # 7 days
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    
    # CORS - Allow credentials
    CORS(app, supports_credentials=True)
    
    # Connexions aux bases de données
    from app.services.database import init_databases
    init_databases(app)

    # Swagger / Flasgger initialization
    swagger_template = {
        'swagger': '2.0',
        'info': {
            'title': 'IoT Smart Building API',
            'description': 'Endpoints for logs, stats, files, and cache',
            'version': '1.0.0'
        },
        'schemes': ['http'],
        'basePath': '/',
        'tags': [
            {'name': 'Logs', 'description': 'Logs retrieval and details'},
            {'name': 'Stats', 'description': 'Global and dashboard statistics'},
            {'name': 'Files', 'description': 'Uploaded files listing'},
            {'name': 'Cache', 'description': 'Redis cache operations'}
        ]
    }
    swagger_config = {
        'headers': [],
        'specs': [
            {
                'endpoint': 'v1_spec',
                'route': '/api/v1/swagger.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/apidocs'
    }
    Swagger(app, template=swagger_template, config=swagger_config)
    
    # Flask-Login initialization
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        import logging
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f'🔍 Loading user with ID: {user_id}')
            user = User.find_by_id(user_id)
            if user:
                logger.debug(f'✅ User loaded: {user.username}')
            else:
                logger.warning(f'⚠️ User not found for ID: {user_id}')
            return user
        except Exception as e:
            logger.error(f'❌ Error loading user {user_id}: {str(e)}')
            return None
    
    @login_manager.unauthorized_handler
    def unauthorized():
        """Handle unauthorized access - return JSON for API requests, redirect for HTML"""
        from flask import request, jsonify, redirect, url_for
        # If it's an API request, return JSON
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'message': 'Please log in'}), 401
        # Otherwise redirect to login page
        return redirect(url_for('auth.login'))
    
    # Enregistrement des blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.upload import upload_bp
    from app.routes.search import search_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Initialize Kibana visualizations in background
    from app.services.kibana_init import init_kibana_async
    init_kibana_async()
    
    # Route de health check
    @app.route('/health')
    def health():
        """Endpoint de santé pour Docker healthcheck"""
        return {
            'status': 'healthy',
            'service': 'iot-monitoring-platform',
            'version': '1.0.0'
        }, 200
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500    
    # Disable caching in development
    @app.after_request
    def add_no_cache_headers(response):
        if app.config['DEBUG']:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response    
    return app
