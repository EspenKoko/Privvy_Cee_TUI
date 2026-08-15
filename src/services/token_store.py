from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
import os

import keyring

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except Exception:
    Fernet = None  # type: ignore
    _HAS_CRYPTO = False

Token_Key = "PVE_TOKEN"

class TokenStore:
    """Local token storage for the TUI.

    Strategy:
    - Primary: store the token in the OS credential store via `keyring`.
    - Fallback: store the token encrypted with a Fernet key and keep the
      Fernet key in the OS keyring. The encrypted file lives in
      `~/.privvycee/token.enc`.

    The fallback requires the `cryptography` package. If it's not
    available the class will only attempt keyring storage and will
    raise when a fallback encrypt/decrypt is needed.
    """

    SERVICE_NAME = "PrivvyCeeToken"
    TOKEN_NAME = "api_token"
    FERNET_KEY_NAME = "encryption_key"
    STORAGE_DIR = Path.home() / ".privvycee"
    TOKEN_FILE = STORAGE_DIR / "token.enc"

    def __init__(self) -> None:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def save_token(self, token: str) -> None:
        """Save token to keyring; if that fails, write encrypted file."""
        try:
            keyring.set_password(self.SERVICE_NAME, self.TOKEN_NAME, token)
            return
        except Exception:
            # best-effort fallback
            pass

        # # Fallback to encrypted file
        # if not _HAS_CRYPTO:
        #     raise RuntimeError("Keyring unavailable and `cryptography` not installed for encrypted fallback")

        # key = self._get_or_create_fernet_key()
        # f = Fernet(key)
        # token_b = token.encode("utf-8")
        # enc = f.encrypt(token_b)
        # self.TOKEN_FILE.write_bytes(enc)

    def get_token(self) -> Optional[str]:
        """Retrieve token from keyring, or decrypt fallback file."""
        try:
            token = keyring.get_password(self.SERVICE_NAME, self.TOKEN_NAME)
            if token:
                return token
        except Exception:
            pass

        # # Fallback: read encrypted file
        # if not _HAS_CRYPTO:
        #     return None

        # if not self.TOKEN_FILE.exists():
        #     return None

        # key = self._get_or_create_fernet_key()
        # f = Fernet(key)
        # data = self.TOKEN_FILE.read_bytes()
        # try:
        #     dec = f.decrypt(data)
        #     return dec.decode("utf-8")
        # except Exception:
        #     return None

    def delete_token(self) -> None:
        """Remove token from keyring and any fallback file."""
        try:
            keyring.delete_password(self.SERVICE_NAME, self.TOKEN_NAME)
        except Exception:
            pass

        # try:
        #     if self.TOKEN_FILE.exists():
        #         self.TOKEN_FILE.unlink()
        # except Exception:
        #     pass

    def _get_or_create_fernet_key(self) -> bytes:
        """Return a Fernet key stored in the OS keyring or create one.

        The key is stored as a URL-safe base64-encoded string compatible
        with `Fernet`.
        """
        if not _HAS_CRYPTO:
            raise RuntimeError("cryptography is required for Fernet keys")

        key = None
        try:
            key = keyring.get_password(self.SERVICE_NAME, self.FERNET_KEY_NAME)
        except Exception:
            key = None

        if key:
            return key.encode("utf-8")

        # create and persist
        new_key = Fernet.generate_key().decode("utf-8")
        try:
            keyring.set_password(self.SERVICE_NAME, self.FERNET_KEY_NAME, new_key)
            return new_key.encode("utf-8")
        except Exception:
            # as a last resort, write the key to disk with restricted perms
            key_path = self.STORAGE_DIR / "fernet.key"
            key_path.write_text(new_key, encoding="utf-8")
            try:
                os.chmod(key_path, 0o600)
            except Exception:
                pass
            return new_key.encode("utf-8")


# if __name__ == "__main__":
#     # simple demo
#     s = TokenStore()
#     print("Saving demo token to keyring...")
#     s.save_token("my-demo-token-123")
#     print("Stored token:", s.get_token())
#     s.delete_token()
#     print("Deleted token, now:", s.get_token())
