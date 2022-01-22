import picamera
import time

camera = None


def init():
    global camera
    print("camera init")
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    print("camera initialized")


def start_recording():
    camera.start_recording(f'/home/pi/recordings/recording_{int(time.time())}.h264')
    print("Recording started")


def stop_recording():
    camera.stop_recording()
    print("Recording ended")
