from models import db, Notification

def create_notification(user_id, message, notification_type='system'):
    """
    Creates and commits an in-app notification for a designated user.
    """
    try:
        notification = Notification(
            user_id=user_id,
            message=message,
            notification_type=notification_type,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None

def notify_match(lost_item, found_item, score):
    """
    Sends in-app notifications to both reporters when a high-scoring match is discovered.
    """
    # Notify reporter of the lost item
    lost_msg = (
        f"Smart Match Alert ({score}% match): A found item '{found_item.item_name}' "
        f"matches your lost report '{lost_item.item_name}'."
    )
    create_notification(lost_item.reporter_id, lost_msg, notification_type='match_found')

    # Notify reporter of the found item
    found_msg = (
        f"Smart Match Alert ({score}% match): A lost item report '{lost_item.item_name}' "
        f"matches the item you found: '{found_item.item_name}'."
    )
    create_notification(found_item.reporter_id, found_msg, notification_type='match_found')

def notify_claim_status(claim, new_status, admin_comment=None):
    """
    Sends an in-app notification to the claimant when an administrator updates their claim.
    """
    comment_text = f" Admin note: {admin_comment}" if admin_comment else ""
    if new_status == 'Approved':
        msg = (
            f"Your claim on item '{claim.item.item_name}' has been APPROVED by the campus administration! "
            f"Please visit the Admin / Lost & Found desk to collect your item.{comment_text}"
        )
        create_notification(claim.claimant_id, msg, notification_type='claim_approved')
    elif new_status == 'Rejected':
        msg = (
            f"Your claim on item '{claim.item.item_name}' was not approved.{comment_text}"
        )
        create_notification(claim.claimant_id, msg, notification_type='claim_rejected')

def notify_item_returned(item, claimant=None):
    """
    Notifies the reporter and claimant when an item is marked as Returned.
    """
    # Notify reporter
    reporter_msg = (
        f"Item status update: Your reported item '{item.item_name}' has been officially marked as RETURNED."
    )
    create_notification(item.reporter_id, reporter_msg, notification_type='item_returned')

    # Notify claimant if applicable
    if claimant:
        claimant_msg = (
            f"Item status update: '{item.item_name}' has been officially marked as RETURNED to you. Thank you for using CampusConnect!"
        )
        create_notification(claimant.id, claimant_msg, notification_type='item_returned')

def get_unread_count(user_id):
    """Returns the number of unread notifications for a user."""
    if not user_id:
        return 0
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()
