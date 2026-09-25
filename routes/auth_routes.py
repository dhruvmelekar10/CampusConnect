from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from services.validation_service import validate_registration_data

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new student and staff registration."""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        department = request.form.get('department', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'student').strip()
        
        # Restrict self-registration to 'student' or 'staff'
        if role not in ['student', 'staff']:
            role = 'student'

        # Validation
        is_valid, err_msg = validate_registration_data({
            'full_name': full_name,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        })

        if not is_valid:
            flash(err_msg, 'danger')
            return render_template('register.html', 
                                   full_name=full_name, 
                                   email=email, 
                                   department=department, 
                                   phone=phone,
                                   role=role)

        # Check existing user
        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists. Please log in.", 'warning')
            return redirect(url_for('auth.login'))

        # Create new user
        new_user = User(
            full_name=full_name,
            email=email,
            role=role,
            department=department or None,
            phone=phone or None,
            is_active=True
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in to CampusConnect.", 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", 'danger')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication for all roles (Student, Staff, Admin)."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        if not email or not password:
            flash("Please enter both email and password.", 'warning')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", 'danger')
            return render_template('login.html', email=email)

        if not user.is_active:
            flash("Your account has been deactivated. Please contact campus administration.", 'danger')
            return render_template('login.html', email=email)

        # Session configuration
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['email'] = user.email
        session['role'] = user.role
        session.permanent = bool(remember)

        flash(f"Welcome back, {user.full_name}!", 'success')

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Clears the active session and logs the user out."""
    session.clear()
    flash("You have been successfully logged out.", 'info')
    return redirect(url_for('main.index'))
