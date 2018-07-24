from collections import namedtuple
from pprint import pprint
import math

#define data Structures
Point = namedtuple('Point', ['x', 'y'])
PlaneInfo = namedtuple('PlaneInfo',['angle','pitch','noOfWires','translationFactor'])
DetectorVolume = namedtuple('DetectorVolume',['width','height'])

#counterClockwise turn of axis
def rotate(point, angle):
    return Point(point.x*math.cos(angle)+point.y*(math.sin(angle)),point.x*(-math.sin(angle))+point.y*math.cos(angle))

def wireNumberFromPoint(plane, point):
    return math.floor(math.cos(plane.angle)*point.x+math.sin(plane.angle)*point.y-math.cos(plane.angle)*palne.translationFactor)

def generatePlaneInfo(wirePitches, volume):
    individualAngle = math.pi/len(wirePitches)
    planes = []

    translationPoint = Point(volume.width,0)

    for planeNo, pitch in enumerate(wirePitches):
        angle = individualAngle*(planeNo+1)

        if (rotate(translationPoint, angle).x<0):
            translationFactor = volume.width
            noOfWires = math.floor((math.sin(angle)*volume.height - math.cos(angle)*translationFactor)/pitch)
        else:
            translationFactor = 0
            noOfWires = math.floor((math.cos(angle)*volume.width + math.sin(angle)*volume.height - math.cos(angle)*translationFactor)/pitch)

        planes.append(PlaneInfo(angle,pitch,noOfWires,translationFactor))

    return planes

volume = DetectorVolume(1000.0, 1000.0)
wirePitches = [5.0,5.0,5.0,5.0]

planes = generatePlaneInfo(wirePitches,volume)

pprint(planes)
