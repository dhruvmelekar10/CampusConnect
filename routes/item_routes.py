import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Item, Match, Claim, User, ITEM_CATEGORIES, ITEM_TYPES, ITEM_STATUSES
from routes import login_required
from services.validation_service import validate_item_data, save_uploaded_image
from services.matching_service import run_matching_for_item

item_bp = Blueprint('item', __name__)

@item_bp.route('/items')
@item_bp.route('/search')
def search():
    """
    Case-insensitive search and multi-criteria filtering with sorting and pagination.
    Available to all users including Guests.
    """
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    item_type = request.args.get('item_type', '').strip()
    brand = request.args.get('brand', '').strip()
    color = request.args.get('color', '').strip()
    location = request.args.get('location', '').strip()
    status = request.args.get('status', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)

    query = Item.query

    # Search filters
    if q:
        query = query.filter(Item.item_name.ilike(f'%{q}%'))
    if category and category in ITEM_CATEGORIES:
        query = query.filter(Item.category == category)
    if item_type and item_type in ITEM_TYPES:
        query = query.filter(Item.item_type == item_type)
    if brand:
        query = query.filter(Item.brand.ilike(f'%{brand}%'))
    if color:
        query = query.filter(Item.color.ilike(f'%{color}%'))
    if location:
        query = query.filter(Item.location.ilike(f'%{location}%'))
    if status and status in ITEM_STATUSES:
        query = query.filter(Item.status == status)

    # Date range filters
    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Item.item_date >= d_from)
        except ValueError:
            pass
    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Item.item_date <= d_to)
        except ValueError:
            pass

    # Sorting options
    if sort_by == 'oldest':
        query = query.order_by(Item.item_date.asc(), Item.created_at.asc())
    elif sort_by == 'name_asc':
        query = query.order_by(Item.item_name.asc())
    elif sort_by == 'location_asc':
        query = query.order_by(Item.location.asc())
    else:  # newest first default
        query = query.order_by(Item.item_date.desc(), Item.created_at.desc())

    # Pagination (9 per page)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 9)
    items_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'search.html',
        items=items_paginated.items,
        pagination=items_paginated,
        categories=ITEM_CATEGORIES,
        item_types=ITEM_TYPES,
        statuses=ITEM_STATUSES,
        q=q,
        selected_category=category,
        selected_type=item_type,
        brand=brand,
        color=color,
        location=location,
        selected_status=status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by
    )

