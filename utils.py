import base64
import binascii
import re
import urllib.parse

def is_base64(s: str) -> bool:
    """Checks if a string could be Base64 encoded."""
    if not s or not isinstance(s, str):
        return False
    # Basic regex for Base64: allows A-Z, a-z, 0-9, +, /, and optional trailing = or ==
    return bool(re.fullmatch(r"^[A-Za-z0-9+/]*={0,2}$", s.strip()))

def decode_base64(s: str) -> bytes:
    """Decodes a Base64 string to bytes."""
    try:
        return base64.b64decode(s.strip())
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 encoding: {e}")

def encode_base64(data: bytes) -> str:
    """Encodes bytes to a Base64 string."""
    return base64.b64encode(data).decode('utf-8')

def url_encode(s: str) -> str:
    """URL encodes a string safely for query parameters."""
    return urllib.parse.quote_plus(s)

def url_decode(s: str) -> str:
    """URL decodes a string."""
    return urllib.parse.unquote(s)
