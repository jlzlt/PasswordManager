import unittest
import os
import tempfile
from passwords_manager import PasswordsManager
from auth import AuthManager
from encryption import EncryptionManager

class TestPasswordsManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Set up auth manager and create a test user
        self.auth = AuthManager(self.temp_db.name)
        self.auth.db.create_tables()
        self.auth.register_user("testuser", "testpassword123", "testpassword123")
        self.auth.login_user("testuser", "testpassword123")
        
        # Get user data
        self.user = self.auth.db.execute_query(
            "SELECT * FROM users WHERE user_id = ?", 
            (self.auth.current_user,)
        )[0]
        
        # Initialize passwords manager
        self.pwman = PasswordsManager(
            "testpassword123",
            self.user["key_salt"],
            self.user["encryption_key"],
            self.auth.current_user,
            self.temp_db.name
        )

    def tearDown(self):
        # Clean up the temporary database
        os.unlink(self.temp_db.name)

    def test_add_entry_success(self):
        """Test successful password entry addition"""
        result = self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        self.assertEqual(result, "Entry successfully added.")

    def test_add_entry_empty_name(self):
        """Test adding entry with empty name"""
        result = self.pwman.add_entry(
            "",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        self.assertEqual(result, "Name field cannot be empty.")

    def test_add_entry_empty_username(self):
        """Test adding entry with empty username"""
        result = self.pwman.add_entry(
            "Test Entry",
            "",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        self.assertEqual(result, "Username field cannot be empty.")

    def test_add_entry_empty_password(self):
        """Test adding entry with empty password"""
        result = self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "",
            "https://test.com",
            "Test comment"
        )
        self.assertEqual(result, "Password field cannot be empty.")

    def test_get_entries(self):
        """Test retrieving entries"""
        # Add a test entry
        self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        
        # Get entries
        entries = self.pwman.get_entries(self.auth.current_user)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Test Entry")
        self.assertEqual(entries[0]["username"], "testuser")
        self.assertEqual(entries[0]["website"], "https://test.com")
        self.assertEqual(entries[0]["comment"], "Test comment")

    def test_update_entry_name(self):
        """Test updating entry name"""
        # Add a test entry
        self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.auth.current_user)
        entry_id = entries[0]["entry_id"]
        
        # Update the name
        result = self.pwman.update_entry(entry_id, "name", "Updated Entry")
        self.assertEqual(result, "Name updated successfully.")
        
        # Verify the update
        entries = self.pwman.get_entries(self.auth.current_user)
        self.assertEqual(entries[0]["name"], "Updated Entry")

    def test_update_entry_password(self):
        """Test updating entry password"""
        # Add a test entry
        self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.auth.current_user)
        entry_id = entries[0]["entry_id"]
        
        # Update the password
        result = self.pwman.update_entry(entry_id, "password", "newpass123")
        self.assertEqual(result, "Password updated successfully.")

    def test_delete_entry(self):
        """Test deleting an entry"""
        # Add a test entry
        self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.auth.current_user)
        entry_id = entries[0]["entry_id"]
        
        # Delete the entry
        self.pwman.delete_entry(entry_id)
        
        # Verify deletion
        entries = self.pwman.get_entries(self.auth.current_user)
        self.assertEqual(len(entries), 0)

    def test_check_entry_exists(self):
        """Test checking if an entry exists"""
        # Add a test entry
        self.pwman.add_entry(
            "Test Entry",
            "testuser",
            "testpass123",
            "https://test.com",
            "Test comment"
        )
        
        # Check if entry exists
        result = self.pwman.check_entry("Test Entry", "testuser", "testpass123")
        self.assertEqual(result, "Entry already exists.")

    def test_check_entry_nonexistent(self):
        """Test checking if a nonexistent entry exists"""
        result = self.pwman.check_entry("Nonexistent", "testuser", "testpass123")
        self.assertEqual(result, "Entry does not exist.")

if __name__ == '__main__':
    unittest.main() 