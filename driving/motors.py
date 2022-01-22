from pinutils.pinutils import *
from backend.logger import *

forwardL = IOPin(IOPin.MODE_OUT, 5, mcp2)
backwardsL = IOPin(IOPin.MODE_OUT, 8, mcp1)
forwardR = IOPin(IOPin.MODE_OUT, 6, mcp2)
backwardsR = IOPin(IOPin.MODE_OUT, 7, mcp2)
speedL = IOPin(IOPin.MODE_OUT, 22)
speedR = IOPin(IOPin.MODE_OUT, 23)


def normalizeVelocity(l, r):
    m = max(abs(l), abs(r))
    l /= m
    r /= m
    return l, r


def set_motors(l, r, speed=1.0, normalize=False):
    try:
        if normalize:
            l, r = normalizeVelocity(l, r)

        l, r = l*speed, r*speed

        if l > 0:
            forwardL.write(True)
            backwardsL.write(False)
        elif l < 0:
            forwardL.write(False)
            backwardsL.write(True)
        else:
            forwardL.write(False)
            backwardsL.write(False)

        if r > 0:
            forwardR.write(True)
            backwardsR.write(False)
        elif r < 0:
            forwardR.write(False)
            backwardsR.write(True)
        else:
            forwardR.write(False)
            backwardsR.write(False)

        speedL.set_pwm(abs(int(l*100)))
        speedR.set_pwm(abs(int(r*100)))
    except OSError:
        logger.log(logging.INFO, "Failed to communicate with motors")
