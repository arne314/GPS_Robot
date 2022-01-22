from flask import *

import sensors.gpsreceiver as gps
from sensors.compass import fetchDeclinationFromLocation
from driving.driving import RouteFollower
from visuals.display import *
import visuals.camera as cam
from utils import *
from backend.logger import *

app = Flask(__name__)
follower: RouteFollower = RouteFollower([])
backend_log: BackendHandler = BackendHandler()

version = None


def returnMsg(msg, code=200):
    return jsonify(msg=msg), code


def okReturn():
    return returnMsg("OK")


@app.route("/setRoute", methods=["POST"])
def setRoute():
    global follower
    follower.route = [Location(pos[0], pos[1], name=f"WP {num}") for num, pos in enumerate(request.json["route"], start=1)]
    logger.log(logging.INFO, "Route updated")
    logger.log(logging.DEBUG, f"Route updated: {follower.route}")
    return okReturn()


@app.route("/setOffset", methods=["POST"])
def setOffset():
    json = request.json
    offset = json["offset"]
    gps.latoffset = offset[0]
    gps.lngoffset = offset[1]

    if "fetchDeclination" in json and json["fetchDeclination"]:
        fetchDeclinationFromLocation(gps.getPosition())
    logger.log(logging.DEBUG, f"GPS offset is now: {gps.latoffset}, {gps.lngoffset}")
    return okReturn()


@app.route("/getStatus")
def getStatus():
    return jsonify(status=follower.currentTargetIndex, log=backend_log.get_new())


@app.route("/startRoute", methods=["POST"])
def startRoute():
    json = request.json
    if len(follower.route):
        if "restart" in json and json["restart"]:
            follower.restartRoute()
        follower.running = True
        logger.log(logging.INFO, "Following route")
        cam.start_recording()
        return okReturn()
    else:
        return returnMsg("No route set", 400)


@app.route("/stopRoute")
def stopRoute():
    follower.running = False
    logger.log(logging.INFO, "Paused remotely")
    cam.stop_recording()
    return okReturn()


@app.route("/getPosition", methods=["POST"])
def getPosition():
    json = request.json
    apply_offset = True
    if "raw" in json:
        apply_offset = not json["raw"]
    lat, lng = gps.getPosition(apply_offset=apply_offset).tuple
    return jsonify(lat=lat, lng=lng)


@app.route("/version")
def getVersion():
    return jsonify(ver=version)


@app.route("/<name>")
def otherPath(name):
    logger.log(logging.INFO, f"Invalid request: /{name}")
    return "Invalid request"


def init(ver):
    global version
    version = ver
    follower.start()
    setupLogger(backend_log)
    startDisplayThread(backend_log, follower)
    cam.init()
    logger.log(logging.INFO, "Robot software initialized")
    app.run(debug=False, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    init("development")
