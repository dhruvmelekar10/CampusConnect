from datetime import datetime
from models import db

class Match(db.Model):
    """
    Model representing a smart match between a Lost item and a Found item.
    """
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    found_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, index=True)
    match_score = db.Column(db.Integer, nullable=False)  # 50 to 100
    match_reason = db.Column(db.Text, nullable=False)    # Explainable match factors
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_seen = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('lost_item_id', 'found_item_id', name='uq_lost_found_match'),
    )

    def __repr__(self):
        return f"<Match Lost:{self.lost_item_id} <=> Found:{self.found_item_id} ({self.match_score} pts)>"
