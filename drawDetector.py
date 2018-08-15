from collections import namedtuple
from sklearn import linear_model
from pprint import pprint
import sys
import numpy as np
import itertools
import math

from cellTable import Point
from cellTable import Line
from cellTable import PlaneInfo
from cellTable import DetectorVolume
from cellTable import Blob
import cellTable

import ROOT as root
from scipy.spatial import ConvexHull

def makeCenterLines(plane, wires):
    lines = []

    for wireNo in range(wires[0], wires[1]+1):
        dist = plane.pitch * wireNo + plane.pitch/2

        if plane.originTranslation > 0:
            point = Point(plane.originTranslation -
                           (dist * (-plane.cos)), dist * plane.sin)
        else:
            point = Point(dist * plane.cos, dist * plane.sin)

        if plane.gradient == "INF":
            line = Line(point, Point(point.x, point.y + 1))
        else:
            line = Line(point, Point(point.x + 1, point.y + plane.gradient))

        lines.append(line)

    return lines

def makeEventLines(planes, event, useCenterLines):
    lines = []

    for planeNo, plane in enumerate(event):
        for wire in plane:
            if (useCenterLines == "both"):
                centerLines = makeCenterLines(planes[planeNo],wire)
                centerLines = list(map(lambda line: (line,True),centerLines))
                lines.extend(centerLines)
                borderLines = cellTable.makeLines(planes[planeNo],wire)
                borderLines = list(map(lambda line: (line,False),borderLines))
                lines.extend(borderLines)
            elif useCenterLines:
                centerLines = makeCenterLines(planes[planeNo],wire)
                centerLines = list(map(lambda line: (line,True),centerLines))
                lines.extend(centerLines)
            else:
                borderLines = cellTable.makeLines(planes[planeNo],wire)
                borderLines = list(map(lambda line: (line,False),borderLines))
                lines.extend(borderLines)
    return lines

def drawEventLines(lines, volume):
    drawLines = []

    x0 = 0
    x1 = volume.width

    for lineNo, line in enumerate(lines):
        if(math.isclose(line[0][0].x, line[0][1].x, rel_tol=1e-5)):
            drawLine = root.TLine(line[0][0].x,0,line[0][0].x,volume.height)
        else:
            gradient = (line[0][1].y-line[0][0].y)/(line[0][1].x-line[0][0].x)
            y0 = gradient * x0 - gradient * line[0][0].x + line[0][0].y
            y1 = gradient * x1 - gradient * line[0][0].x + line[0][0].y
            drawLine = root.TLine(x0,y0,x1,y1)

        if line[1]:
            drawLine.SetLineColor(root.kBlue)
            drawLine.SetLineStyle(2)
        drawLines.append(drawLine)

    return drawLines

def drawBlobs(blobs):
    drawnBlobs = []

    for blob in blobs:
        for i in range(1, len(blob.points)):
            drawnBlobs.append(root.TLine(blob.points[i-1].x,blob.points[i-1].y,blob.points[i].x,blob.points[i].y))

        drawnBlobs.append(root.TLine(blob.points[-1].x,blob.points[-1].y,blob.points[0].x,blob.points[0].y))

    return drawnBlobs

def drawCells(cells, asMarker):
    drawnCells =[]

    if asMarker:
        for cell in cells:
            drawnCells.append(list(map(lambda p: root.TMarker(p.x,p.y,21), cell.points)))
    else:
        for cell in cells:
            drawnCell = []

            for i in range(1, len(cell.points)):
                drawnCell.append(root.TLine(cell.points[i-1].x,cell.points[i-1].y,cell.points[i].x,cell.points[i].y))

            drawnCell.append(root.TLine(cell.points[-1].x,cell.points[-1].y,cell.points[0].x,cell.points[0].y))

            drawnCells.append(drawnCell)
    return drawnCells

def drawCellNumbers(cells):
    numbers = []

    for cellNo, cell in enumerate(cells):
        center = np.mean(cell.points,axis=0)
        numbers.append(root.TText(center[0],center[1],str(cellNo)))


    return numbers

def drawCellPointNumbers(cell):
    numbers = []
    if cell[0] != False:
        for pointNo, point in enumerate(cell.points):
            numbers.append(root.TText(point.x,point.y,str(pointNo)))

    return numbers
