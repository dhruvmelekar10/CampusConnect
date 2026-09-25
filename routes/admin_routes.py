import os
import sqlite3
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from models import db, User, Item, Claim, Match, Notification, ITEM_CATEGORIES, ITEM_STATUSES
from routes import admin_required
from services.notification_service import notify_claim_status, notify_item_returned

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Comprehensive administrative control center with institutional KPIs,
    analytical graphs, recent incident reports, and claims needing review.
    """
    # Key Campus Statistics
    total_users = User.query.count()
    total_lost = Item.query.filter_by(item_type='Lost').count()
    total_found = Item.query.filter_by(item_type='Found').count()
    open_reports = Item.query.filter(Item.status.in_(['Open', 'Possible Match'])).count()
    total_matches = Match.query.count()
    pending_claims_count = Claim.query.filter_by(status='Pending').count()
    returned_items_count = Item.query.filter_by(status='Returned').count()

    # Tables for Quick Action
    recent_reports = Item.query.order_by(Item.created_at.desc()).limit(8).all()
    pending_claims = Claim.query.filter_by(status='Pending').order_by(Claim.created_at.desc()).all()
    returned_items = Item.query.filter_by(status='Returned').order_by(Item.updated_at.desc()).limit(6).all()

    # Chart Data Preparation: Items by Category
    category_counts = {}
    for cat in ITEM_CATEGORIES:
        category_counts[cat] = Item.query.filter_by(category=cat).count()

    # Chart Data Preparation: Reports by Status
    status_counts = {}
    for st in ITEM_STATUSES:
        status_counts[st] = Item.query.filter_by(status=st).count()

    chart_data = {
        'lost_vs_found': {
            'labels': ['Lost Reports', 'Found Reports'],
            'data': [total_lost, total_found]
        },
        'categories': {
            'labels': list(category_counts.keys()),
            'data': list(category_counts.values())
        },
        'statuses': {
            'labels': list(status_counts.keys()),
            'data': list(status_counts.values())
        }
    }

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_lost=total_lost,
        total_found=total_found,
        open_reports=open_reports,
        total_matches=total_matches,
        pending_claims_count=pending_claims_count,
        returned_items_count=returned_items_count,
        recent_reports=recent_reports,
        pending_claims=pending_claims,
        returned_items=returned_items,
        chart_data=chart_data
    )

@admin_bp.route('/claims')
@admin_required
def claims():
    """Administrative review page for all item claim requests."""
    status_filter = request.args.get('status', 'Pending')
    query = Claim.query
    if status_filter != 'All':
        query = query.filter_by(status=status_filter)
    claims_list = query.order_by(Claim.created_at.desc()).all()
    return render_template('admin/claims.html', claims=claims_list, selected_status=status_filter)

@admin_bp.route('/claim/<int:claim_id>/approve', methods=['POST'])
@admin_required
def approve_claim(claim_id):
    """Approves a verified ownership claim and updates the item status."""
    claim = Claim.query.get_or_404(claim_id)
    admin_comment = request.form.get('admin_comment', '').strip()

    claim.status = 'Approved'
    claim.admin_comment = admin_comment or "Verification successful. Ownership confirmed by campus administration."
    claim.updated_at = datetime.now()

    # Transition item to 'Claim Approved'
    claim.item.status = 'Claim Approved'
    claim.item.updated_at = datetime.now()

    try:
        db.session.commit()
        notify_claim_status(claim, 'Approved', claim.admin_comment)
        flash(f"Claim #{claim.id} for item '{claim.item.item_name}' approved successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error approving claim: {str(e)}", 'danger')

    return redirect(url_for('admin.claims'))

@admin_bp.route('/claim/<int:claim_id>/reject', methods=['POST'])
@admin_required
def reject_claim(claim_id):
    """Rejects an unverifiable ownership claim."""
    claim = Claim.query.get_or_404(claim_id)
    admin_comment = request.form.get('admin_comment', '').strip()

    claim.status = 'Rejected'
    claim.admin_comment = admin_comment or "Identifying details do not match the found item records."
    claim.updated_at = datetime.now()

    # Revert item status to Open if no other pending claims exist
    other_pending = Claim.query.filter(
        Claim.item_id == claim.item_id,
        Claim.id != claim.id,
        Claim.status == 'Pending'
    ).count()

    if other_pending == 0:
        # Check if item has matches
        if claim.item.matches_as_found:
            claim.item.status = 'Possible Match'
        else:
            claim.item.status = 'Open'

    try:
        db.session.commit()
        notify_claim_status(claim, 'Rejected', claim.admin_comment)
        flash(f"Claim #{claim.id} has been rejected.", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Error rejecting claim: {str(e)}", 'danger')

    return redirect(url_for('admin.claims'))

@admin_bp.route('/item/<int:item_id>/mark-returned', methods=['POST'])
@admin_required
def mark_returned(item_id):
    """Marks an item as safely returned to its rightful owner."""
    item = Item.query.get_or_404(item_id)
    item.status = 'Returned'
    item.updated_at = datetime.now()

    # Complete any approved claim
    approved_claim = Claim.query.filter_by(item_id=item.id, status='Approved').first()
    claimant = None
    if approved_claim:
        approved_claim.status = 'Completed'
        approved_claim.updated_at = datetime.now()
        claimant = approved_claim.claimant

    try:
        db.session.commit()
        notify_item_returned(item, claimant=claimant)
        flash(f"Item '{item.item_name}' has been marked as RETURNED to owner.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating item status: {str(e)}", 'danger')

    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/users')
@admin_required
def users():
    """Administrative user directory with account status controls."""
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Enables or suspends a campus user account."""
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash("You cannot deactivate your own administrative account.", 'warning')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    state = "activated" if user.is_active else "deactivated"
    flash(f"Account for '{user.full_name}' has been {state}.", 'info')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/toggle-role', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    """Promotes or demotes user administrative privileges."""
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash("You cannot alter your own administrative role.", 'warning')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        user.role = 'student'
        flash(f"Demoted '{user.full_name}' to student role.", 'info')
    else:
        user.role = 'admin'
        flash(f"Promoted '{user.full_name}' to administrator role.", 'success')
    
    db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/database', methods=['GET', 'POST'])
