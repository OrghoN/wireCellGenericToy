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

def makeCenterLines(plane, wires):
    lines = []

    for wireNo in range(wires[0], wires[1]+1):
        # print(wireNo)
        dist = plane.pitch * wires[0] + plane.pitch/2

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

################################################################################

def main(argv):
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    planes = cellTable.generatePlaneInfo(wirePitches, volume)

    event = cellTable.generateEvent(planes,volume)
    event = cellTable.mergeEvent(event)

    # lines = makeCenterLines(planes[2], (5,10))
    # pprint(lines)

    pprint(event)
    pprint(makeEventLines(planes, event))


if __name__ == "__main__":
    main(sys.argv)