################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    wireTranslations = [0.0,0.0,0.0]
    angles = cellTable.generateAngles(len(wirePitches))

    planes = cellTable.generatePlaneInfo(wirePitches, volume, angles, wireTranslations)

    reco = True
    trueBlobs = True
    asMarker = False
    cellNumbering = False
    useCenterLines = "both"

    # blobs = cellTable.generateBlobs(planes,volume)

    # print(blobs)
    blobs = [Blob(charge=4.58748705679011, wires=[(153, 159), (90, 93), (33, 37)], points=[Point(x=813.8436039106869, y=417.60082990853977), Point(x=830.2734426303631, y=440.38585607276224)]), Blob(charge=5.4507416355248655, wires=[(76, 79), (61, 62), (82, 85)], points=[Point(x=571.9607228368554, y=112.88215335645768), Point(x=588.5515032286443, y=118.44586995598164)]), Blob(charge=5.495377296955472, wires=[(17, 22), (105, 105), (183, 188)], points=[Point(x=58.71312010523644, y=68.38897935986054), Point(x=84.83345663997831, y=82.47157029824348)]), Blob(charge=5.241463033926113, wires=[(136, 138), (110, 111), (71, 75)], points=[Point(x=624.9752668698684, y=427.14556360556423), Point(x=640.3274801472991, y=431.31931873656487)]), Blob(charge=4.208319477076222, wires=[(131, 135), (160, 162), (125, 130)], points=[Point(x=348.07442850616644, y=559.1636459012446), Point(x=373.85269822519103, y=567.3346897979171)]), Blob(charge=5.333965066328843, wires=[(116, 118), (54, 56), (37, 37)], points=[Point(x=810.1658190815788, y=203.6702859033279), Point(x=814.233160795954, y=216.24453035143915)]), Blob(charge=5.475988684715355, wires=[(108, 114), (173, 175), (161, 165)], points=[Point(x=174.52867097725323, y=527.7379959165255), Point(x=193.57279642227633, y=547.4596105178639)])]

    # for point in blobs[0].points:
    #     print("\033[94m",cellTable.wireNumberFromPoint(planes[0], point), cellTable.wireNumberFromPoint(planes[1], point), cellTable.wireNumberFromPoint(planes[2], point),"\033[0m")


    event = cellTable.generateEvent(planes,blobs)
    event = cellTable.mergeEvent(event)
    # print("\033[94m","Event:",event,"\033[0m")

    # event = cellTable.mergeEvent(cellTable.fireWires(planes,[Point(500,500)]))



    if reco:
        cells = cellTable.generateCells(planes,event)
        # pprint(cells[0].wires)

        wireList, geomMatrix = cellTable.generateMatrix(planes,cells)

        chargeMatrix = cellTable.generateCharge(planes,blobs)
        charge = cellTable.measureCharge(wireList,chargeMatrix)

        trueCellCharge = cellTable.generateTrueCellMatrix(blobs,cells)
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

    # pprint(event)


########  ########     ###    ##      ## #### ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##  ##  ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##  ##  ####  ## ##
##     ## ########  ##     ## ##  ##  ##  ##  ## ## ## ##   ####
##     ## ##   ##   ######### ##  ##  ##  ##  ##  #### ##    ##
##     ## ##    ##  ##     ## ##  ##  ##  ##  ##   ### ##    ##
########  ##     ## ##     ##  ###  ###  #### ##    ##  ######


    drawnLines = makeEventLines(planes,event, useCenterLines)
    drawnLines =drawEventLines(drawnLines,volume)

    if reco:
        drawnCells = drawCells(cells, asMarker)

        if cellNumbering:
            if len(cells)>0:
                cellText = drawCellNumbers(cells)
                # cellText = drawCellPointNumbers(cells[0])
            else:
                cellText = []

    if trueBlobs:
        drawnBlobs = drawBlobs(blobs)



    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)
    # c1.Range(volume.width-25,0,volume.width,volume.height)
    # c1.Range(780,150,810,180)

    trueColor = root.kGreen

    for line in drawnLines:
        line.Draw()

    if reco:
        cellCount = 0
        for drawnCellNo, drawnCell in enumerate(drawnCells):
            if(math.isclose(trueCellCharge[drawnCellNo],0,rel_tol=1e-5)):
                recoColor = root.kRed
            else:
                recoColor = root.kBlue
                cellCount += 1
            for marker in drawnCell:
                if asMarker:
                    marker.SetMarkerColor(recoColor)
                    marker.Draw()
                else:
                    marker.SetLineWidth(4)
                    marker.SetLineColor(recoColor)
                    marker.Draw()
        print("Cells:",cellCount)
        if cellNumbering:
            for text in cellText:
                # text.SetTextSize(2)
                text.Draw()
    if trueBlobs:
        for marker in drawnBlobs:
            marker.SetLineWidth(2)
            marker.SetLineColor(trueColor)
            marker.Draw()

    # c1.Range(150,480,250,580)
    # print((root.gPad.GetEventX(),root.gPad.GetEventY()))
    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
