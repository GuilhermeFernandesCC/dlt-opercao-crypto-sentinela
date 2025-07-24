import paho.mqtt.client as mqtt
import hashlib
import base64
import time
import json
import funcoes_cript as fc

def enviar_echo():
    BROKER_ADDRESS = "test.mosquitto.org"
    TOPIC = 'sisdef/direto/oraculo'
    echo = {
        "id_unidade": "ut-foxtrot",
        "cmd": "echo"
    }
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)


    client.loop_start()
    client.publish(TOPIC, payload=echo)
    time.sleep(1) # garanir que a menssagem seja publicada

    client.loop_stop() #desconexao
    client.disconnect()
    print("Mensagem Echo publicada e cliente desconectado.")

def get_public_key(destinatario):
    chaves_confiadas = {}
    with open('./scripts/chaves_confiadas.json','r') as f:
        chaves_confiadas= json.load(f)

    try: 
        chaves_dest = chaves_confiadas[destinatario]
        chave_publica_rsa = chaves_dest['chave_publica_rsa']
        chave_publica_ecdsa = chaves_dest['chave_publica_ecdsa']
        return chave_publica_rsa,chave_publica_ecdsa
    except Exception as e:
        print('Destinatário não pertence a chaves confiadas')



def enviar_mensagem_segura(destinatario,conteudo):
    TOPIC = f'sisdef/direto/{destinatario}'
    BROKER_ADDRESS = "test.mosquitto.org"
    # Chaves destinatário
    chave_rsa_pub_destinatario,chave_rsa_pub_destinatario = get_public_key(destinatario)
    # Chave Remetente
    with open('./scripts/chave_ut_foxtrot.json','r') as f:
        chave_rsa_priv_remetente = json.load(f)['ecdsa']['private_key']

    mensagem_segura = fc.criar_mensagem_segura(conteudo,chave_rsa_pub_destinatario,chave_rsa_priv_remetente)
    
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)
    client.loop_start()
    client.publish(TOPIC, json.dumps(mensagem_segura))
    client.loop_stop()
    client.disconnect()

print('### Mensagem Segura ###')
dest = input('id destino: ')
msg = input('Mensagem: ')
enviar_mensagem_segura(dest,msg)
'''
try:
    
    print("### Mensagem Enviada ###")
except Exception as e:
    print("### Erro ao enviar mensagem, tente novamente ###")
'''