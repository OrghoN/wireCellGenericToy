from collections import namedtuple
from pprint import pprint
import numpy as np
import itertools
import math

# define data Structures
Point = namedtuple('Point', ['x', 'y'])
PlaneInfo = namedtuple('PlaneInfo', ['angle', 'pitch', 'noOfWires', 'translationFactor', 'sin', 'cos', 'gradient'])
DetectorVolume = namedtuple('DetectorVolume', ['width', 'height'])

def generatePlaneInfo(wirePitches, volume):
    individualAngle = math.pi / len(wirePitches)
    planes = []

    translationPoint = Point(volume.width, 0)

    for planeNo, pitch in enumerate(wirePitches):
        #basic angle calculations
        angle = individualAngle * (planeNo + 1)
        cos = math.cos(angle)
        sin = math.sin(angle)

        #Origin and number of wire calculations
        if (rotate(translationPoint, angle).x < 0):
            translationFactor = volume.width
            noOfWires = math.floor(
                (sin * volume.height - cos * translationFactor) / pitch)
        else:
            translationFactor = 0
            noOfWires = math.floor(
                (cos * volume.width + sin * volume.height) / pitch)

        #gradient calculations
        if(math.isclose(angle, math.pi, rel_tol=1e-5)):
            gradient = "INF"
        elif translationFactor == 0:
            gradient = math.tan(angle+math.pi/2)
        else:
            gradient = math.tan(angle-math.pi/2)

        planes.append(PlaneInfo(angle, pitch, noOfWires, translationFactor, sin, cos, gradient))

    return planes

def wireNumberFromPoint(plane, point):
    return math.floor((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.translationFactor) / plane.pitch)

def fireWires(planes, track):
    firedWires = []

    for planeNo, plane in enumerate(planes):
        wire0 = wireNumberFromPoint(plane, track[0])
        wire1 = wireNumberFromPoint(plane, track[1])

        if wire0 > wire1:
            wire0, wire1 = wire1, wire0

        firedWires.append(list(range(wire0, wire1 + 1)))

    return firedWires

def generateEvent(planes,volume):
    event = []
    # for i in range(0,np.random.randint(2,15)):
    for i in range(0,4):
        point0 = Point(np.random.random_sample()*volume.width,np.random.random_sample()*volume.height)

        xOffset = point0.x + np.random.random_sample()*30
        yOffset = point0.y + np.random.random_sample()*30

        if xOffset > volume.width:
            xOffset = volume.width
        if yOffset > volume.height:
            yOffset = volume.height

        point1 = Point(xOffset,yOffset)

        wires = fireWires(planes, [point0,point1])

        if i == 0:
            event = wires
        event = [set(item[0]).union(item[1]) for item in list(zip(event, wires))]
    return event

def createMergedWires(firedWirePrimitives):
    firedWirePrimitives = sorted(set(firedWirePrimitives))
    gaps = [[s, e] for s, e in zip(
        firedWirePrimitives, firedWirePrimitives[1:]) if s + 1 < e]
    edges = iter(firedWirePrimitives[:1] +
                 sum(gaps, []) + firedWirePrimitives[-1:])
    return list(zip(edges, edges))

def mergeEvent(event):
    mergedEvent = []
    for plane in event:
        mergedEvent.append(createMergedWires(plane))

    return mergedEvent

def makeLines(plane, wires):
    dist0 = plane.pitch * wires[0]
    dist1 = plane.pitch * wires[1]+1

    if plane.translationFactor > 0:
        point0 = Point(plane.translationFactor - (dist0*(-plane.cos)),dist0*plane.sin)
        point1 = Point(plane.translationFactor - (dist1*(-plane.cos)),dist1*plane.sin)
    else:
        point0 = Point(dist0*plane.cos,dist0*plane.sin)
        point1 = Point(dist1*plane.cos,dist1*plane.sin)

    if plane.gradient == "INF":
        line0 = [point0,Point(point0.x,point0.y+1)]
        line1 = [point1,Point(point1.x,point1.y+1)]
    else:
        line0 = [point0,Point(point0.x+1,point0.y+plane.gradient)]
        line1 = [point1,Point(point1.x+1,point1.y+plane.gradient)]

    return [line0,line1]

    return True

# counterClockwise turn of axis
def rotate(point, angle):
    return Point(point.x * math.cos(angle) + point.y * (math.sin(angle)), point.x * (-math.sin(angle)) + point.y * math.cos(angle))



# def checkCell(planes,wires):


def intersectionToCell(planes, points):
    cell = []
    for plane in planes:
        wires = []
        for point in point:
            wires.append(wireNumberFromPoint(point))
        cell.append((min(wires), max(wires)))

    return cell

# def generateCells(planes, volume):
#     #find out min pitch
#     minPitch = min(planes, key = lambda t: t.pitch).pitch
#
#     yNumber = math.ceil(volume.height/minPitch)
#     xNumber = math.ceil(volume.width/minPitch)
#
#     i = 0
#
#     for y in range(0,yNumber):
#         for x in range(0,xNumber):
#             point = Point(x*minPitch+minPitch/2,y*minPitch+minPitch/2)
#             if(i%1000==0):
#                 print(i)
#             i+=1
#             for plane in planes:
#                 wireNumberFromPoint(plane, point)
#
#     return False


volume = DetectorVolume(1000.0, 1000.0)
wirePitches = [5.0, 5.0, 5.0]

planes = generatePlaneInfo(wirePitches, volume)
# event = generateEvent(planes,volume)
# event = mergeEvent(event)
# pprint(event)
# pprint(firedWires)
# generateCells(planes,volume)
# pprint(planes)
