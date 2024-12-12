import time
import urequests as requests
from machine import Pin
import dht
import network

# Wi-Fi Details
SSID = "connection"
PASSWORD = "@@@@1234"

# REST API Details
BASE_URL = "http://20.123.52.71/api/v1"
DATA_ENDPOINT = "/embed"
DEBUG = True

# Sensor and LED
SENSOR = dht.DHT11(Pin(0))  # Adjust GPIO pin as necessary
LED = Pin("LED", Pin.OUT)

# Functions
def dlog(data) -> None:
    """
    Debug log function to print messages when DEBUG is True.
    """
    if DEBUG:
        print(repr(data))
    return None

def connect_wifi(ssid: str, password: str) -> network.WLAN:
    """
    Connect to Wi-Fi and return the WLAN object.
    """
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
        dlog(f"Sending request to {url}")
        response = requests.get(url)
        dlog(f"Response status: {response.status_code}")
        dlog(f"Response content: {response.text}")
        response.close()
    except Exception as e:
        print("Error sending data:", e)

def main() -> None:
    """
    Main program loop to read sensor data and send it to the API.
    """
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
