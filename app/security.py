"""Local session-key setup and validation of post-login return paths."""

import os
from pathlib import Path
import secrets
from urllib.parse import unquote, urlsplit


def load_secret_key(instance_path):
    """Prefer SECRET_KEY from the environment, otherwise persist a local random key."""
    configured = os.environ.get('SECRET_KEY')
    if configured:
        if len(configured.strip()) < 32:
            raise RuntimeError('SECRET_KEY must contain at least 32 characters. Use a long random value.')
        return configured

    key_path = Path(instance_path) / 'secret_key'
    key_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Exclusive creation avoids replacing a key that already signs active sessions.
        descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        key = key_path.read_text(encoding='ascii').strip()
        if len(key) < 32:
            raise RuntimeError('The local instance/secret_key is invalid. Restore it or configure SECRET_KEY.')
        return key
    else:
        with os.fdopen(descriptor, 'w', encoding='ascii') as key_file:
            key = secrets.token_hex(32)
            key_file.write(key)
        return key


def is_local_redirect_target(target):
    """Allow root-relative paths only, rejecting URL and encoded separator tricks."""
    if not target:
        return False
    candidate = target
    # Decode defensively for validation; return the original URL to Flask unchanged.
    for _ in range(5):
        if (not candidate.startswith('/') or candidate.startswith('//')
                or '\\' in candidate
                or any(ord(character) < 32 or ord(character) == 127 for character in candidate)):
            return False
        try:
            parts = urlsplit(candidate)
            if parts.scheme or parts.netloc:
                return False
            decoded = unquote(candidate, errors='strict')
        except (ValueError, UnicodeError):
            return False
        if decoded == candidate:
            return True
        candidate = decoded
    return False
