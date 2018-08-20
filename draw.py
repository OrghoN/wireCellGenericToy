# External Dependencies
import ROOT as root
import math
import numpy as np
import os

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


def drawEventLines(lines, volume, centerColor=root.kBlue, centerStyle=2,edgeColor=root.kBlack,edgeStyle=1):
    """Create the TLines that will be drawn

    Parameters
    ----------
    lines : list of Line
        List of lines in event
    volume : DetectorVolume
        Volume of Detector
    centerColor : TColor
        Color of Center Wires
    centerStyle : TStyle
        Style of Center Wires
    edgeColor : TColor
        Color of Edge Wirees
    edgeStyle : TStyle
        Style of edge Wires

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

        if line[1]:
            drawLine.SetLineColor(centerColor)
            drawLine.SetLineStyle(centerStyle)
        else:
            drawLine.SetLineColor(edgeColor)
            drawLine.SetLineStyle(edgeStyle)

        drawLine.Draw()

        drawLines.append((drawLine,line[1]))

    return drawLines


def drawBlobs(blobs, color = root.kGreen, width = 4):
    """Draw True Blobs

    Parameters
    ----------
    blobs : list of Blob
        List of True Blobs
    color : TColor
        Color of Blobs
    width : int
        Width of lines that draw Blobs

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

    for line in drawnBlobs:
        line.SetLineWidth(width)
        line.SetLineColor(color)
        line.Draw()

    return drawnBlobs


def drawCells(cells, asMarker, trueColor = root.kGreen, recoColor = root.kRed, width = 4, trueCells=[], drawFake=True):
    """Draw the Cells

    Parameters
    ----------
    cells : list of Cell
        List of reconstructed cells
    asMarker : boolen
        If true draw markers denoting vertices else draw polygon
    trueColor : TColor
        Color of True Cells
    recoColor : TColor
        Color of Cells
    width : int
        Width of lines that draw Cells
    trueCells : list of Boolean
        Truth information for the cells
    drawFake : Boolean
        True if draw fake cells false otherwise

    Returns
    -------
    list of list of TLine or TMarker
        Drawn Cells

    """
    drawnCells = []

    if trueCells == []:
        trueCells = [False] * len(cells)

    if asMarker:
        for cellNo, cell in enumerate(cells):
            drawnCell = list(map(lambda p: root.TMarker(p.x, p.y, 21), cell.points))

            for marker in drawnCell:
                if trueCells[cellNo]:
                    marker.SetMarkerColor(trueColor)
                else:
                    marker.SetMarkerColor(recoColor)
                marker.Draw()

            drawnCells.append(drawnCell)
    else:
        for cellNo, cell in enumerate(cells):
            drawnCell = []

            for i in range(1, len(cell.points)):
                drawnCell.append(root.TLine(
                    cell.points[i - 1].x, cell.points[i - 1].y, cell.points[i].x, cell.points[i].y))

            drawnCell.append(root.TLine(
                cell.points[-1].x, cell.points[-1].y, cell.points[0].x, cell.points[0].y))

            for line in drawnCell:
                line.SetLineWidth(width)
                if drawFake:
                    if trueCells[cellNo]:
                        line.SetLineColor(trueColor)
                    else:
                        line.SetLineColor(recoColor)
                    line.Draw()
                else:
                    if trueCells[cellNo]:
                        line.SetLineColor(trueColor)
                        line.Draw()

            drawnCells.append(drawnCell)
    return drawnCells

def drawCellNumbers(cells, color = root.kBlack, trueCells=[], drawFake=True):
    """Draw Numbering for the cells

    Parameters
    ----------
    cells : list of Cell
        List of reconstructed cells
    color : TColor
        Color of text
    trueCells : list of Boolean
        Truth information for the cells
    drawFake : Boolean
        True if draw fake cells false otherwise

    Returns
    -------
    list of TText
        The number associated with each cell

    """
    numbers = []

    if trueCells == []:
        trueCells = [False] * len(cells)

    counter = 0

    for cellNo, cell in enumerate(cells):
        center = np.mean(cell.points,axis=0)
        number = root.TText(center[0],center[1],str(counter))

        number.SetTextColor(color)
        if drawFake:
            counter += 1
            number.Draw()
            numbers.append(number)
        else:
            if trueCells[cellNo]:
                counter += 1
                number.Draw()
                numbers.append(number)




    return numbers

def drawCellPointNumbers(cell, color = root.kBlack):
    """Draw Numbering for the points in a cell

    Parameters
    ----------
    cell : Cell
        Cell in question
    color : TColor
        Color of text

    Returns
    -------
    list of TText
        The number associated with each point in cell

    """
    numbers = []
    if cell[0] != False:
        for pointNo, point in enumerate(cell.points):
            number = root.TText(point.x,point.y,str(pointNo))

            number.SetTextColor(color)
            number.Draw()

            numbers.append(number)

    return numbers

def zoomCell(cell,side,volume):
    """Zoom in on a particular cell

    Parameters
    ----------
    cell : Cell
        The cell in question
    side : int
        Width of the zoom window in mm
    volume : DetectorVolume
        Volume of detector

    Returns
    -------
    tuple[2] of point
        (Bottom Left Point, Top Right Point)

    """
    width = side
    height = int(side * (volume.height/volume.width))

    center = Point(*np.mean(cell.points,axis=0))

    x1 = int(center.x-width/2)
    y1 = int(center.y-height/2)

    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0

    x2 = x1 + width
    y2 = y1 + height

    if x2 > volume.width:
        x2 = volume.width
        x1 = x2 - width
    if y2 > volume.height:
        y2 = volume.height
        y1 = y2 - height

    #get canvas
    c1 = root.gPad.GetCanvas()

    c1.Range(x1,y1,x2,y2)

    return (Point(x1,y1),Point(x2,y2))

def saveImage(fileName,directory=""):
    #check if directories exist make if not
    if len(directory)>0 and not (os.path.isdir(directory)):
        os.mkdir(directory)
    if not (os.path.isdir(directory+"/png")):
        os.mkdir(directory+"/png")
    if not (os.path.isdir(directory+"/pdf")):
        os.mkdir(directory+"/pdf")

    #get canvas
    c1 = root.gPad.GetCanvas()

    #save file and convert png to transparent background
    c1.SaveAs(directory + "/png/" + fileName+".png")
    c1.SaveAs(directory + "/pdf/" + fileName+".pdf")
    #Convert image to have transparent background requires imagemagick
    os.system("convert " + directory + "/png/" + fileName + ".png -fuzz 20% -transparent white " + directory + "/png/" + fileName+".png")

    return True

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
