# External Dependencies
import ROOT as root
import math
import numpy as np

# Internal Dependencies
from dataTypes import *
import utilities
import geometryReco


def makeCenterLines(plane, wire):
    """Make Lines corresponding to the center of every primitive wire in merged wire

    Parameters
    ----------
    plane : PlaneInfo
        Plane information for the plane the wire is on
    wire : tuple[2] of int
        A merged wire

    Returns
    -------
    list of Line
        List of lines that represent the merged wire

    """
    lines = []

    for wireNo in range(wire[0], wire[1] + 1):
        dist = plane.pitch * wireNo + plane.pitch / 2

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
    """Create all lines in an event

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    event : list of list of tuple[2] of ints
        An event with all merged wires
    useCenterLines : boolean or str
        Make center lines if True, edges if False and both if "both"

    Returns
    -------
    list of lines
        List of lines in event

    """
    lines = []

    for planeNo, plane in enumerate(event):
        for wire in plane:
            if (useCenterLines == "both"):
                centerLines = makeCenterLines(planes[planeNo], wire)
                centerLines = list(map(lambda line: (line, True), centerLines))
                lines.extend(centerLines)
                borderLines = geometryReco.makeLines(planes[planeNo], wire)
                borderLines = list(
                    map(lambda line: (line, False), borderLines))
                lines.extend(borderLines)
            elif useCenterLines:
                centerLines = makeCenterLines(planes[planeNo], wire)
                centerLines = list(map(lambda line: (line, True), centerLines))
                lines.extend(centerLines)
            else:
                borderLines = geometryReco.makeLines(planes[planeNo], wire)
                borderLines = list(
                    map(lambda line: (line, False), borderLines))
                lines.extend(borderLines)
    return lines


def drawEventLines(lines, volume):
    """Create the TLines that will be drawn

    Parameters
    ----------
    lines : list of Line
        List of lines in event
    volume : DetectorVolume
        Volume of Detector

    Returns
    -------
    list of tuple[2] (TLine,boolean)
        The actual Tlines to be drawn and whether they're center line

    """
    drawLines = []

    x0 = 0
    x1 = volume.width

    for lineNo, line in enumerate(lines):
        if(math.isclose(line[0][0].x, line[0][1].x, rel_tol=1e-5)):
            drawLine = root.TLine(line[0][0].x, 0, line[0][0].x, volume.height)
        else:
            gradient = (line[0][1].y - line[0][0].y) / \
                (line[0][1].x - line[0][0].x)
            y0 = gradient * x0 - gradient * line[0][0].x + line[0][0].y
            y1 = gradient * x1 - gradient * line[0][0].x + line[0][0].y
            drawLine = root.TLine(x0, y0, x1, y1)

        drawLines.append((drawLine,line[1]))

    return drawLines


def drawBlobs(blobs):
    """Draw True Blobs

    Parameters
    ----------
    blobs : list of Blob
        List of True Blobs

    Returns
    -------
    list of TLine
        list of lines to be drawn that represent blobs

    """
    drawnBlobs = []

    for blob in blobs:
        for i in range(1, len(blob.points)):
            drawnBlobs.append(root.TLine(
                blob.points[i - 1].x, blob.points[i - 1].y, blob.points[i].x, blob.points[i].y))

        drawnBlobs.append(root.TLine(
            blob.points[-1].x, blob.points[-1].y, blob.points[0].x, blob.points[0].y))

    return drawnBlobs


def drawCells(cells, asMarker):
    """Draw the Cells

    Parameters
    ----------
    cells : list of Cell
        List of reconstructed cells
    asMarker : boolen
        If true draw markers denoting vertices else draw polygon

    Returns
    -------
    list of list of TLine or TMarker
        Description of returned object.

    """
    drawnCells = []

    if asMarker:
        for cell in cells:
            drawnCells.append(
                list(map(lambda p: root.TMarker(p.x, p.y, 21), cell.points)))
    else:
        for cell in cells:
            drawnCell = []

            for i in range(1, len(cell.points)):
                drawnCell.append(root.TLine(
                    cell.points[i - 1].x, cell.points[i - 1].y, cell.points[i].x, cell.points[i].y))

            drawnCell.append(root.TLine(
                cell.points[-1].x, cell.points[-1].y, cell.points[0].x, cell.points[0].y))

            drawnCells.append(drawnCell)
    return drawnCells

def drawCellNumbers(cells):
    """Draw Numbering for the cells

    Parameters
    ----------
    cells : list of Cell
        List of reconstructed cells

    Returns
    -------
    list of TText
        The number associated with each cell

    """
    numbers = []

    for cellNo, cell in enumerate(cells):
        center = np.mean(cell.points,axis=0)
        numbers.append(root.TText(center[0],center[1],str(cellNo)))


    return numbers

def drawCellPointNumbers(cell):
    """Draw Numbering for the points in a cell

    Parameters
    ----------
    cell : Cell
        Cell in question

    Returns
    -------
    list of TText
        The number associated with each point in cell

    """
    numbers = []
    if cell[0] != False:
        for pointNo, point in enumerate(cell.points):
            numbers.append(root.TText(point.x,point.y,str(pointNo)))

    return numbers

def zoom():
    mouseLocation = Point(root.gPad.GetEventX(),root.gPad.GetEventY())

    #get canvas
    c1 = root.gPad.GetCanvas()

    #get canvas range
    x0 = root.Double()
    y0 = root.Double()
    x1 = root.Double()
    y1 = root.Double()
    c1.GetRange(x0,y0,x1,y1)

    root.gPad.HandleInput()
    ev = root.gPad.GetEvent()
    # print(ev)
    # if ev == 11:
    #     continue
    # elif ev == 12:
    #     continue
