import unittest
import os
import tempfile
import sqlite3
from passwords_manager import PasswordsManager
from auth import AuthManager
from encryption import EncryptionManager

class TestPasswordsManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Initialize AuthManager with the temporary database
        self.auth = AuthManager()
        self.auth.db.db_path = self.temp_db.name
        
        # Register a test user
        self.auth.register_user("testuser", "testpass", "testpass")
        
        # Get user data from database
        user_data = self.auth.db.execute_query(
            "SELECT * FROM users WHERE username = ?",
            ("testuser",)
        )[0]
        
        # Initialize PasswordsManager with user data
        self.pwman = PasswordsManager(
            "testpass",
            user_data["key_salt"],
            user_data["encryption_key"],
            user_data["user_id"]
        )
        
        # Clean up any existing entries
        self.pwman.db.execute_query("DELETE FROM passwords WHERE user_id = ?", (self.pwman.user_id,))

    def tearDown(self):
        # Now try to delete the temporary file
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            # If we still can't delete it, that's okay - it will be cleaned up later
            pass

    def test_add_entry_success(self):
        """Test adding a password entry successfully"""
        result = self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        self.assertEqual(result, "Entry successfully added.")

    def test_add_entry_empty_name(self):
        """Test adding an entry with empty name"""
        result = self.pwman.add_entry("", "testuser", "testpass", "test.com", "Test comment")
        self.assertEqual(result, "Name field cannot be empty.")

    def test_add_entry_empty_username(self):
        """Test adding an entry with empty username"""
        result = self.pwman.add_entry("Test Entry", "", "testpass", "test.com", "Test comment")
        self.assertEqual(result, "Username field cannot be empty.")

    def test_add_entry_empty_password(self):
        """Test adding an entry with empty password"""
        result = self.pwman.add_entry("Test Entry", "testuser", "", "test.com", "Test comment")
        self.assertEqual(result, "Password field cannot be empty.")

    def test_get_entries(self):
        """Test retrieving entries for the current user"""
        # Add a test entry
        self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        
        # Get entries
        entries = self.pwman.get_entries(self.pwman.user_id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Test Entry")
        self.assertEqual(entries[0]["username"], "testuser")
        self.assertEqual(entries[0]["website"], "test.com")
        self.assertEqual(entries[0]["comment"], "Test comment")

    def test_update_entry_name(self):
        """Test updating an entry's name"""
        # Add a test entry
        self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.pwman.user_id)
        entry_id = entries[0]["entry_id"]
        
        # Update the name
        result = self.pwman.update_entry(entry_id, "name", "Updated Name")
        self.assertEqual(result, "Name updated successfully.")
        
        # Verify the update
        entries = self.pwman.get_entries(self.pwman.user_id)
        self.assertEqual(entries[0]["name"], "Updated Name")

    def test_update_entry_password(self):
        """Test updating an entry's password"""
        # Add a test entry
        self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.pwman.user_id)
        entry_id = entries[0]["entry_id"]
        
        # Update the password
        result = self.pwman.update_entry(entry_id, "password", "newpass")
        self.assertEqual(result, "Password updated successfully.")
        
        # Verify the update
        entries = self.pwman.get_entries(self.pwman.user_id)
        self.assertEqual(entries[0]["password"], "newpass")

    def test_delete_entry(self):
        """Test deleting an entry"""
        # Add a test entry
        self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        
        # Get the entry ID
        entries = self.pwman.get_entries(self.pwman.user_id)
        entry_id = entries[0]["entry_id"]
        
        # Delete the entry
        self.pwman.delete_entry(entry_id)
        
        # Verify deletion
        entries = self.pwman.get_entries(self.pwman.user_id)
        self.assertEqual(len(entries), 0)

    def test_check_entry_exists(self):
        """Test checking if an entry exists"""
        # Add a test entry
        self.pwman.add_entry("Test Entry", "testuser", "testpass", "test.com", "Test comment")
        
        # Check if it exists
        result = self.pwman.check_entry("Test Entry", "testuser", "testpass")
        self.assertEqual(result, "Entry already exists.")

    def test_check_entry_nonexistent(self):
        """Test checking for a nonexistent entry"""
        result = self.pwman.check_entry("Nonexistent", "testuser", "testpass")
        self.assertEqual(result, "Entry does not exist.")

if __name__ == '__main__':
    unittest.main() 