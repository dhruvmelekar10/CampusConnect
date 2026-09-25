import re
from difflib import SequenceMatcher
from models import db, Item, Match
from services.notification_service import notify_match

# Common words to filter out during keyword extraction
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'from',
    'by', 'of', 'is', 'was', 'are', 'were', 'it', 'its', 'this', 'that', 'near',
    'inside', 'outside', 'around', 'floor', 'room', 'building', 'my', 'i', 'have',
    'has', 'had', 'been', 'there', 'here', 'please', 'help', 'contact', 'me'
}

def extract_tokens(text):
    """Extracts lowercase alphabetic words excluding short tokens and stopwords."""
    if not text:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', str(text).lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}

def calculate_match_score(lost_item, found_item):
    """
    Computes a transparent, explainable match score between a Lost item and a Found item.
    Rules:
    - Same category: +30 points
    - Similar item name: +25 points
    - Same brand: +15 points
    - Same color: +10 points
    - Same or nearby location: +10 points
    - Similar description keywords: +10 points
    Total possible: 100 points.
    Returns: (score, list_of_reasons, reason_text)
    """
    score = 0
    reasons = []

    # 1. Category check (+30 points)
    if lost_item.category and found_item.category:
        if lost_item.category.strip().lower() == found_item.category.strip().lower():
            score += 30
            reasons.append("Same category")

    # 2. Similar item name (+25 points)
    if lost_item.item_name and found_item.item_name:
        name1 = lost_item.item_name.strip().lower()
        name2 = found_item.item_name.strip().lower()
        ratio = SequenceMatcher(None, name1, name2).ratio()
        tokens1 = extract_tokens(name1)
        tokens2 = extract_tokens(name2)
        if ratio >= 0.6 or (tokens1 and tokens2 and (tokens1 & tokens2)):
            score += 25
            reasons.append("Similar item name")

    # 3. Same brand (+15 points)
    if lost_item.brand and found_item.brand:
        b1 = lost_item.brand.strip().lower()
        b2 = found_item.brand.strip().lower()
        if b1 == b2 or b1 in b2 or b2 in b1:
            score += 15
            reasons.append("Same brand")

    # 4. Same color (+10 points)
    if lost_item.color and found_item.color:
        c1 = lost_item.color.strip().lower()
        c2 = found_item.color.strip().lower()
        color_tokens1 = extract_tokens(c1)
        color_tokens2 = extract_tokens(c2)
        if c1 == c2 or (color_tokens1 and color_tokens2 and (color_tokens1 & color_tokens2)):
            score += 10
            reasons.append("Same color")

    # 5. Same or nearby location (+10 points)
    if lost_item.location and found_item.location:
        loc1 = lost_item.location.strip().lower()
        loc2 = found_item.location.strip().lower()
        loc_tokens1 = extract_tokens(loc1)
        loc_tokens2 = extract_tokens(loc2)
        if loc1 == loc2 or (loc_tokens1 and loc_tokens2 and (loc_tokens1 & loc_tokens2)):
            score += 10
            reasons.append("Same or nearby location")

    # 6. Similar description keywords (+10 points)
    if lost_item.description and found_item.description:
        desc_tokens1 = extract_tokens(lost_item.description)
        desc_tokens2 = extract_tokens(found_item.description)
        shared_keywords = desc_tokens1 & desc_tokens2
        if len(shared_keywords) >= 1:
            score += 10
            reasons.append("Similar description keywords")

    # Form human-friendly readable reason
    if not reasons:
        reason_text = "No strong matching attributes found."
    elif len(reasons) == 1:
        reason_text = f"{reasons[0]}."
    elif len(reasons) == 2:
        reason_text = f"{reasons[0]} and {reasons[1].lower()}."
    else:
        reason_text = f"{', '.join(reasons[:-1])}, and {reasons[-1].lower()}."

    return min(score, 100), reasons, reason_text

def run_matching_for_item(item):
    """
    Compares the given item against candidate reports of the opposite type.
    Creates Match records for pairs scoring >= 50 and sends notifications.
    Returns list of newly discovered Match objects.
    """
    new_matches = []
    
    if item.item_type == 'Lost':
        candidates = Item.query.filter(
            Item.item_type == 'Found',
            Item.status.in_(['Open', 'Possible Match', 'Claim Pending'])
        ).all()
        lost_item = item
        for found_item in candidates:
            score, _, reason = calculate_match_score(lost_item, found_item)
            if score >= 50:
                match = _record_match(lost_item, found_item, score, reason)
                if match:
                    new_matches.append(match)

    elif item.item_type == 'Found':
        candidates = Item.query.filter(
            Item.item_type == 'Lost',
            Item.status.in_(['Open', 'Possible Match'])
        ).all()
        found_item = item
        for lost_item in candidates:
            score, _, reason = calculate_match_score(lost_item, found_item)
            if score >= 50:
                match = _record_match(lost_item, found_item, score, reason)
                if match:
                    new_matches.append(match)

    return new_matches

def _record_match(lost_item, found_item, score, reason):
    """Helper to save match record and notify users if new."""
    existing = Match.query.filter_by(
        lost_item_id=lost_item.id,
        found_item_id=found_item.id
    ).first()

    if existing:
        # Update existing score/reason if changed
        existing.match_score = score
        existing.match_reason = reason
        db.session.commit()
        return None

    # Create new match record
    match = Match(
        lost_item_id=lost_item.id,
        found_item_id=found_item.id,
        match_score=score,
        match_reason=reason,
        is_seen=False
    )
    db.session.add(match)

    # Update item status to 'Possible Match' if currently 'Open'
    if lost_item.status == 'Open':
        lost_item.status = 'Possible Match'
    if found_item.status == 'Open':
        found_item.status = 'Possible Match'

    db.session.commit()

    # Trigger notifications for both users
    notify_match(lost_item, found_item, score)

    return match
