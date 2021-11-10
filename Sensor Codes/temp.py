import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

import dht11
import datetime

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client("temp")
client.username_pw_set("user", "raspberry")
client.on_connect = on_connect
client.connect("192.168.50.10", 1883, 60)


GPIO.setmode(GPIO.BCM)
instance = dht11.DHT11(pin=4)


while 1:
    result = instance.read()
    if result.is_valid():
        print("Last valid input: " + str(datetime.datetime.now()))
        print("Temperature: %-3.1f C" % result.temperature)
        print("Humidity: %-3.1f %%" % result.humidity)
        payloadstr = "{{\"temp\":\"{}\", \"humid\":\"{}\"}}".format(result.temperature, result.humidity)
        print(payloadstr)
        client.publish('v1/devices/me/telemetry', payload=payloadstr, qos=0, retain=False)
    time.sleep(3)

GPIO.cleanup()