@admin_required
def database_view():
    """
    Administrative Database Explorer and SQL Query Console.
    Allows inspection of tables, record counts, schema, and read-only query execution.
    """
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        rel_path = db_uri.replace('sqlite:///', '')
        db_path = rel_path if os.path.isabs(rel_path) else os.path.join(current_app.root_path, rel_path)
    else:
        db_path = os.path.join(current_app.root_path, 'lost_found.db')

    size_kb = (os.path.getsize(db_path) / 1024) if (os.path.exists(db_path) and os.path.isfile(db_path)) else 0.0

    con = db.engine.raw_connection()
    cur = con.cursor()

    try:
        cur.execute("PRAGMA integrity_check;")
        integrity = cur.fetchone()[0]
    except Exception:
        integrity = "OK"

    tables = ['users', 'items', 'matches', 'claims', 'notifications']
    counts = {}
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM '{t}'")
            counts[t] = cur.fetchone()[0]
        except Exception:
            counts[t] = 0

    total_records = sum(counts.values())

    selected_table = request.args.get('table', 'items')
    if selected_table not in tables:
        selected_table = 'items'

    cur.execute(f"SELECT * FROM '{selected_table}' LIMIT 50")
    table_headers = [d[0] for d in cur.description] if cur.description else []
    table_rows = cur.fetchall()

    custom_query = ""
    query_result = None
    query_headers = None
    query_error = None
    query_time = None

    if request.method == 'POST':
        custom_query = request.form.get('query', '').strip()
        first_word = custom_query.split()[0].upper() if custom_query else ''
        if first_word not in ['SELECT', 'PRAGMA', 'EXPLAIN']:
            query_error = "Security Policy: Only read-only queries (SELECT, PRAGMA) are permitted in the web query console."
        else:
            try:
                t0 = time.time()
                cur.execute(custom_query)
                query_time = round((time.time() - t0) * 1000, 2)
                if cur.description:
                    query_headers = [d[0] for d in cur.description]
                    query_result = cur.fetchall()
                else:
                    query_result = []
            except Exception as e:
                query_error = str(e)

    cur.close()

    return render_template(
        'admin/database.html',
        size_kb=round(size_kb, 1),
        sqlite_version=sqlite3.sqlite_version,
        integrity=integrity,
        tables=tables,
        counts=counts,
        total_records=total_records,
        selected_table=selected_table,
        table_headers=table_headers,
        table_rows=table_rows,
        custom_query=custom_query,
        query_result=query_result,
        query_headers=query_headers,
        query_error=query_error,
        query_time=query_time
    )

@admin_bp.route('/database/download-db')
@admin_required
def download_db():
    """Download the live SQLite lost_found.db file directly."""
    db_path = os.path.join(current_app.root_path, 'lost_found.db')
    return send_file(db_path, as_attachment=True, download_name='lost_found.db')

@admin_bp.route('/database/download-sql')
@admin_required
def download_sql():
    """Download the pure SQL schema & data script."""
    sql_path = os.path.join(current_app.root_path, 'database.sql')
    if not os.path.exists(sql_path):
        from db_manager import export_sql
        export_sql()
    return send_file(sql_path, as_attachment=True, download_name='database.sql')

