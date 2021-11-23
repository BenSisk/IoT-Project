from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import logging
import requests

def main(client):
    response = requests.get("https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=today")
    sunrise = response.json()['results']['sunrise']
    sunset = response.json()['results']['sunset']

    attributes = {"Sunrise": sunrise, "Sunset": sunset}
    result = client.send_attributes(attributes)
    result.get()
    print("Attributes update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    client = TBDeviceMqttClient("192.168.50.10", "Hf70V5S0Rq4BQEZAZOfy")
    client.max_inflight_messages_set(100)
    client.connect()
    main(client)