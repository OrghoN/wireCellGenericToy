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
