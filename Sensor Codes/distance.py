import RPi.GPIO as GPIO
import time
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import signal
import logging

TRIG = 14
ECHO = 15


def main(client):
	global buffer
	global lastMotion
	global motionActive

	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)


	if (time.time() > lastMotion + 5 and motionActive):
		attributes = {"motion": False}
		result = client.send_attributes(attributes)
		result.get()
		motionActive = False
		print("Attributes update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))

	badScan = False
	
	end_time = time.time() + 1

	pulse_start = time.time()
	pulse_end = time.time()

	while (GPIO.input(ECHO) == 0):
		pulse_start = time.time()
		if (pulse_start > end_time):
			badScan = True
			break

	if (not badScan):
		while (GPIO.input(ECHO) == 1):
			pulse_end = time.time()
			badScan = False
			if (pulse_end > end_time):
				badScan = True
				break
	

	if (not badScan):
		pulse_duration = pulse_end - pulse_start

		distance = pulse_duration * 17150

		distance = round(distance, 0)

		if (distance < 50 ):
			print(buffer)
			buffer.append(distance)
			if (len(buffer) >= 5):
				smallest = buffer[0]
				mean = 0
				for i in buffer:
					mean += i
					if (i < smallest):
						smallest = i
				mean /= len(buffer)

				telemetry = {"distance": smallest}
				result = client.send_telemetry(telemetry)
				result.get()
				print("Telemetry update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))

				if (smallest < mean - 2):
					attributes = {"motion": True}
					result = client.send_attributes(attributes)
					result.get()
					print("Attributes update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))
					lastMotion = time.time()
					motionActive = True
				buffer = []



class GracefulKiller:
	kill_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self, *args):
		self.kill_now = True

if __name__ == '__main__':
	killer = GracefulKiller()
	logging.basicConfig(level=logging.DEBUG)
	client = TBDeviceMqttClient("192.168.50.10", "kM6cVFVjmq3EGnTnmpW9")
	#client.max_inflight_messages_set(100)
	client.connect()
	buffer = []
	lastMotion = 0
	motionActive = False

	attributes = {"motion": False}
	result = client.send_attributes(attributes)
	result.get()
	print("Attributes update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))


	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	GPIO.output(TRIG, False)

	print("Settling")
	time.sleep(2)

	while not killer.kill_now:
		time.sleep(0.2)
		main(client)
	GPIO.cleanup()
	client.stop()