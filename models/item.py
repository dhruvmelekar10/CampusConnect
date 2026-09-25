from datetime import datetime
from models import db

ITEM_CATEGORIES = [
    'Mobile Phone',
    'Laptop',
    'Wallet or Purse',
    'Keys',
    'ID Card',
    'Books or Notes',
    'Bag',
    'Jewellery',
    'Electronic Accessory',
    'Clothing',
    'Other'
]

ITEM_TYPES = ['Lost', 'Found']

ITEM_STATUSES = [
    'Open',
    'Possible Match',
    'Claim Pending',
    'Claim Approved',
    'Returned',
    'Closed'
]

class Item(db.Model):
    """
    Model representing lost and found items reported by campus users.
    """
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    item_type = db.Column(db.String(10), nullable=False, index=True)  # 'Lost' or 'Found'
    item_name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    brand = db.Column(db.String(80), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(120), nullable=False)
    item_date = db.Column(db.Date, nullable=False)
    approximate_time = db.Column(db.String(50), nullable=True)
    identifying_marks = db.Column(db.Text, nullable=True)
    estimated_value = db.Column(db.Float, nullable=True)  # In INR (₹)
    image_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='Open', nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    claims = db.relationship('Claim', backref='item', lazy=True, cascade='all, delete-orphan')
    
    # Matches where this item is the lost item
    matches_as_lost = db.relationship(
        'Match',
        foreign_keys='Match.lost_item_id',
        backref='lost_item',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Matches where this item is the found item
    matches_as_found = db.relationship(
        'Match',
        foreign_keys='Match.found_item_id',
        backref='found_item',
        lazy=True,
        cascade='all, delete-orphan'
    )

    @property
    def is_open(self):
        """Returns True if the item is currently open for claims or matching."""
        return self.status in ['Open', 'Possible Match']

    @property
    def is_claimable(self):
        """Only found items that are Open or Possible Match can receive claims."""
        return self.item_type == 'Found' and self.status in ['Open', 'Possible Match', 'Claim Pending']

    def __repr__(self):
        return f"<Item #{self.id} {self.item_type}: {self.item_name} ({self.status})>"
