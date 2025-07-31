from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
from database import db
import os
from routes.trades import trades_bp
from routes.journal import journal_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
# Import models to ensure they are registered with SQLAlchemy
from models import User, Trade, JournalEntry

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# PostgreSQL configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trading_insights')
# Ensure we're using the public schema
if 'postgresql://' in DATABASE_URL and '?' not in DATABASE_URL:
    DATABASE_URL += '?options=-csearch_path%3Dpublic'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": ["https://traderdashpro.vercel.app","https://wwww.traderdashpro.com", "http://localhost:3000"]}})

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'Trading Dashboard API is running'}

# Register blueprints
app.register_blueprint(trades_bp, url_prefix='/api/trades')
app.register_blueprint(journal_bp, url_prefix='/api/journal')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Run migrations on startup
with app.app_context():
    try:
        from flask_migrate import upgrade
        upgrade()
        print("Database migrations completed successfully!")
    except Exception as e:
        print(f"Migration error (this is normal on first run): {e}")
        # Create tables if migrations don't exist yet
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as create_error:
            print(f"Error creating tables: {create_error}")

if __name__ == '__main__':
    # Import routes after db initialization to avoid circular imports
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5001)))