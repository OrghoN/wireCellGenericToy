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

PlaneInfo = namedtuple('PlaneInfo', ['angle', 'pitch', 'noOfWires', 'originTranslation', 'wireTranslation','sin', 'cos', 'gradient'])
PlaneInfo.__doc__ = '''List of information about planes'''
PlaneInfo.angle.__doc__ = '''angle by whitch plane is roatated'''
PlaneInfo.pitch.__doc__ = '''wire pitch for the plane'''
PlaneInfo.noOfWires.__doc__ = '''number of wires in the plane'''
PlaneInfo.originTranslation.__doc__ = '''x offset for origin of the plane (y origin is always 0)'''
PlaneInfo.wireTranslation.__doc__ = '''x offset for the first wire from origin of plane'''
PlaneInfo.sin.__doc__ = '''sin of the plane angle'''
PlaneInfo.cos.__doc__ = '''cos of the plane angle'''
PlaneInfo.gradient.__doc__ = '''gradient of the wires in plane'''

DetectorVolume = namedtuple('DetectorVolume', ['width', 'height'])
DetectorVolume.__doc__ = '''2D dimensions of the detector'''
DetectorVolume.width.__doc__ = '''width of detector'''
DetectorVolume.height.__doc__ = '''height of detector'''

Cell = namedtuple('Cell', ['wires','points'])
Cell.__doc__='''Merged Cell in Detector'''
Cell.wires.__doc__='''binding wires of the cell'''
Cell.points.__doc__='''points binding the cell'''

def generateAngles(noOfPlanes):
    individualAngle = math.pi/noOfPlanes
    angles = []

    for planeNo in range(noOfPlanes):
        angles.append(individualAngle * (planeNo + 1))

    return angles

def generatePlaneInfo(wirePitches, volume, angles, wireTranslations):
    """Generates information about planes based on wire pitches and volume assuming equal angle between each plane and the next

    Parameters
    ----------
    wirePitches : int or tuple of int or float
        A list of wire pitches, each number corresponding to the pitch of each plane
    volume : DetectorVolume
        The width and height of the detector

    Returns
    -------
    list of PlaneInfo
        List of information regarding the planes.

    """
    planes = []

    translationPoint = Point(volume.width, 0)

    for planeNo, pitch in enumerate(wirePitches):
        # basic angle calculations
        angle = angles[planeNo]
        cos = math.cos(angle)
        sin = math.sin(angle)

        # Origin and number of wire calculations
        if (rotate(translationPoint, angle).x < 0):
            originTranslation = volume.width
            noOfWires = math.floor(
                (sin * volume.height - cos * originTranslation) / pitch)
        else:
            originTranslation = 0
            noOfWires = math.floor(
                (cos * volume.width + sin * volume.height) / pitch)

        # gradient calculations
        if(math.isclose(angle, math.pi, rel_tol=1e-5)):
            gradient = "INF"
        elif originTranslation == 0:
            gradient = math.tan(angle + math.pi / 2)
        else:
            gradient = math.tan(angle - math.pi / 2)

        planes.append(PlaneInfo(angle, pitch, noOfWires,
                                originTranslation, wireTranslations[planeNo], sin, cos, gradient))

    return planes


def wireNumberFromPoint(plane, point):
    """Generates the wire number for a point given a certain plane

    Parameters
    ----------
    plane : PlaneInfo
        Plane information for the plane the wire number is for
    point : Point
        The point being queried

    Returns
    -------
    int
        Wire number

    """
    return round((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.originTranslation) / plane.pitch)

def fireWires(planes, track):
    """Show which wires have been hit for a given track

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    track : list of Points
        List containing the points that define the convex hull of a blob

    Returns
    -------
    2d list of int
        A list that has lists of wire numbers. one list for every plane

    """
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

def generateTracks(planes,volume):
    tracks = []

    for i in range(0,np.random.randint(2,15)):
    # for i in range(0, 4):
        point0 = Point(np.random.random_sample() * volume.width,
                       np.random.random_sample() * volume.height)

        xOffset = point0.x + np.random.random_sample() * 30
        yOffset = point0.y + np.random.random_sample() * 30

        if xOffset > volume.width:
            xOffset = volume.width
        if yOffset > volume.height:
            yOffset = volume.height

        point1 = Point(xOffset, yOffset)

        tracks.append([point0,point1])

    return tracks



