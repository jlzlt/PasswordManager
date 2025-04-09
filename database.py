import logging
import sqlite3
from config import DATABASE

class DatabaseManager:

    def __init__(self, db_name=DATABASE):
        self.db_name = db_name
        self.create_tables()

    
    def create_tables(self):
        """Create Users and Passwords tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Initialize database if it's not there
                cursor.executescript("""

                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        key_salt BLOB NOT NULL,
                        encryption_key TEXT NOT NULL,
                        date_created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        date_modified TEXT
                    );

                    CREATE TABLE IF NOT EXISTS passwords (
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        website TEXT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        iv TEXT NOT NULL,
                        comment TEXT,
                        date_created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        date_modified TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    );
                                     
                    CREATE INDEX IF NOT EXISTS idx_passwords_user_id ON passwords(user_id);
                    CREATE INDEX IF NOT EXISTS idx_passwords_name ON passwords(name);
                    CREATE INDEX IF NOT EXISTS idx_passwords_website ON passwords(website);
                    CREATE INDEX IF NOT EXISTS idx_passwords_username ON passwords(username);

                """)

                conn.commit()

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise RuntimeError(f"Database error: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Unexpected error: {e}")


    def execute_query(self, query, params=None):
        """Execute a query with optional parameteres and return results if needed."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row # Enable dictionary-like access
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                conn.commit()

                if query.strip().upper().startswith("SELECT"):
                    return [dict(row) for row in cursor.fetchall()] # Return as list of dictionaries

                return cursor.rowcount # Return number of affected rows for UPDATE/INSERT/DELETE

        except sqlite3.Error as e:
           logging.error(f"Database error: {e}")
           raise RuntimeError(f"Database error: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Unexpected error: {e}")
        
    def logout(self):
        """Close the database connection."""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
                logging.info("Database connection closed.")
        except sqlite3.Error as e:
            logging.error(f"Error closing database connection: {e}")
            raise RuntimeError(f"Error closing database connection: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Unexpected error: {e}")


if __name__ == "__main__":
    db = DatabaseManager()
