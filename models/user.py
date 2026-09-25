from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    """
    User model representing students, staff members, and administrators.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'staff', 'admin'
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    items = db.relationship('Item', backref='reporter', lazy=True, cascade='all, delete-orphan')
    claims = db.relationship('Claim', backref='claimant', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes the user password using Werkzeug security."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Checks if the user has administrator privileges."""
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
