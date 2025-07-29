import json
import time
import base64
import datetime
import paho.mqtt.client as mqtt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

def emitir_e_publicar_revogacao(unidade_revogada, chave_privada_ecdsa, broker="test.mosquitto.org",remetente_id='ut-foxtrot'):

    #Emite e publica uma ordem de revogação para a unidade comprometida.
    # 1. Cria a mensagem de revogação
    revogacao = {
        "unidade_revogada": unidade_revogada,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

    revogacao_json = json.dumps(revogacao, separators=(',', ':'))  # sem espaços extras

    # 2. Gera o hash da mensagem
    digest = hashes.Hash(hashes.SHA256())
    digest.update(revogacao_json.encode('utf-8'))
    hash_revogacao = digest.finalize()

    # 3. Assina o hash com a chave privada ECDSA
    assinatura = chave_privada_ecdsa.sign(hash_revogacao, ec.ECDSA(hashes.SHA256()))
    assinatura_b64 = base64.b64encode(assinatura).decode()

    # 4. Monta o pacote final
    pacote_revogacao = {
        "remetente": remetente_id,
        "revogacao": revogacao,
        "assinatura_b64": assinatura_b64
    }

    # 5. Publica no tópico MQTT
    client = mqtt.Client()
    client.connect(broker, 1883, 60)
    client.loop_start()
    client.publish("sisdef/broadcast/revogacao", json.dumps(pacote_revogacao))
    time.sleep(1)
    client.loop_stop()
    client.disconnect()

    print(f"[OK] Revogação de '{unidade_revogada}' publicada por '{remetente_id}'.")
