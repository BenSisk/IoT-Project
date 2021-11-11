import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import signal
import dht11

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def on_disconnect(client, userdata, rc):
	client.reconnect()

def main(client):
    result = instance.read()
    if result.is_valid():
        #print("Last valid input: " + str(datetime.datetime.now()))
        #print("Temperature: %-3.1f C" % result.temperature)
        #print("Humidity: %-3.1f %%" % result.humidity)
        payloadstr = "{{\"temp\":\"{}\", \"humid\":\"{}\"}}".format(result.temperature, result.humidity)
        print(payloadstr)
        client.publish('v1/devices/me/telemetry', payload=payloadstr, qos=0, retain=False)
        client.loop()


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True

if __name__ == '__main__':
    killer = GracefulKiller()
    client = mqtt.Client("temp")
    client.username_pw_set("user", "raspberry")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("192.168.50.10", 1883, 60)

    client.loop()

    GPIO.setmode(GPIO.BCM)

    instance = dht11.DHT11(pin=4)
    while not killer.kill_now:
        main(client)
        time.sleep(3)
    client.disconnect()
    GPIO.cleanup()