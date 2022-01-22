from math import *

earth_radius = 6371000


class Location:
    lat: float
    lng: float
    name: str

    def __init__(self, lat, lng, name=None):
        self.lat = lat
        self.lng = lng
        self.name = name

    def toString(self):
        name = ""
        if self.name:
            name = f" ({self.name})"
        return f"Location{name}: {round(self.lat, 5)}, {round(self.lng, 5)}"

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def __add__(self, other):
        new = Location(0, 0)
        new.lat = self.lat + other.lat
        new.lng = self.lng + other.lng
        return new

    def __sub__(self, other):
        new = Location(0, 0)
        new.lat = self.lat - other.lat
        new.lng = self.lng - other.lng
        return new

    @property
    def tuple(self):
        return self.lat, self.lng

    def applyRadians(self):
        return Location(radians(self.lat), radians(self.lng))


def getBearing(l1: Location, l2: Location):
    l1, l2 = l1.applyRadians(), l2.applyRadians()
    deltalng = l2.lng - l1.lng
    return degrees(atan2(
        cos(l2.lat) * sin(deltalng),
        sin(l2.lat) * cos(l1.lat) - cos(l2.lat) * cos(deltalng) * sin(l1.lat)
    ))


def getDistance(l1: Location, l2: Location):
    delta = (l2 - l1).applyRadians()
    l1, l2 = l1.applyRadians(), l2.applyRadians()

    theta = acos(round(cos(l1.lat)*cos(l2.lat)*cos(delta.lng)+sin(l1.lat)*sin(l2.lat), 15))
    d = earth_radius * theta
    return d
