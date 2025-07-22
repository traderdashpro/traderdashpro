from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
import os
from routes.trades import trades_bp
from routes.journal import journal_bp
from routes.dashboard import dashboard_bp
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')




# PostgreSQL configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trading_insights')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Enable CORS

# CORS(app, resources={r"/api/*": {"origins": "https://traderdashpro.vercel.app/"}})
CORS(app, resources={r"/api/*": {"origins": "https://traderdashpro.vercel.app/"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'Trading Dashboard API is running'}

    # Register blueprints
app.register_blueprint(trades_bp, url_prefix='/api/trades')
app.register_blueprint(journal_bp, url_prefix='/api/journal')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Import routes after db initialization to avoid circular imports
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5001)))