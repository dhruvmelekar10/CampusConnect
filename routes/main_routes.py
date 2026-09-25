from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import db, Item, Claim, Notification, Match, User
from routes import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    CampusConnect Landing Page featuring campus metrics, recent reports,
    and a clear 3-step process guide.
    """
    # Key campus metrics
    total_open_reports = Item.query.filter(Item.status.in_(['Open', 'Possible Match'])).count()
    items_returned = Item.query.filter_by(status='Returned').count()
    pending_claims = Claim.query.filter_by(status='Pending').count()

    # Recent 6 items across campus
    recent_items = Item.query.order_by(Item.created_at.desc()).limit(6).all()

    return render_template(
        'home.html',
        total_open_reports=total_open_reports,
        items_returned=items_returned,
        pending_claims=pending_claims,
        recent_items=recent_items
    )

@main_bp.route('/about')
def about():
    """Information regarding VSIT's (Vidyalankar School of Information Technology) Lost & Found guidelines and policies."""
    return render_template('about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing user activity, recent reports, matches, and claims."""
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    # User-specific statistics
    my_lost_count = Item.query.filter_by(reporter_id=user_id, item_type='Lost').count()
    my_found_count = Item.query.filter_by(reporter_id=user_id, item_type='Found').count()
    my_claims_count = Claim.query.filter_by(claimant_id=user_id).count()

    # Smart matches affecting user's items
    user_item_ids = [i.id for i in Item.query.filter_by(reporter_id=user_id).all()]
    user_matches = Match.query.filter(
        (Match.lost_item_id.in_(user_item_ids)) | (Match.found_item_id.in_(user_item_ids))
    ).order_by(Match.created_at.desc()).limit(5).all()

    # Recent reports by user
    recent_user_reports = Item.query.filter_by(reporter_id=user_id).order_by(Item.created_at.desc()).limit(5).all()

    # Recent claims by user
    recent_user_claims = Claim.query.filter_by(claimant_id=user_id).order_by(Claim.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        user=user,
        my_lost_count=my_lost_count,
        my_found_count=my_found_count,
        my_claims_count=my_claims_count,
        user_matches=user_matches,
        recent_user_reports=recent_user_reports,
        recent_user_claims=recent_user_claims
    )

@main_bp.route('/notifications')
@login_required
def notifications():
    """Displays in-app notifications for the logged-in user."""
    user_id = session.get('user_id')
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifs)

@main_bp.route('/notifications/read/<int:notif_id>', methods=['POST', 'GET'])
@login_required
def mark_notification_read(notif_id):
    """Marks a single notification as read."""
    user_id = session.get('user_id')
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first_or_404()
    notif.is_read = True
    db.session.commit()
    flash("Notification marked as read.", 'info')
    return redirect(url_for('main.notifications'))

@main_bp.route('/notifications/read-all', methods=['POST', 'GET'])
@login_required
def mark_all_notifications_read():
    """Marks all notifications for the current user as read."""
    user_id = session.get('user_id')
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash("All notifications marked as read.", 'info')
    return redirect(url_for('main.notifications'))
