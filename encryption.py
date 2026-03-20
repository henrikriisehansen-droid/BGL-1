import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Padding
from utils import decode_base64, encode_base64, url_encode

BLOCK_SIZE = 16

def encrypt(msg: bytes, encrypt_key_b64: str, hash_key_b64: str) -> str:
    """
    Encrypt and hash a message, then URL-encode the result.

    Args:
        msg: Bytes to encrypt
        encrypt_key_b64: Base64 encoded encryption key
        hash_key_b64: Base64 encoded hash key

    Returns:
        URL-encoded Base64 encoded message containing IV + encrypted message + HMAC hash.
    """
    encrypt_key = decode_base64(encrypt_key_b64)
    hash_key = decode_base64(hash_key_b64)

    padded_msg = Padding.pad(msg, BLOCK_SIZE, style="pkcs7")

    cipher = AES.new(encrypt_key, AES.MODE_CBC)
    encrypted_msg = cipher.encrypt(padded_msg)

    # HMAC is calculated over IV + encrypted message
    hmac_data = cipher.iv + encrypted_msg
    msg_hash = hmac.new(hash_key, hmac_data, digestmod=hashlib.sha256).digest()
   
    # Combine IV, encrypted data, and hash
    combined_data = cipher.iv + encrypted_msg + msg_hash
    base64_msg = encode_base64(combined_data)
    
    return url_encode(base64_msg)