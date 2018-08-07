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
import cellTable

import ROOT as root
from scipy.spatial import ConvexHull
import ctypes

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

def drawCells(cells, asMarker):
    drawnCells =[]

    if asMarker:
        for cell in cells:
            sortedPoints = sortPoints(cell.points)
            drawnCells.extend(list(map(lambda p: root.TMarker(p.x,p.y,21), sortedPoints)))
    else:
        for cell in cells:
            sortedPoints = sortPoints(cell.points)

            for i in range(1, len(sortedPoints)):
                drawnCells.append(root.TLine(sortedPoints[i-1].x,sortedPoints[i-1].y,sortedPoints[i].x,sortedPoints[i].y))

            drawnCells.append(root.TLine(sortedPoints[-1].x,sortedPoints[-1].y,sortedPoints[0].x,sortedPoints[0].y))

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

    reco = False

    tracks = cellTable.generateTracks(planes,volume)
    event = cellTable.generateEvent(planes,tracks)
    event = cellTable.mergeEvent(event)

    cells = generateCells(planes,event)

    # event = cellTable.mergeEvent(cellTable.fireWires(planes,[Point(500,500)]))

    if reco:
        cells = cellTable.generateCells(planes,event)

    # wireList, matrix = cellTable.generateMatrix(planes,cells)

    pprint(event)


    # for row in matrix:
    #     print(row)



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
        asMarker = False
        drawnCells = drawCells(cells, asMarker)



    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

    recoColor = root.kRed

    for line in drawnLines:
        line.Draw()

    if reco:
        for marker in drawnCells:
            if asMarker:
                marker.SetMarkerColor(recoColor)
            else:
                marker.SetLineWidth(4)
                # marker.SetLineStyle(2)
                marker.SetLineColor(recoColor)
            marker.Draw()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
