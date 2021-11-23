import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException
import time


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


url = "http://192.168.50.10:8080"

username = "beepboopmoopjoop2@gmail.com"
password = "raspberry"
DeviceID = "1ba4e820-4892-11ec-b1fe-fdae5670298b"


# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # Auth with credentials
        rest_client.login(username=username, password=password)

        # Get device shared attributes
        #logging.info("Found device attributes: \n%r", res)

        previous = False
        while True:
            res = rest_client.get_attributes_by_scope('DEVICE', DeviceID, 'SHARED_SCOPE')
            for i in res:
                if (i["key"] == "manual"):
                    value = i["value"]
                    break
            if (value != previous):
                print(value)
                previous = value
            time.sleep(0.5)

    except ApiException as e:
        logging.exception(e)