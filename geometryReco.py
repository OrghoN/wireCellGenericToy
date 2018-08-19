#External Dependencies
from scipy.spatial import ConvexHull
import itertools

#Internal Dependencies
from dataTypes import *
import geometryGen
import utilities

def makeLines(plane, wire):
    """Create lines based on a merged wire

    Parameters
    ----------
    plane : PlaneInfo
        Plane information for the plane the wire number is for
    wire : tuple[2] of int
        A merged wire

    Returns
    -------
    list of lines
        List of lines that the boundaries of the wire correspond to

    """
    dist0 = plane.pitch * wire[0]
    dist1 = plane.pitch * (wire[1] + 1)

    if plane.originTranslation > 0:
        point0 = Point(plane.originTranslation -
                       (dist0 * (-plane.cos)), dist0 * plane.sin)
        point1 = Point(plane.originTranslation -
                       (dist1 * (-plane.cos)), dist1 * plane.sin)
    else:
        point0 = Point(dist0 * plane.cos, dist0 * plane.sin)
        point1 = Point(dist1 * plane.cos, dist1 * plane.sin)

    if plane.gradient == "INF":
        line0 = Line(point0, Point(point0.x, point0.y + 1))
        line1 = Line(point1, Point(point1.x, point1.y + 1))
    else:
        line0 = Line(point0, Point(point0.x + 1, point0.y + plane.gradient))
        line1 = Line(point1, Point(point1.x + 1, point1.y + plane.gradient))

    return [line0, line1]

def lineIntersection(line0, line1):
    """Gives points of intersection between 2 lines
        Note: Doesn't account for parallel lines

    Parameters
    ----------
    line0 : Line
        First Line
    line1 : Line
        Second Line

    Returns
    -------
    Point
        Intersection Point

    """
    #Doesnt account for parallel line case
    px = ((line0.point0.x * line0.point1.y - line0.point0.y * line0.point1.x) * (line1.point0.x - line1.point1.x) - (line0.point0.x - line0.point1.x) * (line1.point0.x * line1.point1.y -
                                                                                                                                 line1.point0.y * line1.point1.x)) / ((line0.point0.x - line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x - line1.point1.x))
    py = ((line0.point0.x * line0.point1.y - line0.point0.y * line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x * line1.point1.y -
                                                                                                                                 line1.point0.y * line1.point1.x)) / ((line0.point0.x - line0.point1.x) * (line1.point0.y - line1.point1.y) - (line0.point0.y - line0.point1.y) * (line1.point0.x - line1.point1.x))
    return Point(px, py)

def wireIntersection(plane0, wire0, plane1, wire1):
    """Intersection points between two merged wires in different planes

    Parameters
    ----------
    plane0 : PlaneInfo
        Plane information for the plane the wire 0 is for
    wire : tuple[2] of int
        A merged wire (wire0)
    plane1 : PlaneInfo
        Plane information for the plane the wire 1 is for
    wire : tuple[2] of int
        A merged wire (wire1)

    Returns
    -------
    list of Point
        Intersection Points Between merged wires

    """
    points = []
    Lines0 = makeLines(plane0, wire0)
    Lines1 = makeLines(plane1, wire1)

    points.append(lineIntersection(Lines0[0],Lines1[0]))
    points.append(lineIntersection(Lines0[1],Lines1[0]))
    points.append(lineIntersection(Lines0[0],Lines1[1]))
    points.append(lineIntersection(Lines0[1],Lines1[1]))

    return points

def sortPoints(points):
    """Create convex hull and sort the points of convex hull in counterClockwise order

    Parameters
    ----------
    points : list of Point
        Input point cloud to make convex hull

    Returns
    -------
    list of Point
        List of points that form convex hull

    """
    sortedPoints = []
    hull = ConvexHull(points)

    for pointNo in (hull.vertices):
        sortedPoints.append(points[pointNo])

    return sortedPoints

def checkCell(planes, wires):
    """Check if the wires given form a cell

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    wires : list of tuple[2] of int
        A list of wires for each plane

    Returns
    -------
    Cell
        Cell(False, False) if it doesn't form a cell else the generated cell

    """
    points = []

    #generate points for interections between wires from every plane
    for plane0 in range(0,len(wires)):
        for plane1 in  range(plane0+1,len(wires)):
            potentialPoints = wireIntersection(planes[plane0], wires[plane0], planes[plane1], wires[plane1])

            #check if point is in cell
            for point in potentialPoints:
                isPointInside = True
                for planeNo, plane in enumerate(planes):
                    wire = utilities.wireNumberFromPoint(plane, point)
                    #improves performance by not checking in the planes used to make the point
                    if planeNo == plane0 or planeNo == plane1:
                        continue
                    else:
                        if not utilities.pointInWire(plane,point,wires[planeNo]):
                            isPointInside = False

                if isPointInside:
                    points.append(point)

    #if less than or equal to 2 points, cell isn't real
    if len(points) <=2:
        return Cell(False, False)
    else:
        points = sortPoints(points)
        potentialWires = list(itertools.chain(*geometryGen.mergeEvent(utilities.fireWires(planes,points))))
        potentialWires = list(map(lambda x: (max((x[0][0],x[1][0])),min((x[0][1],x[1][1]))),zip(wires,potentialWires)))
        return Cell(potentialWires,points)

def reconstructCells(planes,event):
    """Reconstruct cells from a merged event

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    event : list of list of tuple[2] of int
        List of merged wires in an event

    Returns
    -------
    list of Cell
        List of cells Reconstructed from Geometric information

    """
    cells = []
    #cartesian product of all merged wires
    potentialCells = list(itertools.product(*event))

    #check if each potential combination is valid
    for potentialCell in potentialCells:
        cell = checkCell(planes, potentialCell)
        if cell[0] == False:
            continue
        else:
            cells.append(cell)

    return cells
