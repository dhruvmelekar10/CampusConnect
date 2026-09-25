from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Item, Claim
from routes import login_required

claim_bp = Blueprint('claim', __name__)

@claim_bp.route('/claim/<int:item_id>', methods=['GET', 'POST'])
@login_required
def submit_claim(item_id):
    """
    Form for a student or staff member to claim ownership of a found item.
    Collects ownership rationale and confidential private identifying details.
    """
    item = Item.query.get_or_404(item_id)
    user_id = session.get('user_id')

    # Security and sanity validations
    if item.item_type != 'Found':
        flash("Claim requests can only be submitted for Found items.", 'warning')
        return redirect(url_for('item.item_details', item_id=item.id))

    if item.reporter_id == user_id:
        flash("You cannot claim an item that you reported finding.", 'warning')
        return redirect(url_for('item.item_details', item_id=item.id))

    if not item.is_claimable:
        flash("This item is not currently eligible for new claim requests.", 'warning')
        return redirect(url_for('item.item_details', item_id=item.id))

    # Check for existing pending claim by this user
    existing_claim = Claim.query.filter_by(item_id=item.id, claimant_id=user_id).first()
    if existing_claim:
        flash(f"You have already submitted a claim for this item (Status: {existing_claim.status}).", 'info')
        return redirect(url_for('claim.my_claims'))

    if request.method == 'POST':
        claim_reason = request.form.get('claim_reason', '').strip()
        private_detail = request.form.get('private_detail', '').strip()
        supporting_information = request.form.get('supporting_information', '').strip()
        contact_preference = request.form.get('contact_preference', '').strip()

        errors = []
        if not claim_reason or len(claim_reason) < 10:
            errors.append("Please provide a thorough reason why this item belongs to you (at least 10 characters).")
        if not private_detail or len(private_detail) < 5:
            errors.append("Please describe at least one confidential identifying detail (e.g. wallpaper, serial, engraving, inside contents).")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('claims.html', item=item, is_submit_form=True)

        full_supporting = supporting_information
        if contact_preference:
            full_supporting = f"Preferred Contact: {contact_preference}\n{supporting_information}".strip()

        claim = Claim(
            item_id=item.id,
            claimant_id=user_id,
            claim_reason=claim_reason,
            private_detail=private_detail,
            supporting_information=full_supporting,
            status='Pending'
        )

        try:
            db.session.add(claim)
            # Update item status to 'Claim Pending' if it was Open or Possible Match
            if item.status in ['Open', 'Possible Match']:
                item.status = 'Claim Pending'

            db.session.commit()
            flash("Your claim request has been submitted for administrative verification.", 'success')
            return redirect(url_for('claim.my_claims'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while submitting your claim. Please try again.", 'danger')

    return render_template('claims.html', item=item, is_submit_form=True)

@claim_bp.route('/my-claims')
@login_required
def my_claims():
    """Displays all claims submitted by the logged-in user with status tracking."""
    user_id = session.get('user_id')
    user_claims = Claim.query.filter_by(claimant_id=user_id).order_by(Claim.created_at.desc()).all()
    return render_template('claims.html', claims=user_claims, is_submit_form=False)
