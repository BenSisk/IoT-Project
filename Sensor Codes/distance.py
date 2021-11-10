import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client("USDistance")
client.username_pw_set("user", "raspberry")
client.on_connect = on_connect
client.connect("192.168.50.10", 1883, 60)


GPIO.setmode(GPIO.BCM)

TRIG = 14
ECHO = 15

print("Measuring")

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print("Settling")
time.sleep(2)

while 1:
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

	payloadstr = '{"distance":"' + str(distance) + '"}'
	print(distance)
	if (distance < 50):
		client.publish('v1/devices/me/telemetry', payload=payloadstr, qos=0, retain=False)
	time.sleep(0.2)

GPIO.cleanup()
