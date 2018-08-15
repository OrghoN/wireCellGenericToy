
from pprint import pprint
from sklearn import linear_model
import sys
import numpy as np
import itertools
import math
from scipy.spatial import ConvexHull

from dataTypes import *

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
    return math.floor((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.originTranslation) / plane.pitch)
    # return round((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.originTranslation) / plane.pitch)

def fireWires(planes, points):
    """Show which wires have been hit for a given blob

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    points : list of points
        points defining ConvexHull of blob

    Returns
    -------
    2d list of int
        A list that has lists of wire numbers. one list for every plane

    """
    firedWires = []
    for planeNo, plane in enumerate(planes):
        for pointNo, point in enumerate(points):
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

def generateBlobs(planes,volume):
    blobs = []

    for i in range(0,np.random.randint(2,15)):
    # for i in range(0, 4):
        point0 = Point(np.random.random_sample() * volume.width,
                       np.random.random_sample() * volume.height)

        #30 set as arbitrary max length of blob
        xOffset = point0.x + np.random.random_sample() * 30
        yOffset = point0.y + np.random.random_sample() * 30

        if xOffset > volume.width:
            xOffset = volume.width
        if yOffset > volume.height:
            yOffset = volume.height

        point1 = Point(xOffset, yOffset)

        #charge calculations
        meanCharge, sigmaCharge = 5, 0.5
        charge = np.random.normal(meanCharge, sigmaCharge)

        blobs.append(Blob(charge, list(itertools.chain(*mergeEvent(fireWires(planes,[point0,point1])))), [point0,point1]))

    return blobs



def generateEvent(planes, blobs):
    event = []
    for blobNo, blob in enumerate(blobs):
        wires = fireWires(planes, blob.points)

        if blobNo == 0:
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
    #TODO talk about approximation done here and avoiding magic numbers
    dist1 = plane.pitch * (wires[1] + 1)-0.0000001

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

def sortPoints(points):
    sortedPoints = []
    hull = ConvexHull(points)

    for pointNo in (hull.vertices):
        sortedPoints.append(points[pointNo])
        # sortedPoints.append(hull.points[pointNo])

    return sortedPoints

def checkCell(planes, wires):
    points = []
    # print(wires)

    for plane0 in range(0,len(wires)):
        for plane1 in  range(plane0+1,len(wires)):
            # print("Planes",plane0,plane1)
            potentialPoints = wireIntersection(planes[plane0], wires[plane0], planes[plane1], wires[plane1])

            for point in potentialPoints:
                isPointInside = True
                for planeNo, plane in enumerate(planes):
                    wire = wireNumberFromPoint(plane, point)
                    if planeNo == plane0 or planeNo == plane1:
                        continue
                    else:
                        if wire<wires[planeNo][0] or wire>wires[planeNo][1]:
                            isPointInside = False

                if isPointInside:
                    # print("\033[92m",wireNumberFromPoint(planes[0], point), wireNumberFromPoint(planes[1], point), wireNumberFromPoint(planes[2], point),point,"\033[0m")
                    points.append(point)
                # else:
                    # print("\033[91m",wireNumberFromPoint(planes[0], point), wireNumberFromPoint(planes[1], point), wireNumberFromPoint(planes[2], point),point,"\033[0m")

    if len(points) <=2:
        return Cell(False, False)
    else:
        potentialWires = list(itertools.chain(*mergeEvent(fireWires(planes,points))))
        # potentialWires = list(map(lambda x: (max((x[0][0],x[1][0])),min((x[0][1],x[1][1]))),zip(wires,potentialWires)))
        points = sortPoints(points)
        return Cell(potentialWires,points)
        # return Cell(wires,points)

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
            # print("\033[91m",wire, "\033[0m")
            trueWire = (getTrueWireNo(planes,wire[0],planeNo),getTrueWireNo(planes,wire[1],planeNo))
            # print("\033[93m",trueWire, "\033[0m")

            if trueWire not in wires:
                wires.append(trueWire)
                matrix.append(list(np.zeros(len(cells),dtype=int)))

            matrix[wires.index(trueWire)][cellNo] = 1

    return wires, np.matrix(matrix)

def blobInCell(blob,cell):
    for planeNo in range(len(cell.wires)):
        # print(blob.wires[planeNo],"||",cell.wires[planeNo])
        if blob.wires[planeNo][0]<cell.wires[planeNo][0] or blob.wires[planeNo][1]>cell.wires[planeNo][1]:
            return False
    return True

def generateTrueCellMatrix(blobs,cells):
    matrix = list(np.zeros((len(cells),1)))

    for blob in blobs:
        for cellNo, cell in enumerate(cells):
            if(blobInCell(blob,cell)):
                # matrix[cellNo] = True
                matrix[cellNo][0] += blob.charge
                break

    # print(matrix)
    return np.matrix(matrix)

def generateCharge(planes,blobs):
    chargeMatrix = []

    for plane in planes:
        chargeMatrix.append(list(np.zeros(plane.noOfWires,dtype=int)))

    for blob in blobs:
        wires = fireWires(planes,blob.points)
        for planeNo, plane in enumerate(wires):
            charge = blob.charge/(len(plane))
            for wireNo in plane:
                chargeMatrix[planeNo][wireNo] += charge

    return chargeMatrix

def measureCharge(wireList,chargeMatrix):
    charges = []
    chargeMatrix = list(itertools.chain(*chargeMatrix))

    for wire in wireList:
        charge = 0
        test = []
        for i in range(wire[0],wire[1]+1):
            charge += chargeMatrix[i]

        charges.append(charge)

    return np.matrix(charges)

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

    blobs = generateBlobs(planes,volume)

    event = generateEvent(planes,blobs)
    event = mergeEvent(event)

    cells = generateCells(planes,event)

    wireList, geomMatrix = generateMatrix(planes,cells)

    # pprint(wireList)

    chargeMatrix = generateCharge(planes,blobs)
    charge = measureCharge(wireList,chargeMatrix)

    trueCellCharge = generateTrueCellMatrix(blobs,cells)
    trueWireCharge = geomMatrix * trueCellCharge


    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")
    print("\033[93m","Number of Merged Wires:", np.shape(geomMatrix)[0],"\033[0m")
    print("\033[93m","Number of Cells:", np.shape(geomMatrix)[1],"\033[0m")

    pprint(trueCellCharge)
    pprint(trueCellCharge.shape)
    # pprint(geomMatrix)
    # pprint(geomMatrix.shape)
    # pprint(trueWireCharge)
    # pprint(trueWireCharge.shape)

    chargeSolving = linear_model.Lasso(positive = True, alpha=0.14)
    chargeSolving.fit(geomMatrix,trueWireCharge)

    solved = np.matrix(chargeSolving.coef_.reshape(trueCellCharge.shape))
    print("\033[92m",solved,"\033[0m")


    # pprint(planes)


if __name__ == "__main__":
    main(sys.argv)
