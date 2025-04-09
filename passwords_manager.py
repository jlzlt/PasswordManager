import logging
from config import MIN_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, DATABASE
from database import DatabaseManager
from datetime import datetime
from encryption import EncryptionManager


class PasswordsManager:
    def __init__(self, user_password: str, user_salt: bytes, enc_encryption_key: str, user_id: int, db_name=DATABASE):
        self.db = DatabaseManager(db_name)
        self.user_password = user_password
        self.enc_encryption_key = enc_encryption_key
        self.user_id = user_id
        self.user_salt = user_salt

    def add_entry(self, name: str, username: str, password: str, website: str = None, comment: str = None):
        # Check user inputs
        if not name:
            return "Name field cannot be empty."
        elif not username:
            return "Username field cannot be empty."
        elif not password:
            return "Password field cannot be empty."
        comment_value = comment if comment else None
        website_value = website if website else None

        enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)
        encrypted_password, iv = enc.encrypt_password(password)

        result = self.db.execute_query(
            "INSERT INTO passwords (date_created, user_id, name, username, password, iv, website, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (self.current_time(), self.user_id, name, username, encrypted_password, iv, website_value, comment_value)
            )

        if result:
            logging.info(f"Entry for user #{self.user_id} successfully added.")
            return "Entry successfully added."

        logging.error(f"Failed to add entry for user #{self.user_id}.")
        return "Failed to add entry."

    def retrieve_entry(self, entry_id: int) -> dict:
        try:
            result = self.db.execute_query("SELECT * FROM passwords WHERE entry_id = ? AND user_id = ?", (entry_id, self.user_id))
            if not result:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return {}
            enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)
            result[0]["password"] = enc.decrypt_password(result[0]["password"], result[0]["iv"])
            return result[0]
        except Exception as e:
            logging.error(f"Failed fetch entry #{entry_id} from passwords table: {e}")
            raise RuntimeError(f"Error retrieving entry #{entry_id}: {e}") from e
        
    def get_entries(self, user_id: int, name: str = None) -> list:
        if not name:
            results_appended = []
            results = self.db.execute_query("SELECT * FROM passwords WHERE user_id = ?", (user_id,))
            enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)
            for result in results:
                result["password"] = enc.decrypt_password(result["password"], result["iv"])
                results_appended.append(result)
            return results_appended if results else []
        else:
            results_appended = []
            results = self.db.execute_query("SELECT * FROM passwords WHERE name = ? AND user_id = ?", (name, self.user_id))
            enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)
            for result in results:
                result["password"] = enc.decrypt_password(result["password"], result["iv"])
                results_appended.append(result)
            return results_appended if results else [] 

    def update_entry(self, entry_id: int, field: str, new_value: str):
        if field == "name":
            return(self.update_name(entry_id, new_value))
        elif field == "username":
            return(self.update_username(entry_id, new_value))
        elif field == "website":
            return(self.update_website(entry_id, new_value))
        elif field == "password":
            return(self.update_password(entry_id, new_value))
        elif field == "comment":
            return(self.update_comment(entry_id, new_value))
        else:
            return "Cannot update entry."

    def update_name(self, entry_id: int, name: str):
        if not name:
            return "Name field cannot be empty."

        try:
            rows_affected = self.db.execute_query(
                "UPDATE passwords SET name = ?, date_modified = ? WHERE entry_id = ? AND user_id = ?",
                (name, self.current_time(), entry_id, self.user_id)
                )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully updated name for entry #{entry_id}.")
            return "Name updated successfully."

        except Exception as e:
            logging.error(f"Failed to update name field for entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to update name field for entry #{entry_id}: {e}") from e

    def update_username(self, entry_id: int, username: str):
        if not username:
            return "Username field cannot be empty."

        try:
            rows_affected = self.db.execute_query(
                "UPDATE passwords SET username = ?, date_modified = ? WHERE entry_id = ? AND user_id = ?",
                (username, self.current_time(), entry_id, self.user_id)
                )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully updated username for entry #{entry_id}.")
            return "Username updated successfully."

        except Exception as e:
            logging.error(f"Failed to update username field for entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to update username field for entry #{entry_id}: {e}") from e
        
    def update_website(self, entry_id: int, website: str):
        try:
            website_value = website if website else None
            rows_affected = self.db.execute_query(
                "UPDATE passwords SET website = ?, date_modified = ? WHERE entry_id = ? AND user_id = ?",
                (website_value, self.current_time(), entry_id, self.user_id)
                )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully updated website for entry #{entry_id}.")
            return "Website updated successfully."

        except Exception as e:
            logging.error(f"Failed to update website field for entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to update website field for entry #{entry_id}: {e}") from e

    def update_comment(self, entry_id: int, comment: str):
        try:
            comment_value = comment if comment else None
            rows_affected = self.db.execute_query(
                "UPDATE passwords SET comment = ?, date_modified = ? WHERE entry_id = ? AND user_id = ?",
                (comment_value, self.current_time(), entry_id, self.user_id)
                )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully updated comment for entry #{entry_id}.")
            return "Comment updated successfully."

        except Exception as e:
            logging.error(f"Failed to update comment field for entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to update comment field for entry #{entry_id}: {e}") from e

    def update_password(self, entry_id: int, password: str):
        if not password:
            return "Password field cannot be empty"

        enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)
        encrypted_password, iv = enc.encrypt_password(password)

        try:
            rows_affected = self.db.execute_query(
                "UPDATE passwords SET password = ?, iv = ?, date_modified = ? WHERE entry_id = ? and user_id = ?",
                (encrypted_password, iv, self.current_time(), entry_id, self.user_id)
                )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully updated password for entry #{entry_id}.")
            return "Password updated successfully."

        except Exception as e:
            logging.error(f"Failed to update password field for entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to update password field for entry #{entry_id}: {e}") from e

    def delete_entry(self, entry_id: int):
        try:
            rows_affected = self.db.execute_query(
                "DELETE FROM passwords WHERE entry_id = ? and user_id = ?",
                (entry_id, self.user_id)
            )

            if rows_affected == 0:
                logging.warning(f"Entry #{entry_id} cannot be accessed.")
                return "Entry cannot be accessed."

            logging.info(f"Successfully deleted entry #{entry_id}.")
            return "Entry deleted successfully."

        except Exception as e:
            logging.error(f"Failed to delete entry #{entry_id}: {e}")
            raise RuntimeError(f"Failed to delete entry #{entry_id}: {e}") from e
        
    def check_entry(self, name: str, username: str, password: str):
        # Check user inputs
        if not name:
            return "Name field cannot be empty."
        elif not username:
            return "Username field cannot be empty."
        elif not password:
            return "Password field cannot be empty."

        enc = EncryptionManager(self.user_password, self.user_salt, self.enc_encryption_key)

        name_entries = self.db.execute_query(
            "SELECT * FROM passwords WHERE name = ? AND user_id = ?",
            (name, self.user_id)
        )

        if not name_entries:
            return "Entry does not exist."

        for entry in name_entries:
            if entry["username"] == username:
                if enc.decrypt_password(entry["password"], entry["iv"]) == password:
                    logging.info(f"Entry for user #{self.user_id} already exists.")
                    return "Entry already exists."
        
        return "Entry does not exist."

        
    def current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


