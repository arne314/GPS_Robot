import time
import threading
from simple_pid import *

from driving.motors import set_motors
from sensors.gpsreceiver import getPosition
from sensors.compass import getHeading
from utils import *
from backend.logger import *

RADIUS = 0.03
WHEEL_DISTANCE = 0.19

# threshold distances to target position
reduce_speed = 3
target_reached = 2


class RouteFollower(threading.Thread):
    route = []
    currentTargetIndex = 0
    running = False
    pid: PID

    target: Location
    position: Location
    distance: float
    heading: float
    bearing: float
    error: float

    def __init__(self, route):
        super().__init__()
        self.route = route
        self.resetPID()
        self.heading = 0
        self.error = 0

    def resetPID(self):
        self.pid = PID(1, 0.1, 0.05, setpoint=0)

    def restartRoute(self):
        self.currentTargetIndex = 0
        self.resetPID()

    def calculateRoute(self):
        self.position = getPosition()
        self.target = self.route[self.currentTargetIndex]
        self.distance = getDistance(self.position, self.target)
        self.heading = getHeading()
        self.bearing = getBearing(self.position, self.target)

        # calculate angle between heading and perfect route to target
        error = self.bearing - self.heading
        self.error = degrees(atan2(sin(radians(error)), cos(radians(error))))  # keep between -180 and 180

    def alignHeading(self):
        self.calculateRoute()
        iteration = 0

        while self.running and self.distance >= target_reached:
            if abs(self.error) < 40:
                if iteration >= 10:
                    self.resetPID()
                return
            elif abs(self.error) < 50:
                speed = 0.7
            else:
                speed = 1

            logger.log(logging.DEBUG, "Aligning heading")
            if self.error < 0:
                set_motors(-speed, speed)
            else:
                set_motors(speed, -speed)
            self.calculateRoute()
            iteration += 1
            time.sleep(0.1)

    def run(self):
        while True:
            if self.running:
                self.alignHeading()  # if necessary roughly align heading without driving forward first

                v = 1
                if self.distance < target_reached:
                    self.currentTargetIndex += 1
                    logger.log(logging.INFO, f"Reached waypoint {self.target.name}")

                    if self.currentTargetIndex == len(self.route):
                        logger.log(logging.INFO, "Final waypoint reached")
                        self.running = False
                        break
                    else:
                        continue
                elif self.distance <= reduce_speed:
                    v = 0.7

                w = self.pid(0.2*self.error)
                logger.log(logging.DEBUG, f"distance: {round(self.distance, 1)}, position: {self.position},"
                                          f" target: {self.target}, bearing: {round(self.bearing)},"
                                          f" error: {round(self.error)}, w: {round(w, 2)}, v: {v}")

                differentialDrive(w, v)
            else:
                set_motors(0, 0)
            time.sleep(0.1)


def differentialDrive(w, v=1.0):
    vl = (2 * v - w * WHEEL_DISTANCE) / (2 * RADIUS)
    vr = (2 * v + w * WHEEL_DISTANCE) / (2 * RADIUS)
    set_motors(vl, vr, speed=v, normalize=True)
