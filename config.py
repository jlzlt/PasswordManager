import logging

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE = "passwords.db"
MIN_USERNAME_LENGTH = 1
MAX_USERNAME_LENGTH = 15
MIN_PASSWORD_LENGTH = 4
DEBUG_MODE = True
VERSION = "1.0.0"