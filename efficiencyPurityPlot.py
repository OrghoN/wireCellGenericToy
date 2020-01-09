# External Dependencies
import sys
import math
import numpy as np
import ROOT as root
from array import array

# Internal Dependencies
from dataTypes import *
import driver
import draw

def efficiencyPurityGraph(volume, wirePitches, angles, numberOfBlobs, alphas, numberOfIterations):
    efficiency = array('f', len(alphas) * [0.])
    purity = array('f', len(alphas) * [0.])

    eventNo = 0
    for pointNo, alpha in enumerate(alphas):
        correctSum = 0
        fakeSum = 0

        for i in range(numberOfIterations):
            blobs, cells, channelList, geometryMatrix, recoWireMatrix, recoCellMatrix, trueCellMatrix = driver.drive(
                volume, wirePitches, angles, numberOfBlobs, alpha)

            if (eventNo % 1000 == 0) or (eventNo == 0):
                print("Processed ", eventNo, "/", len(alphas)
                      * numberOfIterations, " events")

            eventNo += 1

            recoCells = list(map(lambda x: not math.isclose(
                x, 0, rel_tol=1e-5), recoCellMatrix))
            trueCells = list(map(lambda x: not math.isclose(
                x, 0, rel_tol=1e-5), trueCellMatrix))

            correctID = sum(bool(x[0]) and bool(x[1])
                            for x in zip(trueCells, recoCells))
            fakeID = sum(not bool(x[0]) and bool(x[1])
                         for x in zip(trueCells, recoCells))

            correctSum += correctID / len(blobs)
            fakeSum += fakeID / len(blobs)

        efficiency[pointNo] = correctSum / numberOfIterations
        purity[pointNo] = 1 - fakeSum / numberOfIterations

    g = root.TGraph(len(alphas), efficiency, purity)

    return g

if __name__ == "__main__":
    main(sys.argv)
