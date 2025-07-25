import json
import time
import datetime
import paho.mqtt.client as mqtt

def atualizar_chaves_confiadas(timeout=10, arquivo_saida="./scripts/chaves_confiadas.json"):
    chaves_por_unidade = {}

    try:
        with open(arquivo_saida, "r") as f:
            chaves_por_unidade = json.load(f)
    except FileNotFoundError:
        pass

    def on_message(client, userdata, msg):
        print(f"Mensagem recebida no tópico {msg.topic}")
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            id_unidade = payload["id_unidade"]
            chave_rsa = payload["chave_publica_rsa"]
            chave_ecdsa = payload["chave_publica_ecdsa"]

            chaves_por_unidade[id_unidade] = {
                "chave_publica_rsa": chave_rsa,
                "chave_publica_ecdsa": chave_ecdsa,
                "ultima_atualizacao": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")

    client = mqtt.Client()
    client.on_message = on_message

    try:
        client.connect("test.mosquitto.org", 1883, 60)
    except Exception as e:
        print(f"Erro ao conectar MQTT: {e}")
        return

    # Inscreve ANTES de iniciar o loop para garantir recebimento das retidas
    client.subscribe("sisdef/broadcast/chaves/+")

    client.loop_start()

    # Aguarda mensagens retidas (e novas)
    print(f"Aguardando mensagens retidas por {timeout} segundos...")
    time.sleep(timeout)

    client.loop_stop()
    client.disconnect()

    print("Desconectado da atualização de chaves MQTT")

    with open(arquivo_saida, "w") as f:
        json.dump(chaves_por_unidade, f, indent=2)

    print(f"Arquivo de chaves atualizado: {arquivo_saida}")

if __name__ == "__main__":
    atualizar_chaves_confiadas(timeout=10)
