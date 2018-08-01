from collections import namedtuple
from pprint import pprint
import sys
import numpy as np
import itertools
import math

# define data Structures
Point = namedtuple('Point', ['x', 'y'])
Point.__doc__ = '''A 2-dimensional coordinate'''
Point.x.__doc__ = '''x coordinate'''
Point.y.__doc__ = '''y coordinate'''

Line = namedtuple('Line', ['point0', 'point1'])
Line.__doc__ = '''A line defined by two points'''
Line.point0.__doc__ = '''First Point'''
Line.point1.__doc__ = '''Second Point'''

PlaneInfo = namedtuple('PlaneInfo', ['angle', 'pitch', 'noOfWires', 'translationFactor', 'sin', 'cos', 'gradient'])
PlaneInfo.__doc__ = '''List of information about planes'''
PlaneInfo.angle.__doc__ = '''angle by whitch plane is roatated'''
PlaneInfo.pitch.__doc__ = '''wire pitch for the plane'''
PlaneInfo.noOfWires.__doc__ = '''number of wires in the plane_'''
PlaneInfo.translationFactor.__doc__ = '''x offset for origin of the plane (y origin is always 0)'''
PlaneInfo.sin.__doc__ = '''sin of the plane angle'''
PlaneInfo.cos.__doc__ = '''cos of the plane angle'''
PlaneInfo.gradient.__doc__ = '''gradient of the wires in plane'''

DetectorVolume = namedtuple('DetectorVolume', ['width', 'height'])
DetectorVolume.__doc__ = '''2D dimensions of the detector'''
DetectorVolume.width.__doc__ = '''width of detector'''
DetectorVolume.height.__doc__ = '''height of detector'''


def generatePlaneInfo(wirePitches, volume):
    """Generates information about planes based on wire pitches and volume assuming equal angle between each plane and the next

    Parameters
    ----------
    wirePitches : int or tuple of int or float
        A list of wire pitches, each number corresponding to the pitch of each plane
    volume : DetectorVolume
        The width and height of the detector

    Returns
    -------
    list of Plane Info
        List of information regarding the planes.

    """
    individualAngle = math.pi / len(wirePitches)
    planes = []

    translationPoint = Point(volume.width, 0)

    for planeNo, pitch in enumerate(wirePitches):
        # basic angle calculations
        angle = individualAngle * (planeNo + 1)
        cos = math.cos(angle)
        sin = math.sin(angle)

        # Origin and number of wire calculations
        if (rotate(translationPoint, angle).x < 0):
            translationFactor = volume.width
            noOfWires = math.floor(
                (sin * volume.height - cos * translationFactor) / pitch)
        else:
            translationFactor = 0
            noOfWires = math.floor(
                (cos * volume.width + sin * volume.height) / pitch)

        # gradient calculations
        if(math.isclose(angle, math.pi, rel_tol=1e-5)):
            gradient = "INF"
        elif translationFactor == 0:
            gradient = math.tan(angle + math.pi / 2)
        else:
            gradient = math.tan(angle - math.pi / 2)

        planes.append(PlaneInfo(angle, pitch, noOfWires,
                                translationFactor, sin, cos, gradient))

    return planes


def wireNumberFromPoint(plane, point):
    return math.floor((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.translationFactor) / plane.pitch)

def fireWires(planes, track):
    firedWires = []

    for planeNo, plane in enumerate(planes):
        for pointNo, point in enumerate(track):
            wireNo = wireNumberFromPoint(plane, point)
            if pointNo == 0:
                min = wireNo
                max = wireNo
            elif wireNo > max:
                max = wireNo
            elif wireNo < min:
                min = wireNo

        firedWires.append(list(range(min, max + 1)))

    return firedWires


