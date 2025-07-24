import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding

def sha256_hash(msg_bytes):
    """Calcula o hash SHA-256 da mensagem."""
    return hashlib.sha256(msg_bytes).digest()


def gerar_chave_aes():
    """Gera chave de sessão AES de 256 bits."""
    return os.urandom(32)


def criptografar_aes_gcm(chave_aes, mensagem_bytes):
    """Criptografa usando AES-256 GCM."""
    nonce = os.urandom(12)  # 96 bits é padrão para GCM
    aesgcm = AESGCM(chave_aes)
    ciphertext = aesgcm.encrypt(nonce, mensagem_bytes, None)
    tag = ciphertext[-16:]          # última parte é o tag de autenticação
    ciphertext = ciphertext[:-16]   # resto é o texto cifrado

    return ciphertext, tag, nonce


def criptografar_chave_aes(chave_aes, chave_rsa_pub):
    """Criptografa a chave AES com a chave pública RSA do destinatário."""
    return chave_rsa_pub.encrypt(
        chave_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def assinar_hash(hash_msg, chave_ecdsa_priv):
    """Assina o hash SHA-256 da mensagem com a chave privada ECDSA."""
    assinatura = chave_ecdsa_priv.sign(
        hash_msg,
        ec.ECDSA(hashes.SHA256())
    )
    return assinatura

def criar_mensagem_segura(payload, chave_rsa_pub_destinatario, chave_ecdsa_priv_remetente):
    """Cria a estrutura JSON segura para transmissão."""
    # 1. Preparar mensagem
    if isinstance(payload, str):
        payload_bytes = payload.encode()
    else:
        payload_bytes = payload  # Ex: imagem em Base64

    # 2. Hash da mensagem
    hash_msg = sha256_hash(payload_bytes)

    # 3. Gerar e criptografar mensagem com AES
    chave_aes = gerar_chave_aes()
    ciphertext, tag, nonce = criptografar_aes_gcm(chave_aes, payload_bytes)

    # 4. Criptografar chave AES com RSA
    chave_sessao_cifrada = criptografar_chave_aes(chave_aes, chave_rsa_pub_destinatario)

    # 5. Assinar o hash com ECDSA
    assinatura = assinar_hash(hash_msg, chave_ecdsa_priv_remetente)

    # 6. Montar mensagem JSON com todos os campos codificados em Base64
    mensagem_segura = {
        "ciphertext_b64": base64.b64encode(ciphertext).decode(),
        "tag_autenticacao_b64": base64.b64encode(tag).decode(),
        "nonce_b64": base64.b64encode(nonce).decode(),
        "chave_sessao_cifrada_b64": base64.b64encode(chave_sessao_cifrada).decode(),
        "assinatura_b64": base64.b64encode(assinatura).decode()
    }

    return mensagem_segura