@item_bp.route('/report/lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Form to report a lost item on campus."""
    return _handle_item_reporting('Lost')

@item_bp.route('/report/found', methods=['GET', 'POST'])
@login_required
def report_found():
    """Form to report a found item on campus."""
    return _handle_item_reporting('Found')

def _handle_item_reporting(target_type):
    """Common helper for Lost and Found reporting workflows."""
    user_id = session.get('user_id')

    if request.method == 'POST':
        raw_data = request.form.to_dict()
        raw_data['item_type'] = target_type

        is_valid, result = validate_item_data(raw_data)
        if not is_valid:
            flash(result, 'danger')
            return render_template(
                'report_item.html',
                item_type=target_type,
                categories=ITEM_CATEGORIES,
                form_data=raw_data
            )

        # File upload handling
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    image_filename = save_uploaded_image(file, current_app.config['UPLOAD_FOLDER'])
                except ValueError as ve:
                    flash(str(ve), 'danger')
                    return render_template(
                        'report_item.html',
                        item_type=target_type,
                        categories=ITEM_CATEGORIES,
                        form_data=raw_data
                    )

        new_item = Item(
            reporter_id=user_id,
            item_type=target_type,
            item_name=result['item_name'],
            category=result['category'],
            description=result['description'],
            brand=result['brand'],
            color=result['color'],
            location=result['location'],
            item_date=result['item_date'],
            approximate_time=result['approximate_time'],
            identifying_marks=result['identifying_marks'],
            estimated_value=result['estimated_value'],
            image_filename=image_filename,
            status='Open'
        )

        try:
            db.session.add(new_item)
            db.session.commit()

            # Execute automated smart matching
            new_matches = run_matching_for_item(new_item)

            if new_matches:
                flash(
                    f"Report submitted! CampusConnect found {len(new_matches)} potential matching item(s).",
                    'success'
                )
            else:
                flash("Your report has been successfully submitted.", 'success')

            return redirect(url_for('item.item_details', item_id=new_item.id))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while saving the report: {str(e)}", 'danger')

    return render_template(
        'report_item.html',
        item_type=target_type,
        categories=ITEM_CATEGORIES,
        form_data={}
    )

@item_bp.route('/item/<int:item_id>')
def item_details(item_id):
    """
    Displays complete item details.
    Sensitive contact details are kept private; claims and contact buttons are provided.
    """
    item = Item.query.get_or_404(item_id)
    current_user_id = session.get('user_id')

    # Fetch associated matches for this item
    matches = []
    if item.item_type == 'Lost':
        matches = Match.query.filter_by(lost_item_id=item.id).order_by(Match.match_score.desc()).all()
    else:
        matches = Match.query.filter_by(found_item_id=item.id).order_by(Match.match_score.desc()).all()

    # Check if logged-in user already submitted a claim for this item
    user_claim = None
    if current_user_id and item.item_type == 'Found':
        user_claim = Claim.query.filter_by(item_id=item.id, claimant_id=current_user_id).first()

    return render_template(
        'item_details.html',
        item=item,
        matches=matches,
        user_claim=user_claim,
        current_user_id=current_user_id
    )

@item_bp.route('/my-reports')
@login_required
def my_reports():
    """Lists all items reported by the currently authenticated user."""
    user_id = session.get('user_id')
    type_filter = request.args.get('type')
    
    query = Item.query.filter_by(reporter_id=user_id)
    if type_filter in ITEM_TYPES:
        query = query.filter_by(item_type=type_filter)
        
    reports = query.order_by(Item.created_at.desc()).all()
    return render_template('my_reports.html', reports=reports, selected_type=type_filter)

@item_bp.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Allows reporters to modify their open reports."""
    item = Item.query.get_or_404(item_id)
    user_id = session.get('user_id')
    user_role = session.get('role')

    # Authorization check
    if item.reporter_id != user_id and user_role != 'admin':
        flash("You are not authorized to edit this report.", 'danger')
        return redirect(url_for('item.item_details', item_id=item.id))

    if item.status not in ['Open', 'Possible Match'] and user_role != 'admin':
        flash("Items with claims or already returned cannot be edited.", 'warning')
        return redirect(url_for('item.item_details', item_id=item.id))

    if request.method == 'POST':
        raw_data = request.form.to_dict()
        raw_data['item_type'] = item.item_type

        is_valid, result = validate_item_data(raw_data)
        if not is_valid:
            flash(result, 'danger')
            return render_template('edit_item.html', item=item, categories=ITEM_CATEGORIES)

        # Image update handling
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    new_filename = save_uploaded_image(file, current_app.config['UPLOAD_FOLDER'])
                    item.image_filename = new_filename
                except ValueError as ve:
                    flash(str(ve), 'danger')
                    return render_template('edit_item.html', item=item, categories=ITEM_CATEGORIES)

        item.item_name = result['item_name']
        item.category = result['category']
        item.description = result['description']
        item.brand = result['brand']
        item.color = result['color']
        item.location = result['location']
        item.item_date = result['item_date']
        item.approximate_time = result['approximate_time']
        item.identifying_marks = result['identifying_marks']
        item.estimated_value = result['estimated_value']
        item.updated_at = datetime.now()

        try:
            db.session.commit()
            # Re-run matching after modification
            run_matching_for_item(item)
            flash("Report updated successfully.", 'success')
            return redirect(url_for('item.item_details', item_id=item.id))
        except Exception as e:
            db.session.rollback()
            flash("Failed to update report.", 'danger')

    return render_template('edit_item.html', item=item, categories=ITEM_CATEGORIES)

@item_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    """Deletes an item report along with associated images."""
    item = Item.query.get_or_404(item_id)
    user_id = session.get('user_id')
    user_role = session.get('role')

    if item.reporter_id != user_id and user_role != 'admin':
        flash("You do not have permission to delete this report.", 'danger')
        return redirect(url_for('item.item_details', item_id=item.id))

    try:
        # Delete image file from static uploads if it exists
        if item.image_filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_filename)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(item)
        db.session.commit()
        flash("Item report has been deleted.", 'info')
    except Exception as e:
        db.session.rollback()
        flash("Error occurred while deleting report.", 'danger')

    if user_role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('item.my_reports'))

@item_bp.route('/matches')
@login_required
def matches():
    """Displays smart matches relevant to the logged-in user or all matches for admin."""
    user_id = session.get('user_id')
    user_role = session.get('role')

    if user_role == 'admin':
        all_matches = Match.query.order_by(Match.created_at.desc()).all()
    else:
        user_items = Item.query.filter_by(reporter_id=user_id).all()
        user_item_ids = [i.id for i in user_items]
        all_matches = Match.query.filter(
            (Match.lost_item_id.in_(user_item_ids)) | (Match.found_item_id.in_(user_item_ids))
        ).order_by(Match.match_score.desc()).all()

    return render_template('matches.html', matches=all_matches)
