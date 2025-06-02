import unittest
import os
import tempfile
import sqlite3
from database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.db.create_tables()

    def tearDown(self):
        # Now try to delete the temporary file
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            # If we still can't delete it, that's okay - it will be cleaned up later
            pass

    def test_create_tables(self):
        """Test that tables are created correctly"""
        # Check if users table exists
        result = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        self.assertTrue(result)

        # Check if passwords table exists
        result = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='passwords'"
        )
        self.assertTrue(result)

    def test_insert_user(self):
        """Test inserting a user"""
        result = self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the user was inserted
        users = self.db.execute_query("SELECT * FROM users WHERE username = ?", ("testuser",))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "testuser")
        self.assertEqual(users[0]["password"], "hashedpass")
        self.assertEqual(users[0]["key_salt"], "salt")
        self.assertEqual(users[0]["encryption_key"], "key")

    def test_insert_password(self):
        """Test inserting a password entry"""
        # First create a user
        self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )
        user = self.db.execute_query("SELECT user_id FROM users WHERE username = ?", ("testuser",))[0]

        # Insert a password entry
        result = self.db.execute_query(
            """INSERT INTO passwords 
               (date_created, user_id, name, username, password, iv, website, comment) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("2024-01-01", user["user_id"], "Test Entry", "testuser", "encryptedpass", "iv", "https://test.com", "Test comment")
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the password entry was inserted
        entries = self.db.execute_query(
            "SELECT * FROM passwords WHERE name = ? AND user_id = ?",
            ("Test Entry", user["user_id"])
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Test Entry")
        self.assertEqual(entries[0]["username"], "testuser")
        self.assertEqual(entries[0]["password"], "encryptedpass")
        self.assertEqual(entries[0]["website"], "https://test.com")
        self.assertEqual(entries[0]["comment"], "Test comment")

    def test_update_user(self):
        """Test updating a user"""
        # First create a user
        self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )

        # Update the user
        result = self.db.execute_query(
            "UPDATE users SET username = ? WHERE username = ?",
            ("newusername", "testuser")
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the update
        users = self.db.execute_query("SELECT * FROM users WHERE username = ?", ("newusername",))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "newusername")

    def test_update_password(self):
        """Test updating a password entry"""
        # First create a user and password entry
        self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )
        user = self.db.execute_query("SELECT user_id FROM users WHERE username = ?", ("testuser",))[0]
        
        self.db.execute_query(
            """INSERT INTO passwords 
               (date_created, user_id, name, username, password, iv, website, comment) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("2024-01-01", user["user_id"], "Test Entry", "testuser", "encryptedpass", "iv", "https://test.com", "Test comment")
        )

        # Update the password entry
        result = self.db.execute_query(
            "UPDATE passwords SET name = ? WHERE name = ? AND user_id = ?",
            ("Updated Entry", "Test Entry", user["user_id"])
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the update
        entries = self.db.execute_query(
            "SELECT * FROM passwords WHERE name = ? AND user_id = ?",
            ("Updated Entry", user["user_id"])
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "Updated Entry")

    def test_delete_user(self):
        """Test deleting a user"""
        # First create a user
        self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )

        # Delete the user
        result = self.db.execute_query(
            "DELETE FROM users WHERE username = ?",
            ("testuser",)
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the deletion
        users = self.db.execute_query("SELECT * FROM users WHERE username = ?", ("testuser",))
        self.assertEqual(len(users), 0)

    def test_delete_password(self):
        """Test deleting a password entry"""
        # First create a user and password entry
        self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            ("testuser", "hashedpass", "salt", "key")
        )
        user = self.db.execute_query("SELECT user_id FROM users WHERE username = ?", ("testuser",))[0]
        
        self.db.execute_query(
            """INSERT INTO passwords 
               (date_created, user_id, name, username, password, iv, website, comment) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("2024-01-01", user["user_id"], "Test Entry", "testuser", "encryptedpass", "iv", "https://test.com", "Test comment")
        )

        # Delete the password entry
        result = self.db.execute_query(
            "DELETE FROM passwords WHERE name = ? AND user_id = ?",
            ("Test Entry", user["user_id"])
        )
        self.assertEqual(result, 1)  # One row affected

        # Verify the deletion
        entries = self.db.execute_query(
            "SELECT * FROM passwords WHERE name = ? AND user_id = ?",
            ("Test Entry", user["user_id"])
        )
        self.assertEqual(len(entries), 0)

    def test_invalid_query(self):
        """Test handling of invalid SQL query"""
        with self.assertRaises(RuntimeError):
            self.db.execute_query("INVALID SQL QUERY")

    def test_invalid_parameters(self):
        """Test handling of invalid parameters"""
        with self.assertRaises(RuntimeError):
            self.db.execute_query(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("testuser",)  # Missing parameter
            )

if __name__ == '__main__':
    unittest.main() 