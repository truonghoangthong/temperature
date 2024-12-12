import time
import urequests as requests
from machine import Pin
import dht
import network

# Wi-Fi Details
SSID = "DN.Matthias"
PASSWORD = "idontknow"

# REST API Details
BASE_URL = "http://20.123.52.71/api/v1"
DATA_ENDPOINT = "/embed"
DEBUG = True

SENSOR = dht.DHT11(Pin(0)) 
LED = Pin("LED", Pin.OUT)

# Functions
def dlog(data) -> None:
    if DEBUG:
        print(repr(data))
    return None

def connect_wifi(ssid: str, password: str) -> network.WLAN:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"Connecting to WiFi SSID: {ssid}")
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConnected to WiFi!")
    dlog(wlan.ifconfig())
    return wlan

def send_temperature(endpoint: str, temp: float) -> None:
    url = f"{BASE_URL}{endpoint}?value={temp}"  
    try:
        response = requests.get(url)
        response.close()
    except Exception as e:
        print("Error sending data:", e)

def main() -> None:
    print("Program starting.")
    wlan = connect_wifi(SSID, PASSWORD)
    while True:
        try:
            SENSOR.measure()
            temp = SENSOR.temperature()  
            print(f"Temperature: {temp} °C")

            LED.on()
            send_temperature(DATA_ENDPOINT, temp)
            LED.off()

            time.sleep(10)  
        except Exception as e:
            print("Error in main loop:", e)

# Run the program
if __name__ == "__main__":
    main()
