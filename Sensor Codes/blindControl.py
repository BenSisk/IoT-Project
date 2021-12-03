import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException
import time
from datetime import datetime
import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


url = "http://192.168.50.10:8080"

username = "beepboopmoopjoop2@gmail.com"
password = "raspberry"
DeviceID = "1ba4e820-4892-11ec-b1fe-fdae5670298b"

client = mqtt.Client("Blind")
file = open("/home/pi/stuff/MQTTBroker.txt", "r")
broker = file.read()
file.close()


def getSunData(rest_client):
    res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'CLIENT_SCOPE')
    sunrise = 0
    sunset = 0
    for i in res:
        if (i["key"] == "intSunrise"):
            sunrise = i["value"]
        if (i["key"] == "intSunset"):
            sunset = i["value"]
    return int(sunrise), int(sunset)

def getManualData(rest_client):
    res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'SHARED_SCOPE')
    openTime = 0
    closeTime = 0
    for i in res:
        if (i["key"] == "openTime"):
            openTime = i["value"]
        if (i["key"] == "closeTime"):
            closeTime = i["value"]
    return (openTime / 1000), (closeTime / 1000)


# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # Auth with credentials
        rest_client.login(username=username, password=password)

        # Get device shared attributes
        #logging.info("Found device attributes: \n%r", res)

        manual = False
        openBlind = False
        previousOpenTime = 0
        previousCloseTime = 0

        while True:
            res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'SHARED_SCOPE')
            for i in res:
                if (i["key"] == "manual"):
                    manual = i["value"]
                    break
            if (manual):
                openTime, closeTime = getManualData(rest_client)
            else:
                openTime, closeTime = getSunData(rest_client)

            now = datetime.now()
            seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
            print(seconds_since_midnight, openTime, closeTime)
            if (seconds_since_midnight > openTime and seconds_since_midnight < closeTime):
                print("bigoof")
                if (openBlind == False):
                    openBlind = True
                    client.connect(broker, 1883, 60)
                    client.publish("NorthumbriaUniIoTSmartHome/Blind", payload="1", qos=0, retain=False)
                    attributes = {"BlindOpen": openBlind}
                    rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
                    print("Call Open Window")
            else:
                if (openBlind == True):
                    openBlind = False
                    client.connect(broker, 1883, 60)
                    client.publish("NorthumbriaUniIoTSmartHome/Blind", payload="0", qos=0, retain=False)
                    attributes = {"BlindOpen": openBlind}
                    rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
                    print("Call Close Window")
            time.sleep(1)

    except ApiException as e:
        logging.exception(e)
