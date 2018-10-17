
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
    alphas = [0.01]

    numberOfIterations = 100

    for numberOfBlobs in numbersOfBlobs:
        for alpha in alphas:
            c1 = root.TCanvas( "RecoRateCanvas", "RecoRateCanvas", 200, 10, 700, 500 )

            correctFractions = root.TH1F("correctFractions", ("Correct Identification Fraction"), 100, -0.1, 1.1)
            fakeFractions = root.TH1F("fakeFractions", ("Fake Identification Fraction"), 100, -0.1, 1.1)
            for i in range(numberOfIterations):
                blobs, cells, channelList, geometryMatrix, recoWireMatrix, recoCellMatrix, trueCellMatrix = driver.drive(volume, wirePitches, angles, numberOfBlobs, alpha)

                recoCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),recoCellMatrix))
                trueCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),trueCellMatrix))

                correctID = sum(bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))
                fakeID = sum(not bool(x[0]) and bool(x[1]) for x in zip(trueCells,recoCells))

                correctFraction = correctID/len(blobs)
                fakeFraction = fakeID/len(blobs)

                correctFractions.Fill(correctFraction)
                fakeFractions.Fill(fakeFraction)

            correctFractions.SetTitle("")
            correctFractions.GetYaxis().SetTitleSize(0.04)
            correctFractions.GetYaxis().SetTitleOffset(1.2)
            correctFractions.GetYaxis().SetLabelSize(0.04)
            correctFractions.GetXaxis().SetTitleSize(0.04)
            correctFractions.GetXaxis().SetTitleOffset(1)
            correctFractions.GetXaxis().SetLabelSize(0.04)

            correctFractions.SetLineWidth(2)
            fakeFractions.SetLineWidth(2)

            # correctFractions.SetLineStyle(2)
            fakeFractions.SetLineStyle(2)

            correctFractions.SetLineColor(root.kBlue)
            fakeFractions.SetLineColor(root.kRed)

            root.gStyle.SetOptStat(0)

            correctFractions.Draw("HIST")
            fakeFractions.Draw("HIST SAMES")

            root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
