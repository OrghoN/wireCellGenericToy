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
    return math.floor((math.cos(plane.angle)*point.x+math.sin(plane.angle)*point.y-math.cos(plane.angle)*plane.translationFactor)/plane.pitch)

def intersectionToCell(planes, points):
    cell = []
    for plane in planes:
        wires = []
        for point in point:
            wires.append(wireNumberFromPoint(point))
        cell.append((min(wires),max(wires)))

    return cell

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
            noOfWires = math.floor((math.cos(angle)*volume.width + math.sin(angle)*volume.height)/pitch)

        planes.append(PlaneInfo(angle,pitch,noOfWires,translationFactor))

    return planes

def createMergedWires(firedWirePrimitives):
    firedWirePrimitives = sorted(set(firedWirePrimitives))
    gaps = [[s, e] for s, e in zip(firedWirePrimitives, firedWirePrimitives[1:]) if s+1 < e]
    edges = iter(firedWirePrimitives[:1] + sum(gaps, []) + firedWirePrimitives[-1:])
    return list(zip(edges, edges))

def fireWires(planes, track):
    firedWires = []

    for planeNo, plane in enumerate(planes):
        wire0 = wireNumberFromPoint(plane,track[0])
        wire1 = wireNumberFromPoint(plane,track[1])

        if wire0 > wire1:
            wire0, wire1 = wire1, wire0

        firedWires.append(list(range(wire0,wire1+1)))

    return firedWires

def generateCells(planes, volume):
    #find out min pitch
    minPitch = min(planes, key = lambda t: t.pitch).pitch

    yNumber = math.ceil(volume.height/minPitch)
    xNumber = math.ceil(volume.width/minPitch)

    i = 0

    for y in range(0,yNumber):
        for x in range(0,xNumber):
            point = Point(x*minPitch+minPitch/2,y*minPitch+minPitch/2)
            if(i%1000==0):
                print(i)
            i+=1
            for plane in planes:
                wireNumberFromPoint(plane, point)

    return False


volume = DetectorVolume(1000.0, 1000.0)
wirePitches = [5.0,5.0,5.0]

planes = generatePlaneInfo(wirePitches,volume)
firedWires = fireWires(planes, [Point(250,150),Point(300,250)])
# pprint(firedWires)
# generateCells(planes,volume)
# pprint(planes)
