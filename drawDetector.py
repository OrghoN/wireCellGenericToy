from collections import namedtuple
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
        # print(wireNo)
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
            if useCenterLines:
                lines.extend(makeCenterLines(planes[planeNo],wire))
            else:
                lines.extend(cellTable.makeLines(planes[planeNo],wire))
    return lines

def drawEventLines(lines, volume):
    drawLines = []

    x0 = 0
    x1 = volume.width

    for lineNo, line in enumerate(lines):
        if(math.isclose(line[0].x, line[1].x, rel_tol=1e-5)):
            drawLines.append(root.TLine(line[0].x,0,line[0].x,volume.height))
        else:
            gradient = (line[1].y-line[0].y)/(line[1].x-line[0].x)
            y0 = gradient * x0 - gradient * line[0].x + line[0].y
            y1 = gradient * x1 - gradient * line[0].x + line[0].y
            drawLines.append(root.TLine(x0,y0,x1,y1))

    return drawLines

def drawBlobs(blobs):
    drawnBlobs = []

    for blob in blobs:
        if len(blob)>2:
            sortedPoints = sortPoints(blob.points)

            for i in range(1, len(sortedPoints)):
                drawnBlobs.append(root.TLine(sortedPoints[i-1].x,sortedPoints[i-1].y,sortedPoints[i].x,sortedPoints[i].y))

            drawnBlobs.append(root.TLine(sortedPoints[-1].x,sortedPoints[-1].y,sortedPoints[0].x,sortedPoints[0].y))
        else:
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

def sortPoints(points):
    sortedPoints = []
    hull = ConvexHull(points)

    for pointNo in reversed(hull.vertices):
        sortedPoints.append(points[pointNo])
        # sortedPoints.append(hull.points[pointNo])

    return sortedPoints

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

    blobs = cellTable.generateBlobs(planes,volume)
    # print(blobs)

    event = cellTable.generateEvent(planes,blobs)
    event = cellTable.mergeEvent(event)

    # event = cellTable.mergeEvent(cellTable.fireWires(planes,[Point(500,500)]))



    if reco:
        cells = cellTable.generateCells(planes,event)

        wireList, geomMatrix = cellTable.generateMatrix(planes,cells)

        chargeMatrix = cellTable.generateCharge(planes,blobs)
        charge = cellTable.measureCharge(wireList,chargeMatrix)

        trueCellCharge = cellTable.generateTrueCellMatrix(blobs,cells)
        trueWireCharge = geomMatrix * trueCellCharge


    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")
    print("\033[93m","Number of Merged Wires:", np.shape(geomMatrix)[0],"\033[0m")
    print("\033[93m","Number of Cells:", np.shape(geomMatrix)[1],"\033[0m")


    # pprint(event)


########  ########     ###    ##      ## #### ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##  ##  ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##  ##  ####  ## ##
##     ## ########  ##     ## ##  ##  ##  ##  ## ## ## ##   ####
##     ## ##   ##   ######### ##  ##  ##  ##  ##  #### ##    ##
##     ## ##    ##  ##     ## ##  ##  ##  ##  ##   ### ##    ##
########  ##     ## ##     ##  ###  ###  #### ##    ##  ######


    drawnLines = makeEventLines(planes,event, True)
    drawnLines =drawEventLines(drawnLines,volume)

    if reco:
        drawnCells = drawCells(cells, asMarker)

    if trueBlobs:
        drawnBlobs = drawBlobs(blobs)



    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

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
    if trueBlobs:
        for marker in drawnBlobs:
            marker.SetLineWidth(2)
            marker.SetLineColor(trueColor)
            marker.Draw()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
