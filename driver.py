#External Dependencies
import sys
import math
import numpy as np

#Internal Dependencies
from dataTypes import *
import utilities
import geometryGen
import geometryReco
import matrixGeneration
import chargeSolving

def generateAngles(noOfPlanes):
    individualAngle = math.pi/noOfPlanes
    angles = []

    for planeNo in range(noOfPlanes):
        angles.append(individualAngle * (planeNo + 1))

    return angles


def drive(volume, wirePitches, angles, noOfBlobs, alpha):
    planes = utilities.generatePlaneInfo(wirePitches, volume, angles)

    #Generating Random Blobs
    blobs = geometryGen.generateBlobs(planes,volume, noOfBlobs)

    #Creating Event
    event = geometryGen.generateEvent(planes,blobs)
    #Merging Event
    event = geometryGen.mergeEvent(event)

    #reconstructing cells based on geometry information
    cells = geometryReco.reconstructCells(planes,event)

    #create matrix associating wires and cells
    channelList, geometryMatrix = matrixGeneration.constructGeometryMatrix(planes, cells)

    #covariance Matrix
    covarianceMatrix = np.identity(len(channelList))

    #create Chrage Matrices
    masterChargeList = matrixGeneration.constructChargeList(planes,blobs)
    recoWireMatrix = matrixGeneration.measureCharge(channelList,masterChargeList)

    #solve
    geometryMatrixU, recoWireMatrixU = matrixGeneration.addUncertainity(geometryMatrix,recoWireMatrix,covarianceMatrix)

    recoCellMatrix = chargeSolving.solve(recoWireMatrixU, geometryMatrixU, alpha)
    trueCellMatrix = matrixGeneration.generateTrueCellMatrix(blobs,cells)

    return blobs, cells, channelList, geometryMatrix, recoWireMatrix, recoCellMatrix, trueCellMatrix

if __name__ == "__main__":

    #Defining Detector Geometry
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    angles = generateAngles(len(wirePitches))
    numberOfBlobs = 4
    alpha = 0.1

    blobs, cells, channelList, geometryMatrix, recoWireMatrix, recoCellMatrix, trueCellMatrix = drive(volume, wirePitches, angles, numberOfBlobs, alpha)

    recoCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),recoCellMatrix))
    trueCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),trueCellMatrix))

    correctID = sum(bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))
    fakeID = sum(not bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))

    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")
    print("\033[93m","Number of Cells:", len(cells),"\033[0m")

    print("reco cell Matrix:")
    print(recoCellMatrix)

    print("true cell Matrix:")
    print(trueCellMatrix)

    print(recoCells)
    print(trueCells)
    print(correctID)
    print(fakeID)
