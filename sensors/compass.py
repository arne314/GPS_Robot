import traceback
import requests
from backend.logger import *

import py_qmc5883l
from utils import Location

mount_offset = -95

degFallback = 3
radminFallback = 14

sensor = None
heading = 0


def init():
    try:
        global sensor
        sensor = py_qmc5883l.QMC5883L(output_range=py_qmc5883l.RNG_2G, output_data_rate=py_qmc5883l.ODR_100HZ)
        sensor.declination = degFallback + radminFallback/60 + mount_offset
        sensor.calibration = [[1.0099196911997583, -0.05430589002618491, -1908.3083029138015],
                              [-0.05430589002618491, 1.297300554235797, 165.2394515863209], [0.0, 0.0, 1.0]]
        sensor.mode_continuous()
        logger.log(logging.DEBUG, "Initialized compass")
    except:
        logger.log(logging.INFO, "Failed to initialize the compass")


def fetchDeclinationFromLocation(location: Location):
    lat, lng = location.tuple
    try:
        res = requests.get(f"https://magnetic-declination.com/srvact/?lat={lat}&lng={lng}&act=1")
        declination = res.text.split("\n")[1].split(" ")
        deg = int(declination[2].replace("+", "").replace("&deg;", ""))
        radmin = int(declination[3].replace("'", ""))
        logger.log(logging.INFO, f"Fetched declination from API: {deg}° {radmin}'")
    except:
        deg = degFallback
        radmin = radminFallback
        logger.log(logging.INFO, f"Failed to fetch declination from API, using fallback: {deg}° {radmin}'")
    sensor.declination = deg + radmin/60 + mount_offset


def getHeading():
    global heading
    try:
        read = sensor.get_bearing()
        if read is None:
            init()
            raise OSError("Sensor disconnected")
        heading = read
        if heading > 180:  # from -180 to 180 not 0 to 360
            heading -= 360
    except OSError:
        traceback.print_exc()
        logger.log(logging.INFO, "Failed to read heading from compass")
    return heading
