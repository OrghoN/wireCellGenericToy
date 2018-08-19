# External Dependencies
import numpy as np

# Internal Dependencies
from dataTypes import *

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
