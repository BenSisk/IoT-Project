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
DeviceID = "d1fdf480-488e-11ec-b1fe-fdae5670298b"
AirQualityDeviceID = "5100b700-488e-11ec-b1fe-fdae5670298b"

MQTTclient = mqtt.Client("window")
file = open("/home/pi/stuff/MQTTBroker.txt", "r")
broker = file.read()
file.close()


def sendDataHeating(heatingOn, rest_client):   
    attributes = {"heatingOn": heatingOn}
    rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
    MQTTclient.connect(broker, 1883, 60)
    if (heatingOn):
        MQTTclient.publish("NorthumbriaUniIoTSmartHome/Heating", payload="1", qos=0, retain=False)
    else:
        MQTTclient.publish("NorthumbriaUniIoTSmartHome/Heating", payload="0", qos=0, retain=False)

def sendDataWindow(windowOpen, rest_client):
    attributes = {"windowOpen": windowOpen}
    rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
    MQTTclient.connect(broker, 1883, 60)
    if (windowOpen):
        MQTTclient.publish("NorthumbriaUniIoTSmartHome/Window", payload="1", qos=0, retain=False)
    else:
        MQTTclient.publish("NorthumbriaUniIoTSmartHome/Window", payload="0", qos=0, retain=False)


# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # Auth with credentials
        rest_client.login(username=username, password=password)

        # Get device shared attributes
        #logging.info("Found device attributes: \n%r", res)

        manual = False
        windowOverride = False

        heatingOn = False
        previousHeatingOn = False
        manualHeatingOnOff = False
        previousManualHeatingOnOff = False

        windowOpen = False
        windowOverride = False
        previousWindowOverride = False
        previousWindowOpen = False
        manualWindowOpenClose = False
        previousManualWindowOpenClose = False

        targetTemp = 0
        currentTemp = 0

        while True:
            res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'SHARED_SCOPE')
            for i in res:
                if (i["key"] == "manual"):
                    manual = i["value"]
                if (i["key"] == "manualHeatingOnOff"):
                    manualHeatingOnOff = i["value"]
                if (i["key"] == "manualWindowOpenClose"):
                    manualWindowOpenClose = i["value"]
                if (i["key"] == "target"):
                    targetTemp = i["value"]
            

            res = rest_client.get_attributes_by_scope('DEVICE', AirQualityDeviceID, 'CLIENT_SCOPE')
            for i in res:
                if (i["key"] == "eCO2"):
                    eCO2 = i["value"]

            previousWindowOverride = windowOverride
            if (eCO2 > 800):
                windowOverride = True
                attributes = {"windowOpen": True}
                rest_client.save_device_attributes(attributes, DeviceID, 'SHARED_SCOPE')
                MQTTclient.publish("NorthumbriaUniIoTSmartHome/Window", payload="1", qos=0, retain=False)
            else:
                windowOverride = False
                if (previousWindowOverride != windowOverride):
                    previousWindowOverride = windowOverride
                    manualWindowOpenClose = not windowOpen
                    previousManualWindowOpenClose = not manualWindowOpenClose

                

            if (manual):
                if (heatingOn != manualHeatingOnOff):
                    previousManualHeatingOnOff = manualHeatingOnOff
                    heatingOn = manualHeatingOnOff
                    sendDataHeating(heatingOn, rest_client)
                if (windowOpen != manualWindowOpenClose and not windowOverride):
                    previousManualWindowOpenClose = manualWindowOpenClose
                    windowOpen = manualWindowOpenClose
                    sendDataWindow(windowOpen, rest_client)

            elif (manualHeatingOnOff != previousManualHeatingOnOff):
                manual = True
                previousManualHeatingOnOff = manualHeatingOnOff
                heatingOn = manualHeatingOnOff
                payload = {"manual": True}
                res = rest_client.save_device_attributes(payload, DeviceID, 'SHARED_SCOPE')
                sendDataHeating(heatingOn, rest_client)

            elif (manualWindowOpenClose != previousManualWindowOpenClose and not windowOverride):
                manual = True
                previousManualWindowOpenClose = manualWindowOpenClose
                windowOpen - manualWindowOpenClose
                payload = {"manual": True}
                res = rest_client.save_device_attributes(payload, DeviceID, 'SHARED_SCOPE')
                sendDataWindow(windowOpen, rest_client)
            else:
                res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'CLIENT_SCOPE')
                for i in res:
                    if (i["key"] == "temperature"):
                        currentTemp = i["value"]

                previousHeatingOn = heatingOn
                heatingOn = currentTemp < targetTemp
                if (heatingOn != previousHeatingOn):
                    manualHeatingOnOff = heatingOn
                    previousManualHeatingOnOff = heatingOn
                    payload = {"manualHeatingOnOff": heatingOn}
                    res = rest_client.save_device_attributes(payload, DeviceID, 'SHARED_SCOPE')
                    sendDataHeating(heatingOn, rest_client)

                if(windowOverride == False):
                    previousWindowOpen = windowOpen
                    windowOpen = currentTemp > targetTemp
                    if (windowOpen != previousWindowOpen):
                        manualWindowOpenClose = windowOpen
                        previousManualWindowOpenClose = windowOpen
                        payload = {"manualWindowOpenClose": windowOpen}
                        res = rest_client.save_device_attributes(payload, DeviceID, 'SHARED_SCOPE')
                        sendDataWindow(windowOpen, rest_client)


            time.sleep(1)

    except ApiException as e:
        logging.exception(e)