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
DeviceID = "83358a10-488f-11ec-b1fe-fdae5670298b"

client = mqtt.Client("Light")
file = open("/home/pi/stuff/MQTTBroker.txt", "r")
broker = file.read()
file.close()


def sendLightData(lightOn, rest_client):
    attributes = {"lightOn": lightOn, "manualLightOnOff": lightOn}
    rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
    client.connect(broker, 1883, 60)
    if (lightOn):
        client.publish("NorthumbriaUniIoTSmartHome/Motion", payload="1", qos=0, retain=False)
    else:
        client.publish("NorthumbriaUniIoTSmartHome/Motion", payload="0", qos=0, retain=False)


# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # Auth with credentials
        rest_client.login(username=username, password=password)

        # Get device shared attributes
        #logging.info("Found device attributes: \n%r", res)

        manual = False
        manualLightOnOff = False
        previousManualLightOnOff = False
        lightOn = False
        motion = False

        while True:
            previousManualLightOnOff = manualLightOnOff
            res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'SHARED_SCOPE')
            for i in res:
                if (i["key"] == "manual"):
                    manual = i["value"]
                if (i["key"] == "manualLightOnOff"):
                    manualLightOnOff = i["value"]
            
            if (manual and lightOn != manualLightOnOff):
                lightOn = manualLightOnOff
                sendLightData(lightOn, rest_client)
            elif (previousManualLightOnOff != manualLightOnOff):
                manual = True
                payload = {"manual": True}
                res = rest_client.save_device_attributes(payload, DeviceID, 'SHARED_SCOPE')

                lightOn = manualLightOnOff
                sendLightData(lightOn, rest_client)
            else:
                res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'CLIENT_SCOPE')
                for i in res:
                    if (i["key"] == "motion"):
                        motion = i["value"]
                        break
                if (not manual and motion != lightOn):
                    lightOn = motion
                    manualLightOnOff = motion
                    previousManualLightOnOff = manualLightOnOff
                    sendLightData(lightOn, rest_client)

            time.sleep(1)

    except ApiException as e:
        logging.exception(e)


