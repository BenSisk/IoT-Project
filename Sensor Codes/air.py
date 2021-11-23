import time
import board
import busio
import adafruit_sgp30
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import signal
import logging

elapsed_sec = 0

def main(client, spg30):
    global elapsed_sec
    #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    elapsed_sec = elapsed_sec + 1
    if elapsed_sec > 5:
        elapsed_sec = 0
        # print(
        #     "**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x"
        #     % (sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        # )

        telemetry = {"eCO2": sgp30.eCO2, "TVOC": sgp30.TVOC}
        result = client.send_telemetry(telemetry)
        result.get()
        print("Telemetry update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))


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
    client = TBDeviceMqttClient("192.168.50.10", "xorzYWvb6gp9am4t7Amo")
    client.max_inflight_messages_set(100)
    client.connect()

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
    client.stop()