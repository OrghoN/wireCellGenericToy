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

def makeEventLines(planes, event):
    lines = []

    for planeNo, plane in enumerate(event):
        for wire in plane:
            lines.extend(makeCenterLines(planes[planeNo],wire))
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
################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    planes = cellTable.generatePlaneInfo(wirePitches, volume)

    event = cellTable.generateEvent(planes,volume)
    event = cellTable.mergeEvent(event)
    eventLines = makeEventLines(planes,event)

    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, 700 )
    c1.Range(0,0,volume.width,volume.height)

    eventLines = drawEventLines(eventLines,volume)
    for line in eventLines:
        line.Draw()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
