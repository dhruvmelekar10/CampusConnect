import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campusconnect-secret-vsit-key-2026')
    
    # Vercel Serverless environment support
    # In Vercel serverless functions, the root filesystem is read-only; /tmp is writable.
    if os.environ.get('VERCEL'):
        tmp_db = '/tmp/lost_found.db'
        src_db = os.path.join(BASE_DIR, 'lost_found.db')
        if not os.path.exists(tmp_db) and os.path.exists(src_db):
            import shutil
            try:
                shutil.copy2(src_db, tmp_db)
            except Exception:
                pass
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_db}"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'lost_found.db')}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB maximum file upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Institution Branding
    COLLEGE_NAME = "VSIT (Vidyalankar School of Information Technology)"
    COLLEGE_SHORT_NAME = "VSIT"
    APP_NAME = "CampusConnect"
    CURRENCY_SYMBOL = "₹"
    
    # Pagination
    ITEMS_PER_PAGE = 9

class TestConfig(Config):
    """Testing configuration using an in-memory SQLite database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'test_uploads')
