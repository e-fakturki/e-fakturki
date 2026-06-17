from cryptography.fernet import Fernet

from backend.settings import settings


class Encryptor:
    """Service for encrypting and decrypting data."""

    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_SECRET_KEY.get_secret_value())

    def encrypt_bytes(self, text: bytes) -> bytes:
        """Encrypt bytes."""
        return self.fernet.encrypt(text)

    def encrypt_text(self, text: str) -> bytes:
        """Encrypt text."""
        return self.fernet.encrypt(text.encode())

    def decrypt_text(self, text: str) -> str:
        """Decrypt text."""
        return self.fernet.decrypt(text).decode()
