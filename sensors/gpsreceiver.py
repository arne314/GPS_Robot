import time
import threading
import serial
import pynmea2

from utils import *
from backend.logger import *

info_rate = 10
last_info = 0

port = "/dev/ttyAMA0"

listener = None
parser = None

latitude, longitude = 0, 0
latoffset, lngoffset = 0, 0
accuracy = 0
number_satellites = 0


class GPSReader(threading.Thread):
    def run(self):
        logger.log(logging.DEBUG, "GPS listener started")
        while True:
            read = listener.readline().decode(encoding="ISO-8859-1")
            try:
                message = pynmea2.parse(read)
                try:
                    lat, lng = message.latitude, message.longitude
                    if lat != 0.0:
                        updatePosition(lat, lng)
                except:
                    pass
                try:
                    acc = message.gps_qual
                    updateAccuracy(acc)
                except:
                    pass
                try:
                    num = message.num_sats
                    updateSatelliteCount(num)
                except:
                    pass
            except:
                pass


def getPosition(apply_offset=True):
    if apply_offset:
        return Location(latitude + latoffset, longitude + lngoffset, name="current pos")
    else:
        return Location(latitude, longitude, name="current raw position")


def updatePosition(lat, lng):
    global latitude, longitude, last_info
    latitude, longitude = lat, lng

    now = time.time()
    if now - last_info >= info_rate:
        last_info = now
        logger.log(logging.DEBUG, f"updated current position to {lat}, {lng}")


def updateAccuracy(acc):
    global accuracy
    accuracy = acc


def updateSatelliteCount(num):
    global number_satellites
    number_satellites = num


def init():
    global listener, parser
    listener = serial.Serial(port, baudrate=9600, timeout=50)
    parser = pynmea2.NMEAStreamReader()
    GPSReader().start()


if __name__ == '__main__':
    init()
