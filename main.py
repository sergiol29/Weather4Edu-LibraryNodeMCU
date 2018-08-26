import network
import ubinascii
from machine import UART
import json
import time
import urequests # importing the requests library

# CHANGE TO CONNECT WIFI
SSID = '**'
PASSWORD_SSID = '**'

# URL ENDPOINT BACKEND & HEADERS
API_ENDPOINT = "http://api-tfg.herokuapp.com/input/v1/save_data"
API_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# MAC OF STATION
mac_station = ""

uart = UART(0, 115200)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1) # init with given arametrs

def do_connect():
    wifi = network.WLAN(network.STA_IF) #interfaz para conectarse a un router

    if not wifi.isconnected():
    #    print('connecting to network...')
        wifi.active(True) #Activamos conexion
        wifi.connect(SSID, PASSWORD_SSID) #Conectamos a la red
        while not wifi.isconnected(): #Comprobamos si ha sido establecida la conexion
            pass
    #print('network config:', wifi.ifconfig())
    global mac_station
    mac_station = ubinascii.hexlify(wifi.config('mac'),':').decode()

def getMAC():
    return mac_station

def setup():
    do_connect()
    mac = getMAC()

# CHECK IF JSON READED TO PORT SERIAL IS CORRECT
def is_json_correct(json_data):
    try:
        json_object = json.loads(json_data)
    except OSError as e:  # This is the correct syntax
        print(e)
        return False
    except ValueError as e:
        print(e)
        return False
    return True

# FIRTS FUNCTION EXECUTE AT PROGRAM
setup()

while( True ):
    time.sleep(400)

    # If string read at port Serial is better than 1 read port serial
    if(uart.any() > 0):
        rawDATA = {}
        readSW = uart.read()

        # IF JSON READED IS CORRECT, SEND TO API
        if is_json_correct(readSW):
            rawDATA["DATA"] = json.loads(readSW)
            rawDATA["STATION_CODE"] = mac_station

            # sending post request and saving response as respons
            try:
                r = urequests.post(API_ENDPOINT, data = json.dumps(rawDATA), headers = API_HEADERS)
            except OSError as e:  # This is the correct syntax
                print(e)
            except ValueError as e:
                print(e)
        else: # IF JSON READED IS INCORRECT, WE MAKE OTHER READ AT PORT SERIAL FOR ERASE BYTES WRONG
            while True: # READ PORT SERIAL UNTIL NOT HAVE MORE BYTE TO READ
                uart.read()
                if(uart.any() <= 0):
                    break
