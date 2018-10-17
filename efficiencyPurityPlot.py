
#External Dependencies
import sys
import math
import numpy as np
import ROOT as root
from array import array

#Internal Dependencies
from dataTypes import *
import driver

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    angles = driver.generateAngles(len(wirePitches))

    numbersOfBlobs = [3]
    alphas = np.linspace(0.01,0.1,11)

    numberOfIterations = 100

    for numberOfBlobs in numbersOfBlobs:
        efficiency = array( 'f', len(alphas)*[ 0. ] )
        purity = array( 'f', len(alphas)*[ 0. ] )
        c1 = root.TCanvas( "PuriyEfficiencyCanvas", "PuriyEfficiencyCanvas", 200, 10, 700, 500 )
        for pointNo, alpha in enumerate(alphas):

            correctSum = 0
            fakeSum = 0

            for i in range(numberOfIterations):
                blobs, cells, channelList, geometryMatrix, recoWireMatrix, recoCellMatrix, trueCellMatrix = driver.drive(volume, wirePitches, angles, numberOfBlobs, alpha)

                recoCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),recoCellMatrix))
                trueCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),trueCellMatrix))

                correctID = sum(bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))
                fakeID = sum(not bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))

                correctSum += correctID/len(blobs)
                fakeSum += fakeID/len(blobs)

            efficiency[pointNo] = correctSum/numberOfIterations
            purity[pointNo] = 1 - fakeSum/numberOfIterations

        g =  root.TGraph(len(alphas), efficiency, purity)

        g.SetTitle("Efficiency vs Purity")
        g.GetYaxis().SetTitle("purity")
        g.GetXaxis().SetTitle("efficiency")
        g.GetYaxis().SetTitleSize(0.04)
        g.GetYaxis().SetTitleOffset(1.2)
        g.GetYaxis().SetLabelSize(0.04)
        g.GetXaxis().SetTitleSize(0.04)
        g.GetXaxis().SetTitleOffset(1)
        g.GetXaxis().SetLabelSize(0.04)

        # g.Draw("A*")
        g.Draw()
    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
