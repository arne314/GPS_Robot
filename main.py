from backend import backend
from sensors import compass, gpsreceiver
from driving import motors
from visuals import display

VERSION = "1.5"

try:
    # setup hardware
    gpsreceiver.init()
    compass.init()
    display.init()

    # setup backend
    backend.init(VERSION)
finally:
    motors.set_motors(0, 0)
