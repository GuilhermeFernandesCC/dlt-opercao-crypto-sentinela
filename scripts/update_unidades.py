import json
import datetime
import paho.mqtt.client as mqtt
import time
import threading

def atualizar_chaves_confiadas(timeout=3, arquivo_saida="./scripts/chaves_confiadas.json"):
    """
    Escuta o tópico 'sisdef/broadcast/chaves/+' por alguns segundos e atualiza o JSON de chaves confiadas.
    Deve ser chamada antes de enviar/receber mensagens.
    """
    chaves_por_unidade = {}

    # Carrega chaves anteriores (se existirem)
    try:
        with open(arquivo_saida, "r") as f:
            chaves_por_unidade = json.load(f)
    except FileNotFoundError:
        pass  # Arquivo ainda não existe, sem problema

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            id_unidade = payload["id_unidade"]
            chave_rsa = payload["chave_publica_rsa"]
            chave_ecdsa = payload["chave_publica_ecdsa"]

            chaves_por_unidade[id_unidade] = {
                "chave_publica_rsa": chave_rsa,
                "chave_publica_ecdsa": chave_ecdsa,
                "ultima_atualizacao": datetime.datetime.now(datetime.UTC)
            }

            print(f"### Chaves de {id_unidade} recebidas e atualizadas.")
        except Exception as e:
            print(f"### Erro ao processar atulaização de chaves: {e}")

    # Setup MQTT
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("test.mosquitto.org", 1883, 60)
    client.subscribe("sisdef/broadcast/chaves/+")

    # Rodar o loop em thread separada
    def iniciar_loop():
        client.loop_forever()

    thread = threading.Thread(target=iniciar_loop)
    thread.start()

    # Espera o tempo necessário para coletar mensagens
    time.sleep(timeout)

    client.disconnect()
    print(" Desconectado atualização de chaves mqtt ")
    thread.join(timeout=1)

    # Salva JSON atualizado
    with open(arquivo_saida, "w") as f:
        json.dump(chaves_por_unidade, f, indent=2)

    print(f" Arquivo de chaves atualizado: {arquivo_saida}")