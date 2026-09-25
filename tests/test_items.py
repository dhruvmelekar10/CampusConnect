import unittest
from datetime import date, timedelta
from app import create_app
from config import TestConfig
from models import db, User, Item

class ItemTestCase(unittest.TestCase):
    """Test suite for reporting, validating, searching, editing, and deleting items."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed two students
        self.user1 = User(full_name="Student One", email="one@vsit.edu.in", role="student")
        self.user1.set_password("Pass123")

        self.user2 = User(full_name="Student Two", email="two@vsit.edu.in", role="student")
        self.user2.set_password("Pass123")

        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _login(self, email="one@vsit.edu.in", password="Pass123"):
        return self.client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)

    def test_report_lost_item_success(self):
        """Tests reporting a lost item with valid data."""
        self._login()
        today_str = date.today().strftime('%Y-%m-%d')
        response = self.client.post('/report/lost', data={
            'item_name': 'Lenovo ThinkPad',
            'category': 'Laptop',
            'description': 'Black ThinkPad T14 laptop left on table 4.',
            'brand': 'Lenovo',
            'color': 'Black',
            'location': 'Library 1st Floor',
            'item_date': today_str,
            'approximate_time': '10:00 AM',
            'estimated_value': '45000'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        item = Item.query.filter_by(item_name='Lenovo ThinkPad').first()
        self.assertIsNotNone(item)
        self.assertEqual(item.item_type, 'Lost')
        self.assertEqual(item.reporter_id, self.user1.id)
        self.assertEqual(item.estimated_value, 45000.0)

    def test_report_found_item_success(self):
        """Tests reporting a found item with valid data."""
        self._login("two@vsit.edu.in")
        today_str = date.today().strftime('%Y-%m-%d')
        response = self.client.post('/report/found', data={
            'item_name': 'Keychain with 2 Keys',
            'category': 'Keys',
            'description': 'Two brass door keys with a green tag.',
            'brand': 'Godrej',
            'color': 'Silver and Brass',
            'location': 'Campus Canteen',
            'item_date': today_str
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        item = Item.query.filter_by(item_name='Keychain with 2 Keys').first()
        self.assertIsNotNone(item)
        self.assertEqual(item.item_type, 'Found')
        self.assertEqual(item.reporter_id, self.user2.id)

    def test_item_validation_future_date(self):
        """Tests that dates in the future are rejected."""
        self._login()
        future_date = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        response = self.client.post('/report/lost', data={
            'item_name': 'Calculator',
            'category': 'Electronic Accessory',
            'description': 'Scientific calculator.',
            'location': 'Lab 1',
            'item_date': future_date
        }, follow_redirects=True)

        self.assertIn(b"cannot be in the future", response.data)

    def test_item_validation_missing_required(self):
        """Tests that missing mandatory fields generates validation errors."""
        self._login()
        response = self.client.post('/report/lost', data={
            'item_name': '',  # missing name
            'category': 'Laptop',
            'description': 'Short',
            'location': ''
        }, follow_redirects=True)

        self.assertIn(b"Item name is required", response.data)

    def test_search_and_filtering(self):
        """Tests case-insensitive search and category filtering."""
        today = date.today()
        i1 = Item(reporter_id=self.user1.id, item_type='Lost', item_name='Sony Headphones', category='Electronic Accessory', description='Noise cancelling black headphones.', location='Library', item_date=today)
        i2 = Item(reporter_id=self.user2.id, item_type='Found', item_name='Blue Water Bottle', category='Other', description='Stainless steel blue bottle.', location='Canteen', item_date=today)
        db.session.add_all([i1, i2])
        db.session.commit()

        # Keyword search
        resp = self.client.get('/search?q=sony')
        self.assertIn(b"Sony Headphones", resp.data)
        self.assertNotIn(b"Blue Water Bottle", resp.data)

        # Category filter
        resp2 = self.client.get('/search?category=Other')
        self.assertIn(b"Blue Water Bottle", resp2.data)
        self.assertNotIn(b"Sony Headphones", resp2.data)

    def test_unauthorized_edit_prevention(self):
        """Tests that user2 cannot edit an item reported by user1."""
        item = Item(
            reporter_id=self.user1.id,
            item_type='Lost',
            item_name='Fastrack Watch',
            category='Jewellery',
            description='Black dial watch.',
            location='Gym',
            item_date=date.today()
        )
        db.session.add(item)
        db.session.commit()

        self._login("two@vsit.edu.in")
        response = self.client.post(f'/item/{item.id}/edit', data={
            'item_name': 'Hacked Watch Name',
            'category': 'Jewellery',
            'description': 'Attempting unauthorized modification.',
            'location': 'Gym',
            'item_date': date.today().strftime('%Y-%m-%d')
        }, follow_redirects=True)

        self.assertIn(b"not authorized to edit", response.data)
        # Verify db wasn't modified
        reloaded = db.session.get(Item, item.id)
        self.assertEqual(reloaded.item_name, 'Fastrack Watch')

if __name__ == '__main__':
    unittest.main()
