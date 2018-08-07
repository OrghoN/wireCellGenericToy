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

def drawTracks(tracks):
    drawnTracks = []

    for track in tracks:
        if len(track)>2:
            sortedPoints = sortPoints(track)

            for i in range(1, len(sortedPoints)):
                drawnTracks.append(root.TLine(sortedPoints[i-1].x,sortedPoints[i-1].y,sortedPoints[i].x,sortedPoints[i].y))

            drawnTracks.append(root.TLine(sortedPoints[-1].x,sortedPoints[-1].y,sortedPoints[0].x,sortedPoints[0].y))
        else:
            drawnTracks.append(root.TLine(track[-1].x,track[-1].y,track[0].x,track[0].y))

    return drawnTracks

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

    reco = True
    trueTracks = True

    tracks = cellTable.generateTracks(planes,volume)
    # print(tracks)
    # tracks = [[Point(x=863.8123073383628, y=237.20168408402608), Point(x=879.4898046480805, y=254.62154700104645)], [Point(x=897.9838145021016, y=439.5699574322691), Point(x=902.347089347595, y=468.8372505491941)], [Point(x=459.63144104619903, y=382.5122915123376), Point(x=478.56034194461296, y=394.98763986555116)], [Point(x=369.41224394065944, y=55.55274812296673), Point(x=397.7209383565665, y=56.24356916499068)], [Point(x=578.1128823395261, y=273.8996549910089), Point(x=583.7715820489404, y=292.4068956477323)], [Point(x=941.9828398931954, y=178.23820741638875), Point(x=943.528575834209, y=199.43152310955702)], [Point(x=645.308777546017, y=993.1588096256064), Point(x=661.7143776363092, y=1000.0)], [Point(x=949.9509075031596, y=299.7882799523782), Point(x=954.9046204270968, y=328.3046326103498)], [Point(x=578.310633419964, y=592.0264442273417), Point(x=608.2096218066717, y=597.7219708757535)], [Point(x=72.10782804142946, y=907.6779840572092), Point(x=79.71799075810334, y=914.5026522713857)], [Point(x=79.34759023948767, y=316.7756627053493), Point(x=84.81605650767631, y=339.67444310978664)], [Point(x=857.1478822876211, y=719.2239721372098), Point(x=870.3523257618657, y=741.9981552299636)], [Point(x=436.0112182472958, y=208.39444975904973), Point(x=461.3275953650955, y=212.67620037911408)], [Point(x=835.5899544130887, y=16.421382970551512), Point(x=857.4268345198027, y=45.11805871199907)]]

    event = cellTable.generateEvent(planes,tracks)
    event = cellTable.mergeEvent(event)

    # event = cellTable.mergeEvent(cellTable.fireWires(planes,[Point(500,500)]))

    if reco:
        cells = cellTable.generateCells(planes,event)

    # wireList, matrix = cellTable.generateMatrix(planes,cells)

    # pprint(event)


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

    if trueTracks:
        drawnTracks = drawTracks(tracks)



    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

    recoColor = root.kRed
    trueColor = root.kGreen

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

    if trueTracks:
        print(len(drawnTracks))
        for marker in drawnTracks:
            marker.SetLineWidth(6)
            # marker.SetLineStyle(2)
            marker.SetLineColor(trueColor)
            marker.Draw()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
