from datetime import datetime
from models import db

CLAIM_STATUSES = ['Pending', 'Approved', 'Rejected', 'Completed']

class Claim(db.Model):
    """
    Model representing a user's verification claim on a found item.
    """
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    claim_reason = db.Column(db.Text, nullable=False)
    private_detail = db.Column(db.Text, nullable=False)  # Confidential identifying mark for admin review
    supporting_information = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Pending', nullable=False, index=True)  # Pending, Approved, Rejected, Completed
    admin_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Claim #{self.id} on Item #{self.item_id} by User #{self.claimant_id} ({self.status})>"
