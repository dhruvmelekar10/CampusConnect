import os
import re
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config
from models.item import ITEM_CATEGORIES, ITEM_TYPES

def allowed_file(filename):
    """Verifies that an uploaded file has a permitted image extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def save_uploaded_image(file_storage, upload_folder=None):
    """
    Saves an uploaded image with a sanitized, collision-free filename.
    Returns the saved filename or None if invalid.
    """
    if not file_storage or not file_storage.filename:
        return None
    
    if not allowed_file(file_storage.filename):
        raise ValueError("Invalid image format. Allowed formats: PNG, JPG, JPEG.")
    
    folder = upload_folder or Config.UPLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    
    base_name = secure_filename(file_storage.filename)
    unique_prefix = uuid.uuid4().hex[:10]
    filename = f"{unique_prefix}_{base_name}"
    filepath = os.path.join(folder, filename)
    
    file_storage.save(filepath)
    return filename

def validate_registration_data(data):
    """
    Validates user registration payload.
    Returns (is_valid, error_message).
    """
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not full_name or len(full_name) < 2:
        return False, "Full name must be at least 2 characters long."

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return False, "Please provide a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if confirm_password and password != confirm_password:
        return False, "Passwords do not match."

    return True, None

def validate_item_data(data):
    """
    Validates item reporting form fields.
    Returns (is_valid, sanitized_dict_or_error_message).
    """
    errors = []

    item_name = data.get('item_name', '').strip()
    item_type = data.get('item_type', '').strip()
    category = data.get('category', '').strip()
    description = data.get('description', '').strip()
    location = data.get('location', '').strip()
    item_date_str = data.get('item_date', '').strip()
    estimated_value_str = data.get('estimated_value', '').strip()

    if not item_name:
        errors.append("Item name is required.")
    
    if item_type not in ITEM_TYPES:
        errors.append(f"Invalid item type. Must be one of: {', '.join(ITEM_TYPES)}.")

    if category not in ITEM_CATEGORIES:
        errors.append(f"Invalid category. Must be one of the campus categories.")

    if not description or len(description) < 5:
        errors.append("Description must be at least 5 characters.")

    if not location:
        errors.append("Campus location is required.")

    parsed_date = None
    if not item_date_str:
        errors.append("Date is required.")
    else:
        try:
            parsed_date = datetime.strptime(item_date_str, '%Y-%m-%d').date()
            if parsed_date > datetime.now().date():
                errors.append("The date cannot be in the future.")
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD.")

    estimated_value = None
    if estimated_value_str:
        try:
            val = float(estimated_value_str)
            if val < 0:
                errors.append("Estimated value cannot be negative.")
            else:
                estimated_value = val
        except ValueError:
            errors.append("Estimated value must be a valid number.")

    if errors:
        return False, " ".join(errors)

    sanitized = {
        'item_name': item_name,
        'item_type': item_type,
        'category': category,
        'description': description,
        'brand': data.get('brand', '').strip() or None,
        'color': data.get('color', '').strip() or None,
        'location': location,
        'item_date': parsed_date,
        'approximate_time': data.get('approximate_time', '').strip() or None,
        'identifying_marks': data.get('identifying_marks', '').strip() or None,
        'estimated_value': estimated_value
    }

    return True, sanitized
