import os
from flask import Flask, render_template, session
from config import Config
from models import db, User
from services.notification_service import get_unread_count

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.item_routes import item_bp
from routes.claim_routes import claim_bp
from routes.admin_routes import admin_bp

def create_app(config_class=Config):
    """
    Application factory for CampusConnect – Smart Lost and Found Management System.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(claim_bp)
    app.register_blueprint(admin_bp)

    # Global template context processor
    @app.context_processor
    def inject_global_data():
        user_id = session.get('user_id')
        current_user = None
        unread_count = 0
        if user_id:
            current_user = db.session.get(User, user_id)
            unread_count = get_unread_count(user_id)
        
        return {
            'college_name': app.config.get('COLLEGE_NAME', 'VSIT (Vidyalankar School of Information Technology)'),
            'college_short_name': app.config.get('COLLEGE_SHORT_NAME', 'VSIT'),
            'app_name': app.config.get('APP_NAME', 'CampusConnect'),
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
            'current_user': current_user,
            'unread_notifications_count': unread_count
        }

    # Custom Jinja template filters
    @app.template_filter('format_date')
    def format_date(value, format='%d %b %Y'):
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('format_currency')
    def format_currency(value):
        if value is None:
            return "N/A"
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return str(value)

    # Custom Error Pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto-initialize database tables if not existing
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print(f"Starting {Config.APP_NAME} for {Config.COLLEGE_NAME}...")
    print("Accessible locally at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
