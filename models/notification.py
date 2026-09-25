from datetime import datetime
from models import db

class Notification(db.Model):
    """
    Model representing in-app notifications dispatched to users.
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'match_found', 'claim_approved', 'claim_rejected', 'item_returned', 'system'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Notification #{self.id} for User #{self.user_id} read={self.is_read}>"
