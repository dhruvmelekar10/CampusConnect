import unittest
from datetime import date
from app import create_app
from config import TestConfig
from models import db, User, Item, Match, Notification
from services.matching_service import calculate_match_score, run_matching_for_item

class MatchingTestCase(unittest.TestCase):
    """Test suite for the explainable smart matching engine."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed two users
        self.user_lost = User(full_name="User Lost", email="lost@vsit.edu.in", role="student")
        self.user_lost.set_password("Pass123")

        self.user_found = User(full_name="User Found", email="found@vsit.edu.in", role="student")
        self.user_found.set_password("Pass123")

        db.session.add_all([self.user_lost, self.user_found])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_perfect_match_score_100(self):
        """Tests that identical attributes yield a 100-point score and transparent reasons."""
        lost = Item(
            reporter_id=self.user_lost.id,
            item_type='Lost',
            item_name='Apple MacBook Pro 14',
            category='Laptop',
            brand='Apple',
            color='Space Grey',
            location='Library 2nd Floor',
            description='MacBook Pro with sticker on keyboard palm rest.',
            item_date=date.today()
        )

        found = Item(
            reporter_id=self.user_found.id,
            item_type='Found',
            item_name='Apple MacBook Pro 14',
            category='Laptop',
            brand='Apple',
            color='Space Grey',
            location='Library 2nd Floor',
            description='MacBook Pro with sticker on keyboard.',
            item_date=date.today()
        )

        score, reasons, reason_text = calculate_match_score(lost, found)
        self.assertEqual(score, 100)
        self.assertIn("Same category", reasons)
        self.assertIn("Similar item name", reasons)
        self.assertIn("Same brand", reasons)
        self.assertIn("Same color", reasons)
        self.assertIn("Same or nearby location", reasons)
        self.assertIn("Similar description keywords", reasons)
        self.assertTrue(len(reason_text) > 10)

    def test_partial_match_above_threshold(self):
        """Tests that category (+30) and similar name (+25) meet the >= 50 points threshold."""
        lost = Item(
            reporter_id=self.user_lost.id,
            item_type='Lost',
            item_name='Physics Notes Notebook',
            category='Books or Notes',
            brand=None,
            color='Red',
            location='Hostel Block A',
            description='Semester 3 notebook.',
            item_date=date.today()
        )

        found = Item(
            reporter_id=self.user_found.id,
            item_type='Found',
            item_name='Physics Notebook',
            category='Books or Notes',
            brand=None,
            color='Green',
            location='Auditorium',
            description='Classroom notes inside.',
            item_date=date.today()
        )

        score, reasons, _ = calculate_match_score(lost, found)
        # Category (+30) + Similar Name (+25) = 55 points
        self.assertGreaterEqual(score, 50)
        self.assertIn("Same category", reasons)
        self.assertIn("Similar item name", reasons)

    def test_match_below_threshold_ignored(self):
        """Tests that different category and name attributes score below 50."""
        lost = Item(
            reporter_id=self.user_lost.id,
            item_type='Lost',
            item_name='Water Flask',
            category='Other',
            brand='Milton',
            color='Silver',
            location='Library',
            description='Insulated bottle.',
            item_date=date.today()
        )

        found = Item(
            reporter_id=self.user_found.id,
            item_type='Found',
            item_name='Dell Charger',
            category='Electronic Accessory',
            brand='Dell',
            color='Black',
            location='Library',
            description='Laptop adapter.',
            item_date=date.today()
        )

        score, reasons, _ = calculate_match_score(lost, found)
        # Only location matches (+10)
        self.assertLess(score, 50)

    def test_run_matching_creates_match_and_notifications(self):
        """Tests that run_matching_for_item creates Match records and dispatches alerts."""
        # Create existing found item
        found = Item(
            reporter_id=self.user_found.id,
            item_type='Found',
            item_name='Wildcraft Bag',
            category='Bag',
            brand='Wildcraft',
            color='Black',
            location='Canteen',
            description='College bag with books.',
            item_date=date.today(),
            status='Open'
        )
        db.session.add(found)
        db.session.commit()

        # Newly reported lost item matching found item
        lost = Item(
            reporter_id=self.user_lost.id,
            item_type='Lost',
            item_name='Wildcraft Backpack',
            category='Bag',
            brand='Wildcraft',
            color='Black',
            location='Canteen',
            description='College backpack with drawing tools.',
            item_date=date.today(),
            status='Open'
        )
        db.session.add(lost)
        db.session.commit()

        matches = run_matching_for_item(lost)
        self.assertEqual(len(matches), 1)
        self.assertGreaterEqual(matches[0].match_score, 50)

        # Verify items status transitioned to 'Possible Match'
        self.assertEqual(lost.status, 'Possible Match')
        self.assertEqual(found.status, 'Possible Match')

        # Verify in-app notifications generated for both users
        notifs_lost = Notification.query.filter_by(user_id=self.user_lost.id).all()
        notifs_found = Notification.query.filter_by(user_id=self.user_found.id).all()
        self.assertEqual(len(notifs_lost), 1)
        self.assertEqual(len(notifs_found), 1)
        self.assertIn("Smart Match Alert", notifs_lost[0].message)

if __name__ == '__main__':
    unittest.main()
