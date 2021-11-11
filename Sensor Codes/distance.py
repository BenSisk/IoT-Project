import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import signal

TRIG = 14
ECHO = 15

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_disconnect(client, userdata, rc):
	client.reconnect()

def main(client):
	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	while GPIO.input(ECHO) == 0:
		pulse_start = time.time()

	while GPIO.input(ECHO) == 1:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start

	distance = pulse_duration * 17150

	distance = round(distance, 0)

	payloadstr = "{{\"distance\":\"{}\"}}".format(distance)
	print(distance)
	if (distance < 50):
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
	client = mqtt.Client("USDistance")
	client.username_pw_set("user", "raspberry")
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.connect("192.168.50.10", 1883, 60)
	client.loop()

	GPIO.setmode(GPIO.BCM)

	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)

	GPIO.output(TRIG, False)
	print("Settling")
	time.sleep(2)

	while not killer.kill_now:
		main(client)
		time.sleep(0.1)
	client.disconnect()
	GPIO.cleanup()