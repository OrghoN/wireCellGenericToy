from collections import namedtuple
from pprint import pprint
import numpy as np
import itertools
import math

# define data Structures
Point = namedtuple('Point', ['x', 'y'])
Point.__doc__ = '''A 2-dimensional coordinate'''
Point.x.__doc__ = '''x coordinate'''
Point.y.__doc__ = '''y coordinate'''

PlaneInfo = namedtuple('PlaneInfo', [
                       'angle', 'pitch', 'noOfWires', 'translationFactor', 'sin', 'cos', 'gradient'])
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
    @param wirePitches : list or tuple of int or float
        A list of wire pitches, each number corresponding to the pitch of each plane
    @param volume : Detector Volume
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
        wire0 = wireNumberFromPoint(plane, track[0])
        wire1 = wireNumberFromPoint(plane, track[1])

        if wire0 > wire1:
            wire0, wire1 = wire1, wire0

        firedWires.append(list(range(wire0, wire1 + 1)))

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
        line0 = [point0, Point(point0.x, point0.y + 1)]
        line1 = [point1, Point(point1.x, point1.y + 1)]
    else:
        line0 = [point0, Point(point0.x + 1, point0.y + plane.gradient)]
        line1 = [point1, Point(point1.x + 1, point1.y + plane.gradient)]

    return [line0, line1]


def lineIntersection(line0, line1):
    #Doesnt account for parallel line case
    px = ((line0[0][0] * line0[1][1] - line0[0][1] * line0[1][0]) * (line1[0][0] - line1[1][0]) - (line0[0][0] - line0[1][0]) * (line1[0][0] * line1[1][1] -
                                                                                                                                 line1[0][1] * line1[1][0])) / ((line0[0][0] - line0[1][0]) * (line1[0][1] - line1[1][1]) - (line0[0][1] - line0[1][1]) * (line1[0][0] - line1[1][0]))
    py = ((line0[0][0] * line0[1][1] - line0[0][1] * line0[1][0]) * (line1[0][1] - line1[1][1]) - (line0[0][1] - line0[1][1]) * (line1[0][0] * line1[1][1] -
                                                                                                                                 line1[0][1] * line1[1][0])) / ((line0[0][0] - line0[1][0]) * (line1[0][1] - line1[1][1]) - (line0[0][1] - line0[1][1]) * (line1[0][0] - line1[1][0]))
    return Point(px, py)

    # def findIntersection(line0[0][0],line0[0][1],line0[1][0],line0[1][1],line1[0][0],line1[0][1],line1[1][0],line1[1][1]):

# counterClockwise turn of axis


def rotate(point, angle):
    return Point(point.x * math.cos(angle) + point.y * (math.sin(angle)), point.x * (-math.sin(angle)) + point.y * math.cos(angle))


#
# def intersectionToCell(planes, points):
#     cell = []
#     for plane in planes:
#         wires = []
#         for point in point:
#             wires.append(wireNumberFromPoint(point))
#         cell.append((min(wires), max(wires)))
#
#     return cell


volume = DetectorVolume(1000.0, 1000.0)
wirePitches = [5.0, 5.0, 5.0]

line0 = [Point(-1,-1),Point(-1,1)]
line1 = [Point(-1,-1),Point(-1,1)]
pprint(lineIntersection(line0, line1))
planes = generatePlaneInfo(wirePitches, volume)
# event = generateEvent(planes,volume)
# event = mergeEvent(event)
# pprint(event)
# pprint(firedWires)
# generateCells(planes,volume)
# pprint(planes)
