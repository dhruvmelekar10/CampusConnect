import unittest
from datetime import date
from app import create_app
from config import TestConfig
from models import db, User, Item, Claim, Match, Notification

class DatabaseTestCase(unittest.TestCase):
    """Test suite for database tables, foreign keys, and admin database explorer."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed admin and student
        self.admin = User(full_name="DB Admin", email="admin@vsit.edu.in", role="admin")
        self.admin.set_password("Admin123")

        self.student = User(full_name="DB Student", email="student@vsit.edu.in", role="student")
        self.student.set_password("Pass123")

        db.session.add_all([self.admin, self.student])
        db.session.commit()

        # Seed test item
        self.item = Item(
            reporter_id=self.student.id,
            item_type='Lost',
            item_name='Sample Laptop',
            category='Laptop',
            description='Test laptop description',
            location='Library',
            item_date=date.today(),
            status='Open'
        )
        db.session.add(self.item)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_database_tables_exist(self):
        """Verifies that all 5 required relational tables exist."""
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        for required_table in ['users', 'items', 'matches', 'claims', 'notifications']:
            self.assertIn(required_table, table_names)

    def test_student_blocked_from_database_explorer(self):
        """Verifies that non-admin students cannot access /admin/database."""
        self.client.post('/login', data={'email': 'student@vsit.edu.in', 'password': 'Pass123'})
        resp = self.client.get('/admin/database')
        self.assertEqual(resp.status_code, 302)

    def test_admin_access_database_explorer(self):
        """Verifies that admin can access /admin/database."""
        self.client.post('/login', data={'email': 'admin@vsit.edu.in', 'password': 'Admin123'})
        resp = self.client.get('/admin/database')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Database Explorer", resp.data)
        self.assertIn(b"Live SQL Query Console", resp.data)

    def test_admin_execute_valid_select_query(self):
        """Verifies that admin can execute SELECT queries via web console."""
        self.client.post('/login', data={'email': 'admin@vsit.edu.in', 'password': 'Admin123'})
        resp = self.client.post('/admin/database', data={
            'query': 'SELECT item_name, category FROM items;'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Sample Laptop", resp.data)
        self.assertIn(b"Executed in", resp.data)

    def test_admin_console_rejects_destructive_query(self):
        """Verifies that DROP or DELETE queries are rejected with security error."""
        self.client.post('/login', data={'email': 'admin@vsit.edu.in', 'password': 'Admin123'})
        resp = self.client.post('/admin/database', data={
            'query': 'DROP TABLE items;'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Security Policy: Only read-only queries", resp.data)

    def test_database_downloads(self):
        """Verifies that database files can be downloaded by admin."""
        self.client.post('/login', data={'email': 'admin@vsit.edu.in', 'password': 'Admin123'})
        resp_db = self.client.get('/admin/database/download-db')
        self.assertEqual(resp_db.status_code, 200)

        resp_sql = self.client.get('/admin/database/download-sql')
        self.assertEqual(resp_sql.status_code, 200)

if __name__ == '__main__':
    unittest.main()
