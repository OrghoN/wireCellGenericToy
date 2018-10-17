# External Dependencies
import numpy as np
import itertools

# Internal Dependencies
from dataTypes import *
import utilities

def blobInCell(blob, cell):
    """Check if a True Blob is in a cell

    Parameters
    ----------
    blob : Blob
        The true Blob
    cell : Cell
        Reconstructed Cell

    Returns
    -------
    Boolean
        True if blob in cell, false otherwise

    """
    for planeNo in range(len(cell.wires)):
        if blob.wires[planeNo][0] < cell.wires[planeNo][0] or blob.wires[planeNo][1] > cell.wires[planeNo][1]:
            return False
    return True


def generateTrueCellMatrix(blobs, cells):
    """Generate the True charge matrix for cells

    Parameters
    ----------
    blobs : list of Blob
        List of True Blobs
    cells : list of Cell
        List of cells reconstructed with geometry

    Returns
    -------
    np.matrix
        Matrix denoting charge of each cell

    """
    matrix = list(np.zeros((len(cells), 1)))

    for blob in blobs:
        for cellNo, cell in enumerate(cells):
            if(blobInCell(blob, cell)):
                matrix[cellNo][0] += blob.charge
                break

    return np.matrix(matrix)

def constructGeometryMatrix(planes, cells):
    """Make a matrix that associates merged wires and cells based on detector Geometry

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    cells : list of Cell
        List of cells Reconstructed from Geometric information

    Returns
    -------
    list of tuple[2] int, np.matrix
        list of merged channels, Matrix that associates merged wire with merged cells

    """
    splittingList = []

    # createSplittingList
    for cellNo, cell in enumerate(cells):
        for planeNo, wire in enumerate(cell.wires):
            splittingList.append(utilities.getChannelNo(planes, wire[0], planeNo))
            splittingList.append(utilities.getChannelNo(planes, wire[1], planeNo)+1)

    #Sort and make list unique
    splittingList = list(set(splittingList))
    splittingList.sort()

    channelList = []
    matrix = []

    for cellNo, cell in enumerate(cells):
        for planeNo, wire in enumerate(cell.wires):
            channel0 = utilities.getChannelNo(planes, wire[0], planeNo)
            channel1 = utilities.getChannelNo(planes, wire[1], planeNo)

            for i in range(splittingList.index(channel0),splittingList.index(channel1+1)):
                mergedChannel = (splittingList[i],splittingList[i+1]-1)
                fractionalAssociation = (mergedChannel[1]-mergedChannel[0]+1)/(channel1-channel0+1)

                #Check if wire is already in list
                if mergedChannel not in channelList:
                    channelList.append(mergedChannel)
                    matrix.append(np.zeros(len(cells)))

                matrix[channelList.index(mergedChannel)][cellNo] = fractionalAssociation

    return channelList, np.matrix(matrix)

def constructChargeList(planes,blobs):
    chargeList = []

    for plane in planes:
        chargeList.append(list(np.zeros(plane.noOfWires,dtype=int)))

    for blob in blobs:
        wires = utilities.fireWires(planes,blob.points)
        for planeNo, plane in enumerate(wires):
            charge = blob.charge/(len(plane))
            for wireNo in plane:
                chargeList[planeNo][wireNo-1] += charge
            
    return chargeList

def measureCharge(wireList,chargeList):
    charges = []
    chargeList = list(itertools.chain(*chargeList))

    for wire in wireList:
        charge = 0
        test = []
        for i in range(wire[0],wire[1]+1):
            charge += chargeList[i]

        charges.append(charge)

    return np.reshape(np.matrix(charges),(len(wireList),1))

def addUncertainity(geometryMatrix,wireChargeMatrix,covarianceMatrix):
    invertedcovarianceMatrix = np.linalg.inv(covarianceMatrix)
    decomposedMatrix = np.linalg.cholesky(invertedcovarianceMatrix)

    #Adding Uncertaininty through Covariance Matrix
    wireChargeMatrixU = decomposedMatrix * wireChargeMatrix
    geometryMatrixU = decomposedMatrix * geometryMatrix

    return geometryMatrixU, wireChargeMatrixU
