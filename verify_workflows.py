import os
import sys
from datetime import date
from app import create_app
from config import Config
from models import db, User, Item, Match, Claim, Notification

def run_workflow_verifications():
    print("==================================================")
    print("CAMPUSCONNECT - WORKFLOW VERIFICATION TEST SUITE")
    print("==================================================")
    
    app = create_app(Config)
    client = app.test_client()

    with app.app_context():
        # Ensure fresh seeded state
        import seed
        seed.seed_database()

        # ------------------------------------------------------------------
        # Workflow 1: Register -> Login -> Report Lost Item -> View Dashboard
        # ------------------------------------------------------------------
        print("\n--- Testing Workflow 1: Registration, Login & Lost Item Report ---")
        reg_resp = client.post('/register', data={
            'full_name': 'Kavita Nair',
            'email': 'kavita.nair@vsit.edu.in',
            'role': 'student',
            'department': 'Electronics & Telecommunication',
            'phone': '+91 98111 22334',
            'password': 'Student@123',
            'confirm_password': 'Student@123'
        }, follow_redirects=True)
        assert reg_resp.status_code == 200
        assert b"Registration successful" in reg_resp.data
        print("[PASS] User Registration successful.")

        login_resp = client.post('/login', data={
            'email': 'kavita.nair@vsit.edu.in',
            'password': 'Student@123'
        }, follow_redirects=True)
        assert login_resp.status_code == 200
        assert b"Welcome back, Kavita Nair" in login_resp.data
        print("[PASS] User Login successful.")

        report_lost_resp = client.post('/report/lost', data={
            'item_name': 'Casio FX-991EX ClassWiz Calculator',
            'category': 'Electronic Accessory',
            'description': 'Black scientific calculator with stickers on the protective cover.',
            'brand': 'Casio',
            'color': 'Black',
            'location': 'Physics Lab 2',
            'item_date': date.today().strftime('%Y-%m-%d'),
            'approximate_time': '11:00 AM',
            'identifying_marks': 'Transparent tape over battery compartment',
            'estimated_value': '1300'
        }, follow_redirects=True)
        assert report_lost_resp.status_code == 200
        print("[PASS] Lost Item Report submitted successfully.")

        dash_resp = client.get('/dashboard')
        assert dash_resp.status_code == 200
        assert b"Kavita Nair" in dash_resp.data
        assert b"Casio FX-991EX ClassWiz Calculator" in dash_resp.data
        print("[PASS] User Dashboard displays newly reported item.")

        # ------------------------------------------------------------------
        # Workflow 2: Report Found Item -> Search -> View Details
        # ------------------------------------------------------------------
        print("\n--- Testing Workflow 2: Report Found Item, Search & View Details ---")
        report_found_resp = client.post('/report/found', data={
            'item_name': 'Blue Parker Vector Fountain Pen',
            'category': 'Other',
            'description': 'Metallic blue Parker vector pen found on desk 12.',
            'brand': 'Parker',
            'color': 'Blue',
            'location': 'Seminar Hall B',
            'item_date': date.today().strftime('%Y-%m-%d'),
            'approximate_time': '4:00 PM',
            'identifying_marks': 'Silver pocket clip'
        }, follow_redirects=True)
        assert report_found_resp.status_code == 200
        print("[PASS] Found Item Report submitted successfully.")

        # Search without authentication (Guest accessibility check)
        client.get('/logout')
        search_resp = client.get('/search?q=parker&category=Other')
        assert search_resp.status_code == 200
        assert b"Blue Parker Vector Fountain Pen" in search_resp.data
        print("[PASS] Search & Filtering catalog returned expected found item.")

        found_item = Item.query.filter_by(item_name='Blue Parker Vector Fountain Pen').first()
        detail_resp = client.get(f'/item/{found_item.id}')
        assert detail_resp.status_code == 200
        assert b"Blue Parker Vector Fountain Pen" in detail_resp.data
        assert b"Seminar Hall B" in detail_resp.data
        # Ensure private phone is not leaked publicly to guest
        assert b"+91 98111 22334" not in detail_resp.data
        print("[PASS] Item details page rendered with privacy controls active.")

        # ------------------------------------------------------------------
        # Workflow 3: Matching Lost and Found Items -> Verify Match
        # ------------------------------------------------------------------
        print("\n--- Testing Workflow 3: Smart Match Discovery & Notification ---")
        # Notice when Kavita reported the Casio calculator, it matched with student3's found Casio in seed.py!
        casio_match = Match.query.filter(
            (Match.lost_item_id == Item.query.filter_by(item_name='Casio FX-991EX ClassWiz Calculator').first().id)
        ).first()
        assert casio_match is not None
        assert casio_match.match_score >= 50
        print(f"[PASS] Smart Match automatically discovered: Score {casio_match.match_score}%, Reason: {casio_match.match_reason}")

        # ------------------------------------------------------------------
        # Workflow 4: Submit Claim -> Admin Login -> Approve Claim -> Mark Returned
        # ------------------------------------------------------------------
        print("\n--- Testing Workflow 4: Claim Submission, Admin Approval & Return ---")
        # Student Aarav logs in and claims the Dell laptop found in Library (found1)
        client.post('/login', data={'email': 'aarav.sharma@vsit.edu.in', 'password': 'Student@123'})
        found_laptop = Item.query.filter_by(item_name='Silver Dell Laptop in Padded Sleeve').first()

        # Submit claim
        claim_resp = client.post(f'/claim/{found_laptop.id}', data={
            'claim_reason': 'This is my Dell Inspiron 15 which I forgot during my study session.',
            'private_detail': 'Serial number tag ends in 9821, and the laptop sticker has my GitHub handle @aaravdev.',
            'supporting_information': 'I have the original tax invoice from Croma.',
            'contact_preference': 'Phone +91 98201 11223'
        }, follow_redirects=True)
        assert claim_resp.status_code == 200
        print("[PASS] Claim request submitted by claimant.")

        # Login as Admin
        client.get('/logout')
        admin_login = client.post('/login', data={'email': 'admin@vsit.edu.in', 'password': 'Admin@123'}, follow_redirects=True)
        assert admin_login.status_code == 200
        assert b"Campus Administration Center" in admin_login.data
        print("[PASS] Admin logged in successfully.")

        # Find the claim submitted by Aarav
        aarav_claim = Claim.query.filter_by(item_id=found_laptop.id, claimant_id=User.query.filter_by(email='aarav.sharma@vsit.edu.in').first().id).first()
        assert aarav_claim is not None

        # Admin approves claim
        approve_resp = client.post(f'/admin/claim/{aarav_claim.id}/approve', data={
            'admin_comment': 'Serial number verified against student laptop registry. Approved for collection.'
        }, follow_redirects=True)
        assert approve_resp.status_code == 200

        db.session.refresh(aarav_claim)
        db.session.refresh(found_laptop)
        assert aarav_claim.status == 'Approved'
        assert found_laptop.status == 'Claim Approved'
        print("[PASS] Admin approved claim. Item status updated to 'Claim Approved'.")

        # Admin marks item as returned
        return_resp = client.post(f'/admin/item/{found_laptop.id}/mark-returned', follow_redirects=True)
        assert return_resp.status_code == 200

        db.session.refresh(found_laptop)
        db.session.refresh(aarav_claim)
        assert found_laptop.status == 'Returned'
        assert aarav_claim.status == 'Completed'
        print("[PASS] Item marked as 'Returned'. Claim marked as 'Completed'.")

        # Verify notification sent to Aarav
        aarav_user = User.query.filter_by(email='aarav.sharma@vsit.edu.in').first()
        latest_notif = Notification.query.filter_by(user_id=aarav_user.id).order_by(Notification.created_at.desc()).first()
        assert latest_notif is not None
        assert "RETURNED" in latest_notif.message
        print(f"[PASS] Notification delivered to claimant: '{latest_notif.message}'")

    print("\n==================================================")
    print("ALL 4 KEY WORKFLOWS VERIFIED SUCCESSFULLY (100% PASS)!")
    print("==================================================")

if __name__ == '__main__':
    run_workflow_verifications()
