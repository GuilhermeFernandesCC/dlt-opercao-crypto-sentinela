import paho.mqtt.client as mqtt

BROKER_ADDRESS = "test.mosquitto.org"
TOPICOS = [
    "ufcg/cc/dlt/wall",
    "ufcg/cc/dlt/menssagens",
    "ufcg/cc/dlt/chaves/+",
    "sisdef/broadcast/chaves/+",
    "sisdef/direto/ut-foxtrot",
]

# --- Funções de Callback ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for topico in TOPICOS:
            client.subscribe(topico)
    else:
        print(f"Falha na conexão. Código de retorno: {rc}")

def on_message(client, userdata, msg):
    mensagem = msg.payload.decode()
    print("-" * 30)
    print(f"📥 Tópico: {msg.topic}")
    print(f"📨 Conteúdo: {mensagem}")
    print("-" * 30)

# --- Cliente MQTT ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, 1883, 60)
client.loop_forever()