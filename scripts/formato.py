import base64
from cryptography.hazmat.primitives import serialization

def load_rsa_pub_key(b64_str):
    key_bytes = base64.b64decode(b64_str)
    return serialization.load_der_public_key(key_bytes)

def load_ecdsa_pub_key(b64_str):
    key_bytes = base64.b64decode(b64_str)
    return serialization.load_der_public_key(key_bytes)
