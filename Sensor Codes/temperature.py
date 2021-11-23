import RPi.GPIO as GPIO
import time
import signal
import dht11
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import logging

def main(client):
  result = instance.read()
  if result.is_valid():
    #print("Last valid input: " + str(datetime.datetime.now()))
    #print("Temperature: %-3.1f C" % result.temperature)
    #print("Humidity: %-3.1f %%" % result.humidity)
    telemetry = {"temperature": result.temperature, "humidity": result.humidity}
    res = client.send_telemetry(telemetry)
    res.get()
    print("Telemetry update sent: " + str(res.rc() == TBPublishInfo.TB_ERR_SUCCESS))


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
  client = TBDeviceMqttClient("192.168.50.10", "qmRcppjpc4i9fotKjyUB")
  client.max_inflight_messages_set(100)
  client.connect()

  GPIO.setmode(GPIO.BCM)

  instance = dht11.DHT11(pin=4)
  while not killer.kill_now:
    main(client)
    time.sleep(3)
  GPIO.cleanup()
  client.stop()