def generateEvent(planes, volume):
    event = []
    # for i in range(0,np.random.randint(2,15)):
    for i in range(0, 4):
        point0 = Point(np.random.random_sample() * volume.width,
                       np.random.random_sample() * volume.height)

        xOffset = point0.x + np.random.random_sample() * 30
        yOffset = point0.y + np.random.random_sample() * 30

        if xOffset > volume.width:
            xOffset = volume.width
        if yOffset > volume.height:
            yOffset = volume.height

        point1 = Point(xOffset, yOffset)

        wires = fireWires(planes, [point0, point1])

        if i == 0:
            event = wires
        event = [set(item[0]).union(item[1])
                 for item in list(zip(event, wires))]
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
    dist1 = plane.pitch * wires[1] + 1

    if plane.translationFactor > 0:
        point0 = Point(plane.translationFactor -
                       (dist0 * (-plane.cos)), dist0 * plane.sin)
        point1 = Point(plane.translationFactor -
                       (dist1 * (-plane.cos)), dist1 * plane.sin)
    else:
        point0 = Point(dist0 * plane.cos, dist0 * plane.sin)
        point1 = Point(dist1 * plane.cos, dist1 * plane.sin)

    if plane.gradient == "INF":
        line0 = Line(point0, Point(point0.x, point0.y + 1))
        line1 = Line(point1, Point(point1.x, point1.y + 1))
    else:
        line0 = Line(point0, Point(point0.x + 1, point0.y + plane.gradient))
        line1 = Line(point1, Point(point1.x + 1, point1.y + plane.gradient))

    return [line0, line1]


def lineIntersection(line0, line1):
    #Doesnt account for parallel line case
    px = ((line0.point0.x * line0.point1.y - line0.point0.y * line0.point1.x) * (line1.point0.x - line1.point1.x) - (line0.point0.x - line0.point1.x) * (line1.point0.x * line1.point1.y -
                                                                                                                                 line1.point0.y * line1.point1.x)) / ((line0.point0.x - line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x - line1.point1.x))
    py = ((line0.point0.x * line0.point1.y - line0.point0.y * line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x * line1.point1.y -
                                                                                                                                 line1.point0.y * line1.point1.x)) / ((line0.point0.x - line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x - line1.point1.x))
    return Point(px, py)

def wireIntersection(plane0, wire0, plane1, wire1):
    points = []
    Lines0 = makeLines(plane0, wire0)
    Lines1 = makeLines(plane1, wire1)

    points.append(lineIntersection(Lines0[0],Lines1[0]))
    points.append(lineIntersection(Lines0[1],Lines1[0]))
    points.append(lineIntersection(Lines0[0],Lines1[1]))
    points.append(lineIntersection(Lines0[1],Lines1[1]))

    return points

def checkCell(planes, wires):
    potentialPoints = []
    points = []

    for plane0 in range(0,len(wires)):
        for plane1 in  range(plane0+1,len(wires)):
            potentialPoints.extend(wireIntersection(planes[plane0], wires[plane0], planes[plane1], wires[plane1]))

    for point in potentialPoints:
        isPointInside = True
        for planeNo, plane in enumerate(planes):
            wire = wireNumberFromPoint(plane, point)
            if wire<wires[planeNo][0] or wire>wires[planeNo][1]:
                isPointInside = False
                print(wire<wires[planeNo][0],wire>wires[planeNo][1])
                print("\033[91m",wires[planeNo][0]," | ", wire, " | ", wires[planeNo][1],"\033[0m")
            else:
                print("\033[92m",wires[planeNo][0]," | ", wire, " | ", wires[planeNo][1],"\033[0m")
        if isPointInside or not isPointInside:
            points.append(point)
        print("\n")

    # print(points)

    if len(points) <=2:
        return False
    else:
        return mergeEvent(fireWires(planes,points)),points

def rotate(point, angle):
    # counterClockwise turn of axis
    return Point(point.x * math.cos(angle) + point.y * (math.sin(angle)), point.x * (-math.sin(angle)) + point.y * math.cos(angle))

################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    planes = generatePlaneInfo(wirePitches, volume)
    # event = generateEvent(planes,volume)
    # event = mergeEvent(event)

    blob = mergeEvent(fireWires(planes,[Point(300,300),Point(500,500)]))
    pprint(blob)
    blob = list(itertools.chain(*blob))
    pprint(checkCell(planes,blob))


    # pprint(wireIntersection(planes[0], (10,50), planes[1], (200,300)))


    # pprint(planes)
    # pprint(event)

if __name__ == "__main__":
    main(sys.argv)
