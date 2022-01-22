import time

import board
import busio
import pigpio
from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import DigitalInOut

i2c = busio.I2C(board.SCL, board.SDA)
pi = pigpio.pi()

mcp1 = MCP23017(i2c, address=0x20)
mcp2 = MCP23017(i2c, address=0x21)


def init_mcp(mcp: MCP23017):
    mcp.clear_ints()


class IOPin:  # uses BCM
    MODE_IN = True
    MODE_OUT = False

    def __init__(self, mode, pin, mcp: MCP23017=None):
        self.pin = pin
        self.mode = mode
        if mcp:
            self.isMcp = True
            self.mcp: MCP23017 = mcp
            self.mcp_pin: DigitalInOut = mcp.get_pin(pin)
        else:
            self.isMcp = False
        self.setmode(mode)

    def setmode(self, mode):  # True is input
        self.mode = mode
        if self.isMcp:
            if mode:
                self.mcp_pin.switch_to_input()
            else:
                self.mcp_pin.switch_to_output()
        else:
            pi.set_mode(self.pin, pigpio.INPUT if mode else pigpio.OUTPUT)

    def read(self):
        if self.isMcp:
            return self.mcp_pin.value
        else:
            return pi.read(self.pin)

    def write(self, value):
        if self.isMcp:
            self.mcp_pin.value = value
        else:
            pi.write(self.pin, pigpio.HIGH if value else pigpio.LOW)

    def set_servo(self, pulsewidth):  # pulsewidth 500 - 2500
        if not self.isMcp:
            pi.set_servo_pulsewidth(self.pin, pulsewidth)
        else:
            raise Exception("The MCP23017 doesn't support pwm")

    def set_pwm(self, pulsewidth):  # 0-100
        if not self.isMcp:
            pi.set_PWM_dutycycle(self.pin, round(pulsewidth/100*255))
        else:
            raise Exception("The MCP23017 doesn't support pwm")

    def reset_servo(self):
        self.set_servo(0)


if __name__ == '__main__':
    print("running test")

    mcp = mcp1
    p = mcp.get_pin(6)
    p.switch_to_output(value=True)
    p.value = True

    usesmbus = False
    if usesmbus:
        import smbus

        bus = smbus.SMBus(1)
        ad = 0x20

        bus.write_byte_data(ad, 0x00, 0x00)
        bus.write_byte_data(ad, 0x14, 0xFE)
        time.sleep(3)
        bus.write_byte_data(ad, 0x14, 0x00)

