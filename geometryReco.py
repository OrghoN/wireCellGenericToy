#Internal Dependencies
from dataTypes import *

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
