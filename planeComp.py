# External Dependencies
import sys
import math
import numpy as np
import ROOT as root

# Internal Dependencies
from dataTypes import *
import driver
import efficiencyPurityPlot
import draw

def main(argv):
    #saveOptions
    directory = "img"
    fileName = "plane4Compl"

########################################################

    volume = DetectorVolume(1000.0, 1000.0)
    wirePitchList = [[5.0,5.0], [5.0, 5.0, 5.0], [5.0,5.0,5.0,5.0], [5.0,5.0,5.0,5.0, 5.0]]
    anglesList = list(map(lambda x: driver.generateAngles(len(x)), wirePitchList))

    numberOfBlobs = 3
    alphas = np.linspace(0.001, 1, 10)

    numberOfIterations = 10000

    c1 = root.TCanvas("PuriyEfficiencyCanvas",
                      "PuriyEfficiencyCanvas", 200, 10, 700, 500)

    legendPosition=[0.141834,0.151899,0.315186,0.35443]
    legend = root.TLegend(legendPosition[0], legendPosition[1], legendPosition[2], legendPosition[3])

    graphs = []
    colors = [root.kRed, root.kBlue, root.kGreen, 6]

    mg = root.TMultiGraph()

    for i, wirePitches in enumerate(wirePitchList):
        g = efficiencyPurityPlot.efficiencyPurityGraph(volume, wirePitches, anglesList[i], numberOfBlobs, alphas, numberOfIterations)
        legend.AddEntry(g,"Planes: " + str(len(wirePitches)),"l")
        g.SetLineColor(colors[i])
        mg.Add(g)
        graphs.append(g)

    mg.SetTitle("Efficiency vs Purity")
    mg.GetYaxis().SetTitle("purity")
    mg.GetXaxis().SetTitle("efficiency")
    mg.GetYaxis().SetTitleSize(0.04)
    mg.GetYaxis().SetTitleOffset(1.2)
    mg.GetYaxis().SetLabelSize(0.04)
    mg.GetXaxis().SetTitleSize(0.04)
    mg.GetXaxis().SetTitleOffset(1)
    mg.GetXaxis().SetLabelSize(0.04)

    mg.Draw("a*c")
        # g.Draw("A*")

    legend.SetFillColor(root.kWhite)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.043)

    legend.Draw()

    c1.Update()

    if isinstance(fileName, str) and len(fileName)>0:
        draw.saveImage(fileName,directory)

    # root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
