import paho.mqtt.client as mqtt
import time

BROKER_ADDRESS = "test.mosquitto.org"
TOPIC = "ufcg/cc/dlt/menssagens"
MESSAGE = "Olá, mundo da criptografia! Esta é uma mensagem de teste."

client = mqtt.Client()
client.connect(BROKER_ADDRESS, 1883, 60)


client.loop_start()
client.publish(TOPIC, MESSAGE)
time.sleep(1) # garanir que a menssagem seja publicada

client.loop_stop() #desconexao
client.disconnect()
print("Mensagem publicada e cliente desconectado.")