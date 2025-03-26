import bcrypt
import logging
from config import MIN_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, DATABASE
from database import DatabaseManager
from encryption import EncryptionManager


class AuthManager:

    def __init__(self, db_name=DATABASE):
        self.db = DatabaseManager(db_name)
        self.current_user = None

    def hash_password(self, password: str) -> str:
        """Hash the password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if a password matches its hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def register_user(self, username: str, password: str) -> str:
        """Registers a new user if the username is not taken."""
        query = self.db.execute_query("SELECT * FROM users WHERE username = ?", (username,))

        if query:
            return "Username already taken."

        elif len(username) < MIN_USERNAME_LENGTH:
            return f"Username must be at least {MIN_USERNAME_LENGTH} characters long."

        elif len(password) < MIN_PASSWORD_LENGTH:
            return f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

        hashed_password = self.hash_password(password)
        key_salt = EncryptionManager.generate_salt()

        # Generate a new encryption_key and encrypt it
        encryption_manager = EncryptionManager(password, key_salt)
        enc_encryption_key = encryption_manager.encrypt_encryption_key()

        # Store user in DB
        registration = self.db.execute_query(
            "INSERT INTO users (username, password, key_salt, encryption_key) VALUES (?, ?, ?, ?)",
            (username, hashed_password, key_salt, enc_encryption_key)
            )

        if registration:
            logging.info(f"User {username} registered successfully.")
            return "Registration successful."

        logging.error(f"Failed to register user {username}.")
        return "Registration failed."

    def login_user(self, username: str, password: str) -> str:
        """Verifies username, password, and decrypts the encryption key for session use."""
        query = self.db.execute_query("SELECT * FROM users WHERE username = ?", (username,))

        if not query:
            return "User not found."

        user_data = query[0]
        hashed_password = user_data["password"]

        if self.verify_password(password, hashed_password):
            self.current_user = user_data["user_id"]

            logging.info(f"User #{self.current_user} logged in successfully.")
            return "Login successful."

        return "Incorrect password."

    def logout_user(self) -> bool:
        """Logs out user from session"""
        if self.current_user:
            username = self.current_user
            self.current_user = None
            logging.info(f"User #{username} logged out successfully.")
            return True

        logging.warning("Logout failed: No user is currently logged in.")
        return False

    def is_logged_in(self) -> bool:
        """Checks if a user is currently logged in."""
        return self.current_user is not None

    def change_username(self, new_username: str) -> str:
        """Changes username if user is logged in."""
        if not self.is_logged_in():
            return "User not logged in."

        if len(new_username) < MIN_USERNAME_LENGTH:
            return f"Username must be at least {MIN_USERNAME_LENGTH} characters long."

        try:
            # Check whether user is already taken
            if self.db.execute_query("SELECT * FROM users WHERE username = ?", (new_username,)):
                return "Username already exists."

            # Update the username where the user_id matches
            result = self.db.execute_query(
                "UPDATE users SET username = ? WHERE user_id = ?",
                (new_username, self.current_user)
                )

            if result == 0:
                return "Username change failed."

            logging.info(f"User #{self.current_user} changed his username successfully.")
            return "Username changed successfully."

        except Exception as e:
            logging.error(f"Error changing username for User #{self.current_user}: {e}")
            return "An error occurred while changing the username."

    def change_password(self, old_password: str, new_password: str) -> str:
        """Changes password if user is logged in."""
        if not self.is_logged_in():
            return "User not logged in."

        if len(new_password) < MIN_PASSWORD_LENGTH:
            return f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."

        user = self.db.execute_query("SELECT * FROM users WHERE user_id = ?", (self.current_user,))[0]
        db_password = user["password"]
        if not self.verify_password(old_password, db_password):
            return "Old password is incorrect."

        enc = EncryptionManager(old_password, user["key_salt"], user["encryption_key"])
        enc.user_key = enc.derive_key(new_password, user["key_salt"])
        new_enc_encription_key = enc.encrypt_encryption_key()

        hashed_new_password = self.hash_password(new_password)

        try:
            result = self.db.execute_query(
                "UPDATE users SET password = ?, encryption_key = ? WHERE user_id = ?",
                (hashed_new_password, new_enc_encription_key, self.current_user)
                )
            if result == 0:
                return "Password change failed."

            logging.info(f"User #{self.current_user} changed his password successfully.")
            return "Password changed successfully."
        except Exception as e:
            logging.error(f"Error changing password for User #{self.current_user}: {e}")
            return "An error occurred while changing the password."