def generateEvent(planes, tracks):
    event = []
    for trackNo, track in enumerate(tracks):
        wires = fireWires(planes, track)

        if trackNo == 0:
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

    if plane.originTranslation > 0:
        point0 = Point(plane.originTranslation -
                       (dist0 * (-plane.cos)), dist0 * plane.sin)
        point1 = Point(plane.originTranslation -
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
            # print(plane0,plane1)
            potentialPoints.extend(wireIntersection(planes[plane0], wires[plane0], planes[plane1], wires[plane1]))

    for point in potentialPoints:
        isPointInside = True
        for planeNo, plane in enumerate(planes):
            wire = wireNumberFromPoint(plane, point)
            if wire<wires[planeNo][0] or wire>wires[planeNo][1]:
                isPointInside = False
                # print(wire<wires[planeNo][0],wire>wires[planeNo][1])
                # print("\033[91m",wires[planeNo][0]," | ", wire, " | ", wires[planeNo][1],"\033[0m")
            # else:
                # print("\033[92m",wires[planeNo][0]," | ", wire, " | ", wires[planeNo][1],"\033[0m")
        if isPointInside:
            points.append(point)

    # print(points)

    if len(points) <=2:
        return Cell(False, False)
    else:
        return Cell(list(itertools.chain(*mergeEvent(fireWires(planes,points)))),points)

def generateCells(planes,event):
    cells = []
    potentialCells = list(itertools.product(*event))
    for potentialCell in potentialCells:
        cell = checkCell(planes, potentialCell)
        if cell[0] == False:
            continue
        else:
            cells.append(cell)

    return cells

def getTrueWireNo(planes, wireNo, planeNo):
    trueWireNo = 0

    for plane in range(0,planeNo):
        trueWireNo += planes[plane].noOfWires

    trueWireNo += wireNo

    return trueWireNo

def generateMatrix(planes, cells):
    cellBindings = []
    wires = []
    matrix = []

    for cellNo, cell in enumerate(cells):
        for planeNo, wire in enumerate(cell.wires):
            trueWire = (getTrueWireNo(planes,wire[0],planeNo),getTrueWireNo(planes,wire[0],planeNo))

            if trueWire not in wires:
                wires.append(trueWire)
                matrix.append(list(np.zeros(len(cells),dtype=int)))

            matrix[wires.index(trueWire)][cellNo] = 1

    return wires, matrix

def generateCharge(planes,tracks):
    charge = []

    meanCharge, sigmaCharge = 5, 0.1

    for plane in planes:
        charge.append(list(np.zeros(plane.noOfWires,dtype=int)))

    for track in tracks:
        wires = fireWires(planes,track)
        for planeNo, plane in enumerate(wires):
            for wireNo in plane:
                # TODO:  uncertainity later
                charge[planeNo][wireNo] = np.random.normal(meanCharge, sigmaCharge)

    return charge

def measureCharge(wireList,chargeMatrix):
    charges = []
    chargeMatrix = list(itertools.chain(*chargeMatrix))

    for wire in wireList:
        charge = 0

        for i in range(wire[0],wire[1]+1):
            charge += chargeMatrix[i]

        charges.append(charge)

    return charges

def rotate(point, angle):
    # counterClockwise turn of axis
    return Point(point.x * math.cos(angle) + point.y * (math.sin(angle)), point.x * (-math.sin(angle)) + point.y * math.cos(angle))

################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    wireTranslations = [0.0,0.0,0.0]
    angles = generateAngles(len(wirePitches))

    planes = generatePlaneInfo(wirePitches, volume, angles, wireTranslations)

    tracks = generateTracks(planes,volume)

    event = generateEvent(planes,tracks)
    event = mergeEvent(event)

    cells = generateCells(planes,event)

    wireList, matrix = generateMatrix(planes,cells)

    chargeMatrix = generateCharge(planes,tracks)
    charge = measureCharge(wireList,chargeMatrix)

    pprint(charge)

    # pprint(event)

    # pprint(planes)

    # for row in matrix:
    #     print(row)


if __name__ == "__main__":
    main(sys.argv)
