import paho.mqtt.client as mqtt
import time
import json
import funcoes_cript as fc
import update_unidades as uu

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
    time.sleep(1) # garantir que a menssagem seja publicada

    client.loop_stop() #desconexao
    client.disconnect()
    print("Mensagem Echo publicada e cliente desconectado.")

def get_public_key(destinatario):
    #uu.atualizar_chaves_confiadas()
    chaves_confiadas = {}
    with open('./scripts/chaves_confiadas.json','r') as f:
        chaves_confiadas= json.load(f)

    try: 
        chaves_dest = chaves_confiadas[destinatario]
        return chaves_dest['chave_publica_rsa'],chaves_dest['chave_publica_ecdsa']
    except Exception as e:
        print('Destinatário não pertence a chaves confiadas')
        return None,None

def enviar_mensagem_segura(destinatario,conteudo):
    TOPIC = f'sisdef/direto/{destinatario}'
    BROKER_ADDRESS = "test.mosquitto.org"

    # Chaves destinatário
    chave_rsa_pub_destinatario,chave_ecdsa_pub_destinatario = get_public_key(destinatario)
    
    if not chave_rsa_pub_destinatario:
        return
    
    chave_rsa_pub_destinatario = fc.carregar_chave_publica_b64(chave_rsa_pub_destinatario)
    chave_ecdsa_pub_destinatario = fc.carregar_chave_publica_b64(chave_ecdsa_pub_destinatario)

    # Chave Remetente
    with open('./scripts/chave_ut_foxtrot.json','r') as f:
        chave_ecdsa_priv_remetente = json.load(f)['ecdsa']['private_key']
        chave_ecdsa_priv_remetente = fc.carregar_chave_privada_b64(chave_ecdsa_priv_remetente)

    
    mensagem_segura = fc.criar_mensagem_segura(
        conteudo,
        chave_rsa_pub_destinatario,
        chave_ecdsa_priv_remetente)
    
    client = mqtt.Client()
    client.connect(BROKER_ADDRESS, 1883, 60)
    time.sleep(1)
    client.loop_start()
    client.publish(TOPIC, payload=json.dumps(mensagem_segura))
    client.loop_stop()
    client.disconnect()

print('### Mensagem Segura ###')
dest = input('id destino: ')
msg = input('Mensagem: ')
if dest=="" and msg=="":
    dest='ut-foxtrot'
    msg='teste'
    print('mensagem padrão')
elif dest=="oraculo" and msg=="echo":
    enviar_echo()
else:
    try:    
        enviar_mensagem_segura(dest,msg)
        print("### Mensagem Enviada ###")
    except Exception as e:
        print("### Erro ao enviar mensagem, tente novamente ###")
