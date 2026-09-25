from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models for easy access across the project
from models.user import User
from models.item import Item, ITEM_CATEGORIES, ITEM_TYPES, ITEM_STATUSES
from models.match import Match
from models.claim import Claim, CLAIM_STATUSES
from models.notification import Notification

__all__ = [
    'db',
    'User',
    'Item',
    'Match',
    'Claim',
    'Notification',
    'ITEM_CATEGORIES',
    'ITEM_TYPES',
    'ITEM_STATUSES',
    'CLAIM_STATUSES'
]
