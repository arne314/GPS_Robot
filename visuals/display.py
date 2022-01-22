import time
import threading
import socket
from PIL import Image, ImageDraw, ImageFont

import board
import busio
import adafruit_ssd1306

from backend.logger import *
import sensors.gpsreceiver as gps

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
font = ImageFont.load_default()


def init():
    oled.fill(0)
    oled.show()


def new_image():
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    return image, draw


def showText(text, size=10):
    image, draw = new_image()
    draw.text((0, 0), text=text, font=ImageFont.truetype("visuals/Roboto-Medium.ttf", size=size), fill=255)
    oled.image(image)
    oled.show()


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def displayWorker(log: BackendHandler, follower):
    while True:
        try:
            if follower.running:
                follower_text = f"Head: {round(follower.heading)} Err: {round(follower.error)}"
            else:
                follower_text = ""
            text = f"IP: {get_ip()} GPS: {gps.number_satellites}\n" \
                   f"{follower_text}\n" \
                   f"{log.log_messages_display[-1]}\n" \
                   f"{log.log_messages_display[-2]}\n" \
                   f"{log.log_messages_display[-3]}\n"
            showText(text)
        except OSError:
            logger.log(logging.INFO, "Failed to communicate with display")
        time.sleep(0.5)


def startDisplayThread(log, follower):
    threading.Thread(target=displayWorker, args=(log, follower)).start()
