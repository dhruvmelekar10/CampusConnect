import unittest
from app import create_app
from config import TestConfig
from models import db, User

class AuthTestCase(unittest.TestCase):
    """Test suite for authentication, registration, sessions, and access control."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed test student and admin
        self.student = User(
            full_name="Test Student",
            email="student@vsit.edu.in",
            role="student",
            department="Computer Engineering"
        )
        self.student.set_password("Password123")

        self.admin = User(
            full_name="Test Admin",
            email="admin@vsit.edu.in",
            role="admin",
            department="Administration"
        )
        self.admin.set_password("AdminPass123")

        db.session.add_all([self.student, self.admin])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration_success(self):
        """Tests that a valid student can register successfully."""
        response = self.client.post('/register', data={
            'full_name': 'New Student',
            'email': 'new.student@vsit.edu.in',
            'role': 'student',
            'department': 'Information Technology',
            'phone': '+91 99999 88888',
            'password': 'SecretPassword123',
            'confirm_password': 'SecretPassword123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)
        user = User.query.filter_by(email='new.student@vsit.edu.in').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "New Student")
        self.assertTrue(user.check_password("SecretPassword123"))

    def test_registration_duplicate_email(self):
        """Tests that duplicate email registration is rejected."""
        response = self.client.post('/register', data={
            'full_name': 'Duplicate User',
            'email': 'student@vsit.edu.in',
            'role': 'student',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)

        self.assertIn(b"already exists", response.data)

    def test_registration_password_mismatch(self):
        """Tests validation error when password confirmation fails."""
        response = self.client.post('/register', data={
            'full_name': 'Mismatch User',
            'email': 'mismatch@vsit.edu.in',
            'role': 'student',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword'
        }, follow_redirects=True)

        self.assertIn(b"Passwords do not match", response.data)

    def test_login_successful(self):
        """Tests login with valid credentials."""
        response = self.client.post('/login', data={
            'email': 'student@vsit.edu.in',
            'password': 'Password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back", response.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['email'], 'student@vsit.edu.in')
            self.assertEqual(sess['role'], 'student')

    def test_login_invalid_password(self):
        """Tests login failure with an incorrect password."""
        response = self.client.post('/login', data={
            'email': 'student@vsit.edu.in',
            'password': 'WrongPassword!'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email or password", response.data)

    def test_logout(self):
        """Tests logging out clears the active session."""
        self.client.post('/login', data={
            'email': 'student@vsit.edu.in',
            'password': 'Password123'
        })
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b"logged out", response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)

    def test_unauthorized_admin_access(self):
        """Tests that a student cannot access the administrative dashboard."""
        self.client.post('/login', data={
            'email': 'student@vsit.edu.in',
            'password': 'Password123'
        })
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b"Administrator privileges required", response.data)

    def test_guest_redirect_from_protected_route(self):
        """Tests that unauthenticated guests are redirected to login when reporting items."""
        response = self.client.get('/report/lost', follow_redirects=True)
        self.assertIn(b"Please log in to access this feature", response.data)
        self.assertIn(b"CampusConnect Login", response.data)

if __name__ == '__main__':
    unittest.main()
