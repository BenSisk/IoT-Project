from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import logging
import requests

def main(client):
    response = requests.get("https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=today")
    sunrise = response.json()['results']['sunrise']
    sunset = response.json()['results']['sunset']

    sunrisePartition = sunrise.split(" ")
    arraySunrise = sunrisePartition[0].split(":")
    arraySunrise = [int(numeric_string) for numeric_string in arraySunrise]
    if (sunrisePartition[1] == "PM"):
        arraySunrise[0] += 12
    intSunrise = (arraySunrise[0] *60*60) + (arraySunrise[1] * 60) + arraySunrise[2]

    sunsetPartition = sunset.split(" ")
    arraySunset = sunsetPartition[0].split(":")
    arraySunset = [int(numeric_string) for numeric_string in arraySunset]
    if (sunsetPartition[1] == "PM"):
        arraySunset[0] += 12
    intSunset = (arraySunset[0] *60*60) + (arraySunset[1] * 60) + arraySunset[2]

    
    attributes = {"Sunrise": sunrise, "Sunset": sunset, "intSunrise": intSunrise, "intSunset": intSunset}
    result = client.send_attributes(attributes)
    result.get()
    print("Attributes update sent: " + str(result.rc() == TBPublishInfo.TB_ERR_SUCCESS))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    client = TBDeviceMqttClient("192.168.50.10", "Hf70V5S0Rq4BQEZAZOfy")
    client.max_inflight_messages_set(100)
    client.connect()
    main(client)