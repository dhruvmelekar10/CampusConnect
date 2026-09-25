import unittest
from datetime import date
from app import create_app
from config import TestConfig
from models import db, User, Item, Claim, Notification

class ClaimsTestCase(unittest.TestCase):
    """Test suite for the claims lifecycle, verification, and admin approval workflows."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Admin, Reporter, Claimant
        self.admin = User(full_name="Admin Officer", email="admin@vsit.edu.in", role="admin")
        self.admin.set_password("Admin123")

        self.reporter = User(full_name="Reporter Student", email="reporter@vsit.edu.in", role="student")
        self.reporter.set_password("Pass123")

        self.claimant = User(full_name="Claimant Student", email="claimant@vsit.edu.in", role="student")
        self.claimant.set_password("Pass123")

        db.session.add_all([self.admin, self.reporter, self.claimant])
        db.session.commit()

        # Seed a found item
        self.found_item = Item(
            reporter_id=self.reporter.id,
            item_type='Found',
            item_name='Leather Wallet',
            category='Wallet or Purse',
            description='Brown leather wallet found in Auditorium.',
            location='Main Auditorium',
            item_date=date.today(),
            status='Open'
        )
        db.session.add(self.found_item)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self, email, password="Pass123"):
        return self.client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

    def test_submit_claim_success(self):
        """Tests that a student can submit a valid ownership claim on a found item."""
        self._login("claimant@vsit.edu.in")
        response = self.client.post(f'/claim/{self.found_item.id}', data={
            'claim_reason': 'I lost my brown wallet during the afternoon presentation.',
            'private_detail': 'Contains college library card with roll number ME-2024-08.',
            'supporting_information': 'Purchased in 2025.'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"claim request has been submitted", response.data)

        # Verify claim record in database
        claim = Claim.query.filter_by(item_id=self.found_item.id, claimant_id=self.claimant.id).first()
        self.assertIsNotNone(claim)
        self.assertEqual(claim.status, 'Pending')

        # Verify item status transitioned to 'Claim Pending'
        reloaded_item = db.session.get(Item, self.found_item.id)
        self.assertEqual(reloaded_item.status, 'Claim Pending')

    def test_prevent_claiming_own_found_report(self):
        """Tests that a finder cannot claim an item they themselves reported finding."""
        self._login("reporter@vsit.edu.in")
        response = self.client.post(f'/claim/{self.found_item.id}', data={
            'claim_reason': 'Attempting to claim own reported item.',
            'private_detail': 'Any detail'
        }, follow_redirects=True)

        self.assertIn(b"cannot claim an item that you reported finding", response.data)

    def test_admin_approve_claim(self):
        """Tests that an administrator can approve a pending claim."""
        # Create pending claim
        claim = Claim(
            item_id=self.found_item.id,
            claimant_id=self.claimant.id,
            claim_reason="Belongs to me.",
            private_detail="Secret mark inside.",
            status="Pending"
        )
        db.session.add(claim)
        self.found_item.status = 'Claim Pending'
        db.session.commit()

        # Admin logs in and approves claim
        self._login("admin@vsit.edu.in", "Admin123")
        response = self.client.post(f'/admin/claim/{claim.id}/approve', data={
            'admin_comment': 'Proof verified against college records.'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"approved successfully", response.data)

        # Verify claim status
        reloaded_claim = db.session.get(Claim, claim.id)
        self.assertEqual(reloaded_claim.status, 'Approved')

        # Verify item status transitioned to 'Claim Approved'
        reloaded_item = db.session.get(Item, self.found_item.id)
        self.assertEqual(reloaded_item.status, 'Claim Approved')

        # Verify notification sent to claimant
        notif = Notification.query.filter_by(user_id=self.claimant.id, notification_type='claim_approved').first()
        self.assertIsNotNone(notif)
        self.assertIn("APPROVED", notif.message)

    def test_admin_reject_claim(self):
        """Tests that an administrator can reject a claim with a reason."""
        claim = Claim(
            item_id=self.found_item.id,
            claimant_id=self.claimant.id,
            claim_reason="Unverified claim.",
            private_detail="Wrong detail.",
            status="Pending"
        )
        db.session.add(claim)
        self.found_item.status = 'Claim Pending'
        db.session.commit()

        # Admin logs in and rejects
        self._login("admin@vsit.edu.in", "Admin123")
        response = self.client.post(f'/admin/claim/{claim.id}/reject', data={
            'admin_comment': 'Identifying detail does not match.'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        reloaded_claim = db.session.get(Claim, claim.id)
        self.assertEqual(reloaded_claim.status, 'Rejected')

        # Item status reverts to Open
        reloaded_item = db.session.get(Item, self.found_item.id)
        self.assertEqual(reloaded_item.status, 'Open')

    def test_admin_mark_item_returned(self):
        """Tests that an admin can mark an item as returned and complete approved claims."""
        claim = Claim(
            item_id=self.found_item.id,
            claimant_id=self.claimant.id,
            claim_reason="Verified owner.",
            private_detail="Valid serial number.",
            status="Approved"
        )
        db.session.add(claim)
        self.found_item.status = 'Claim Approved'
        db.session.commit()

        self._login("admin@vsit.edu.in", "Admin123")
        response = self.client.post(f'/admin/item/{self.found_item.id}/mark-returned', follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check item status is Returned
        reloaded_item = db.session.get(Item, self.found_item.id)
        self.assertEqual(reloaded_item.status, 'Returned')

        # Check claim status is Completed
        reloaded_claim = db.session.get(Claim, claim.id)
        self.assertEqual(reloaded_claim.status, 'Completed')

if __name__ == '__main__':
    unittest.main()
