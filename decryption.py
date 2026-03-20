import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Padding
from utils import decode_base64, url_decode

BLOCK_SIZE = 16

class DecryptionError(Exception):
    """Base class for custom decryption errors."""
    pass

class EncodingError(DecryptionError):
    """Raised when the input is not properly URL or Base64 encoded."""
    pass

class IntegrityError(DecryptionError):
    """Raised when the message fails integrity verification."""
    pass

class PaddingError(DecryptionError):
    """Raised when the padding is invalid."""
    pass

class JSONFormatError(DecryptionError):
    """Raised when the decrypted message is not valid JSON."""
    pass

def decrypt(encrypted_msg_b64: str, encrypt_key_b64: str, hash_key_b64: str) -> bytes:
    """Decrypts and verifies the integrity of a message.

    Args:
        encrypted_msg_b64: Base64 encoded, URL encoded message
        encrypt_key_b64: Base64 encoded encryption key
        hash_key_b64: Base64 encoded hash key

    Returns:
        Decrypted message bytes.

    Raises:
        EncodingError: If the input is not properly encoded.
        IntegrityError: If message integrity verification fails.
        PaddingError: If the padding is invalid.
    """

    # --- 1. Decode Keys ---
    try:
        encrypt_key = decode_base64(encrypt_key_b64)
        hash_key = decode_base64(hash_key_b64)
    except ValueError as e:
        raise EncodingError(f"Invalid Base64 encoding for keys: {e}")
    
    # --- 2. Decode Message ---
    try:
        # url_decode handles both + and %20 style encoding
        url_decoded_msg = url_decode(encrypted_msg_b64)
        encrypted_msg_bytes = decode_base64(url_decoded_msg)
    except Exception as e:
        raise EncodingError(f"Invalid encoding for message: {e}")

    if len(encrypted_msg_bytes) < BLOCK_SIZE + 32:
        raise IntegrityError("Message is too short to be valid.")

    iv = encrypted_msg_bytes[:BLOCK_SIZE]
    encrypted_data = encrypted_msg_bytes[BLOCK_SIZE:-32] 
    msg_hash = encrypted_msg_bytes[-32:]

    # --- 3. Verify Message Integrity ---
    # HMAC is calculated over IV + encrypted message
    hmac_data = iv + encrypted_data
    expected_hash = hmac.new(hash_key, hmac_data, digestmod=hashlib.sha256).digest()
    
    if not hmac.compare_digest(msg_hash, expected_hash):
        raise IntegrityError(
            "Message integrity verification failed. "
            "Ensure the authentication keys match."
        )
    
    # --- 4. Decrypt the Message ---
    try:
        cipher = AES.new(encrypt_key, AES.MODE_CBC, iv)
        decrypted_padded_msg = cipher.decrypt(encrypted_data)
        decrypted_msg = Padding.unpad(decrypted_padded_msg, BLOCK_SIZE, style="pkcs7")
    except ValueError as e:
        raise PaddingError(
            f"Decryption failed (padding error): {e}. "
            "This can happen if the encryption key is incorrect or the data is corrupted."
        ) from e
    except Exception as e:
        raise DecryptionError(f"Unexpected error during decryption: {e}")

    return decrypted_msg
