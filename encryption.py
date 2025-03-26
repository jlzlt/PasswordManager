import base64
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class EncryptionManager:
    def __init__(self, user_password: str, user_salt: bytes, enc_encryption_key: str = None):
        """
        Must be initialize with either:
        - user_password + user_salt (Registration: generates an encryption key during registration)
        - user_password + use_salt + encrypted_encryption_key (Login: Decrypts encrypted encryption key)
        """
        self.user_key = self.derive_key(user_password, user_salt)
        self.user_password = user_password

        if enc_encryption_key:
            # Convert from Base64 to bytes before decrypting
            encrypted_bytes = base64.b64decode(enc_encryption_key)
            self.encryption_key = self.decrypt_encryption_key(encrypted_bytes)
        else:
            # Registration: Generate a new encryption key
            self.encryption_key = os.urandom(32)

    def derive_key(self, user_password: str, user_salt: bytes) -> bytes:
        """Derives a 32-byte key from the user's password and salt using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            user_password.encode(),
            user_salt,
            100000
        )

    def encrypt_encryption_key(self) -> str:
        """Encrypts the encryption key using the user_key and returns it as a base64 string."""
        iv = os.urandom(16)
        cipher = AES.new(self.user_key, AES.MODE_CBC, iv)
        encrypted_key = cipher.encrypt(pad(self.encryption_key, AES.block_size))
        return base64.b64encode(iv + encrypted_key).decode("utf-8")

    def decrypt_encryption_key(self, encrypted_key: bytes) -> bytes:
        """Decrypts the encryption key using the user_key."""
        try:
            cipher = AES.new(self.user_key, AES.MODE_CBC, iv=encrypted_key[:16])
            decrypted = unpad(cipher.decrypt(encrypted_key[16:]), AES.block_size)
            return decrypted
        except (ValueError, KeyError):
            raise ValueError("Failed to decrypt encryption key.")

    def encrypt_password(self, plain_password: str) -> tuple[str, str]:
        """Encrypts a password using the derived key."""
        # Generate random initialization vector for encryption
        iv = os.urandom(16) # AES block size is 16 bytes

        # Encrypt the password using AES with the derived key and the generated IV
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        encrypted_password = cipher.encrypt(pad(plain_password.encode(), AES.block_size))

        # Convert the encrypted password and IV to base64 for easy storage
        encrypted_password_base64 = base64.b64encode(encrypted_password).decode("utf-8")
        iv_base64 = base64.b64encode(iv).decode("utf-8")

        # Return encrypted password and the IV for database storage
        return encrypted_password_base64, iv_base64

    def decrypt_password(self, encrypted_password_base64: str, iv_base64: str) -> str:
        """Decrypts an encrypted password using the derived key."""
        # Convert the encrypted password and IV from base64 to bytes
        encrypted_password = base64.b64decode(encrypted_password_base64)
        iv = base64.b64decode(iv_base64)

        # Decrypt the password using AES with the derived key and the IV
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        decrypted_password = unpad(cipher.decrypt(encrypted_password), AES.block_size)

        # Return the decrypted password as a string
        return decrypted_password.decode("utf-8")

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a random salt for key derivation."""
        return os.urandom(16)
