import base64
import json
import time
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization
import paho.mqtt.client as mqtt
import exportacaoKeys

#Estabelecimento de Identidade (IFF)
#1 Geração de par de chaves assimétricas

def gerar_chave_rsa():
    #Gera um par de chaves RSA (2048 bits, e=65537).
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def gerar_chave_ecdsa():
    #Gera um par de chaves ECDSA usando a curva secp256r1.
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def gerar_identidade():
        # Gera par de chaves RSA
    rsa_priv, rsa_pub = gerar_chave_rsa()
    rsa_keys = exportacaoKeys.export_keys_as_string(rsa_priv, rsa_pub)

    # Gera par de chaves ECDSA
    ecdsa_priv, ecdsa_pub = gerar_chave_ecdsa()
    ecdsa_keys = exportacaoKeys.export_keys_as_string(ecdsa_priv, ecdsa_pub)
    identidadeJson = {
        "rsa": rsa_keys,
        "ecdsa": ecdsa_keys
    }
    with open('./scripts/chave_ut_foxtrot.json', "w") as f:
        json.dump(identidadeJson, f, indent=2)
    
    return [rsa_priv,rsa_pub,ecdsa_priv,ecdsa_pub]


#2 Publicação Identidade no CCU

def publicar_identidade_mqtt(id_unidade, pub_rsa_b64, pub_ecdsa_b64):
    BROKER_ADDRESS = "test.mosquitto.org"
    topico = f"sisdef/broadcast/chaves/{id_unidade}"

    mensagem = {
        "id_unidade": id_unidade,
        "chave_publica_rsa": pub_rsa_b64,
        "chave_publica_ecdsa": pub_ecdsa_b64
    }
    print(mensagem)
    cliente = mqtt.Client()
    cliente.connect(BROKER_ADDRESS, 1883, 60)
    cliente.loop_start()
    cliente.publish(topico, json.dumps(mensagem),retain=True)
    time.sleep(1)
    cliente.loop_stop()
    cliente.disconnect()

    print(f"Publicado com sucesso no tópico: {topico}")


def exportar_chave_publica_base64(pub_key):
    """Exporta chave pública no formato DER e codifica em Base64."""
    pub_bytes = pub_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(pub_bytes).decode()

identidade = gerar_identidade()

ID_UNIDADE = "ut-foxtrot"

pub_rsa_b64 = exportar_chave_publica_base64(identidade[1])
pub_ecdsa_b64 = exportar_chave_publica_base64(identidade[3])

print(pub_rsa_b64,pub_ecdsa_b64)

publicar_identidade_mqtt(ID_UNIDADE, pub_rsa_b64, pub_ecdsa_b64)