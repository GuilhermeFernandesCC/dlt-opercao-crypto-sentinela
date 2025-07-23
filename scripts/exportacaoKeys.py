import base64
from cryptography.hazmat.primitives import serialization

def export_keys_as_string(private_key, public_key):
    _priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    _pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    chaves = {
        "private_key": base64.b64encode(_priv_bytes).decode(),
        "public_key": base64.b64encode(_pub_bytes).decode()
    }

    return chaves