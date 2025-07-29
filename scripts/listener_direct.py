import base64
import json
import revogador
import funcoes_cript as fc
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import paho.mqtt.client as mqtt
import update_unidades as uu
# 🟡 CONFIGURAÇÕES
ID_UNIDADE = "ut-foxtrot"
TOPICO_ESPECIFICO = f"sisdef/direto/{ID_UNIDADE}"
CHAVES_PATH = "./scripts/chaves_confiadas.json"
ARQUIVO_PRIVADO = "./scripts/chave_ut_foxtrot.json"


def carregar_chave_privada_rsa_de_json():
    with open(ARQUIVO_PRIVADO,'r') as f:
        data = json.load(f)
    chave_privada_b64 = data["rsa"]["private_key"]
    chave_privada = fc.carregar_chave_privada_b64(chave_privada_b64)
    return chave_privada

# Recuperar chave pública ECDSA de uma unidade remetente (confiada)
def recuperar_chave_ecdsa(id_unidade):
    with open(CHAVES_PATH, "r") as f:
        chaves = json.load(f)
    chave_b64 = chaves[id_unidade]["chave_publica_ecdsa"]
    
    return fc.carregar_chave_publica_b64(chave_b64)

# Verificar assinatura ECDSA
def verificar_assinatura(chave_ecdsa_pub, mensagem, assinatura):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(mensagem)
    hash_mensagem = digest.finalize()

    try:
        chave_ecdsa_pub.verify(assinatura, hash_mensagem, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

# Descriptografar com AES-GCM
def descriptografar_aes_gcm(chave_sessao, nonce, tag, ciphertext):
    decryptor = Cipher(
        algorithms.AES(chave_sessao),
        modes.GCM(nonce, tag),
        backend=default_backend()
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# Descriptografar chave de sessão com RSA
def descriptografar_chave_sessao(chave_privada, chave_sessao_cifrada):
    return chave_privada.decrypt(
        chave_sessao_cifrada,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

# Callback de mensagem recebida
def on_message(client, userdata, msg):
    print(f"\n Mensagem recebida em {msg.topic}")
    uu.atualizar_chaves_confiadas()
    try:
        pacote = json.loads(msg.payload.decode("utf-8"))

        # Passo 1 - Decodificação Base64
        ciphertext = base64.b64decode(pacote["ciphertext_b64"])
        nonce = base64.b64decode(pacote["nonce_b64"])
        tag = base64.b64decode(pacote["tag_autenticacao_b64"])
        chave_sessao_cifrada = base64.b64decode(pacote["chave_sessao_cifrada_b64"])
        assinatura = base64.b64decode(pacote["assinatura_b64"])
        remetente = pacote["remetente"].lower()

        # Passo 2 - Descriptografar chave de sessão
        chave_privada_rsa = carregar_chave_privada_rsa_de_json()
        try:
            chave_sessao = descriptografar_chave_sessao(chave_privada_rsa, chave_sessao_cifrada)
        except ValueError as e:
            print("Erro ao descriptografar chave de sessão:", e)
            print("Possível chave corrompida ou mal direcionada.")

        print("Mensagem diz ser de:", remetente)
        # Passo 3 - Descriptografar a mensagem com AES-GCM
        mensagem_clara = descriptografar_aes_gcm(chave_sessao, nonce, tag, ciphertext)
        print("Mensagem descriptografada com sucesso:")
        print(mensagem_clara.decode("utf-8"))

        # Passo 4 - Validar assinatura
        chave_pub_ecdsa = recuperar_chave_ecdsa(remetente)
        if verificar_assinatura(chave_pub_ecdsa, mensagem_clara, assinatura):
            print(f"ASSINATURA VERIFICADA: Mensagem autêntica de {remetente}")
        else:
            raise Exception("Assinatura inválida! Possível falsificação.")

    except Exception as e:
        print(f"Falha na validação: {e}")
        with open("./scripts/chave_ut_foxtrot.json") as f:
            identidade = json.load(f)

        ecdsa_priv_b64 = identidade["ecdsa"]["private_key"]
        chave_priv_ecdsa = fc.carregar_chave_privada_b64(ecdsa_priv_b64)

        revogador.emitir_e_publicar_revogacao(
            unidade_revogada="ut-charlie",
            remetente_id="ut-foxtrot",
            chave_privada_ecdsa=chave_priv_ecdsa
        )
        
# Conectar e escutar tópico
def iniciar_listener():
    print(f" Iniciando listener seguro para {ID_UNIDADE} no tópico: {TOPICO_ESPECIFICO}")
    client = mqtt.Client()
    client.on_message = on_message
    client.connect('test.mosquitto.org', 1883, 60)
    client.subscribe(TOPICO_ESPECIFICO)
    print("Conectado")
    client.loop_forever()

iniciar_listener()