import time
import paho.mqtt.client as mqtt
import board
import busio
import adafruit_sgp30
import signal

elapsed_sec = 0

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_disconnect(client, userdata, rc):
	client.reconnect()

def main(client, spg30):
    global elapsed_sec
    #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    elapsed_sec = elapsed_sec + 1
    if elapsed_sec > 5:
        elapsed_sec = 0
        print(
            "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
            % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        )
        payloadstr = "{{\"eCO2\":\"{}\", \"TVOC\":\"{}\"}}".format(sgp30.eCO2, sgp30.TVOC)
        client.publish('v1/devices/me/telemetry', payload=payloadstr, qos=0, retain=False)


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True

if __name__ == '__main__':
    killer = GracefulKiller()
    client = mqtt.Client("air")
    client.username_pw_set("user", "raspberry")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("192.168.50.10", 1883, 60)
    client.loop()
    client.loop_start()

    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

    # Create library object on our I2C port
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    elapsed_sec = 0

    #print("SGP30 serial #", [hex(i) for i in sgp30.serial])

    sgp30.iaq_init()
    sgp30.set_iaq_baseline(0x8973, 0x8AAE)

    while not killer.kill_now:
        main(client, sgp30)
        time.sleep(1)
    client.loop_stop()
    client.disconnect()