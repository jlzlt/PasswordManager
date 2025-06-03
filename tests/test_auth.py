import unittest
import os
import tempfile
from auth import AuthManager
from config import MIN_USERNAME_LENGTH, MIN_PASSWORD_LENGTH

class TestAuthManager(unittest.TestCase):
    # Setup the test environment
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.auth = AuthManager(self.temp_db.name)
        self.auth.db.create_tables()

    # Clean up the test environment
    def tearDown(self):
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            pass

    def test_register_user_success(self):
        """Test successful user registration"""
        result = self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        self.assertEqual(result, "Registration successful.")

    def test_register_user_short_username(self):
        """Test registration with short username"""
        result = self.auth.register_user(
            "a" * (MIN_USERNAME_LENGTH - 1),
            "testpassword123",
            "testpassword123"
        )
        self.assertEqual(result, f"Username must be at least {MIN_USERNAME_LENGTH} characters long.")

    def test_register_user_short_password(self):
        """Test registration with short password"""
        result = self.auth.register_user(
            "testuser",
            "a" * (MIN_PASSWORD_LENGTH - 1),
            "a" * (MIN_PASSWORD_LENGTH - 1)
        )
        self.assertEqual(result, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords"""
        result = self.auth.register_user(
            "testuser",
            "testpassword123",
            "differentpassword"
        )
        self.assertEqual(result, "Passwords do not match.")

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # First registration
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        # Second registration with same username
        result = self.auth.register_user(
            "testuser",
            "anotherpassword",
            "anotherpassword"
        )
        self.assertEqual(result, "Username already taken.")

    def test_login_success(self):
        """Test successful login"""
        # Register a user first
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        # Try to login
        result = self.auth.login_user("testuser", "testpassword123")
        self.assertEqual(result, "Login successful.")

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # Register a user first
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        # Try to login with wrong password
        result = self.auth.login_user("testuser", "wrongpassword")
        self.assertEqual(result, "Incorrect password.")

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        result = self.auth.login_user("nonexistent", "password123")
        self.assertEqual(result, "User not found.")

    def test_change_username_success(self):
        """Test successful username change"""
        # Register and login a user
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        self.auth.login_user("testuser", "testpassword123")
        # Change username
        result = self.auth.change_username("newusername")
        self.assertEqual(result, "Username changed successfully.")

    def test_change_username_not_logged_in(self):
        """Test username change when not logged in"""
        result = self.auth.change_username("newusername")
        self.assertEqual(result, "User not logged in.")

    def test_change_password_success(self):
        """Test successful password change"""
        # Register and login a user
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        self.auth.login_user("testuser", "testpassword123")
        # Change password
        result = self.auth.change_password("testpassword123", "newpassword123")
        self.assertEqual(result, "Password changed successfully.")

    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        # Register and login a user
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        self.auth.login_user("testuser", "testpassword123")
        # Try to change password with wrong current password
        result = self.auth.change_password("wrongpassword", "newpassword123")
        self.assertEqual(result, "Old password is incorrect.")

    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        # Register and login a user
        self.auth.register_user(
            "testuser",
            "testpassword123",
            "testpassword123"
        )
        self.auth.login_user("testuser", "testpassword123")
        # Try to change password with mismatched new passwords
        result = self.auth.change_password("testpassword123", "newpassword123")
        self.assertEqual(result, "Password changed successfully.")

if __name__ == '__main__':
    unittest.main() 