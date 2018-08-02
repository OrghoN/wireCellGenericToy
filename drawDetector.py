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

        if plane.translationFactor > 0:
            point = Point(plane.translationFactor -
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

def drawCells(cells):
    drawnCells =[]

    for cell in cells:
        drawnCells.extend(list(map(lambda p: root.TMarker(p.x,p.y,21), cell.points)))

    return drawnCells

def sortPoints(points):
    sortedPoints = []
    hull = ConvexHull(points)

    for pointNo in reversed(hull.vertices):
        # sortedPoints.append(points[pointNo])
        sortedPoints.append(hull.points[pointNo])

    return sortedPoints

################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    planes = cellTable.generatePlaneInfo(wirePitches, volume)

    event = cellTable.generateEvent(planes,volume)
    event = cellTable.mergeEvent(event)
    pprint(event)

    cells = cellTable.generateCells(planes,event)

    drawnLines = makeEventLines(planes,event, True)
    drawnLines =drawEventLines(drawnLines,volume)

    drawnCells = drawCells(cells)

    # sorted = sortPoints(recoPoints)
    # sortedx = np.array(list(map(lambda p: p[0], sorted)))
    # sortedy = np.array(list(map(lambda p: p[1], sorted)))
    #
    # Cx = (ctypes.c_double * len(sorted))(*sortedx)
    # Cy = (ctypes.c_double * len(sorted))(*sortedy)
    #
    # cell = root.TGeoPolygon(len(sorted))
    # cell.SetXY(Cx, Cy)
    # cell.FinishPolygon()
    # pprint(cell.Area())

    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

    recoColor = root.kRed

    for line in drawnLines:
        line.Draw()

    for marker in drawnCells:
        marker.SetMarkerColor(recoColor)
        marker.Draw()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
