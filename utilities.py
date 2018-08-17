#External Dependencies
import math

#internal Dependencies
from dataTypes import *

def generatePlaneInfo(wirePitches, volume, angles):
    """Generates information about planes based on wire pitches and volume assuming equal angle between each plane and the next

    Parameters
    ----------
    wirePitches : list or tuple of int or float
        A list of wire pitches, each number corresponding to the pitch of each plane
    volume : DetectorVolume
        The width and height of the detector
    angles : list or tuple of float
        List of the angles of the wire plane in radians

    Returns
    -------
    list of PlaneInfo
        List of information regarding the planes.

    """

    #TODO Add functionality for translating wires by a certain amount

    planes = []

    for planeNo, pitch in enumerate(wirePitches):
        # basic angle calculations
        angle = angles[planeNo]
        cos = math.cos(angle)
        sin = math.sin(angle)

        # Origin and number of wire calculations
        if (volume.width * math.cos(angle) < 0):
            originTranslation = volume.width
            noOfWires = math.floor(
                (sin * volume.height - cos * originTranslation) / pitch)
        else:
            originTranslation = 0
            noOfWires = math.floor(
                (cos * volume.width + sin * volume.height) / pitch)

        # gradient calculations
        if(math.isclose(angle, math.pi, rel_tol=1e-5)):
            gradient = "INF"
        elif originTranslation == 0:
            gradient = math.tan(angle + math.pi / 2)
        else:
            gradient = math.tan(angle - math.pi / 2)

        planes.append(PlaneInfo(angle, pitch, noOfWires,
                                originTranslation, sin, cos, gradient))

    return planes

def wireNumberFromPoint(plane, point):
    """Generates the wire number for a point given a certain plane

    Parameters
    ----------
    plane : PlaneInfo
        Plane information for the plane the wire number is for
    point : Point
        The point being queried

    Returns
    -------
    int
        Primitive Wire number

    """
    return math.floor((plane.cos * point.x + plane.sin * point.y - plane.cos * plane.originTranslation) / plane.pitch)

def pointInWire(plane,point,wire):
    """Check if a point is inside a certain merged wire

    Parameters
    ----------
    plane : PlaneInfo
        Plane information for the plane the wire number is for
    point : Point
        The point being queried
    wire : tuple[2] of int
        A merged wire

    Returns
    -------
    Boolean
        True if point is in wire, False if not

    """
    wireNo = (plane.cos * point.x + plane.sin * point.y - plane.cos * plane.originTranslation) / plane.pitch

    # The first two check for boundary points while the last accounts for a point being inside the wire
    if(math.isclose(wireNo,wire[0]-1,rel_tol=1e-5) or math.isclose(wireNo,wire[1]+1,rel_tol=1e-5) or (math.floor(wireNo) >= wire[0] and math.floor(wireNo) <= wire[1])):
        return True

    return False

def fireWires(planes, points):
    """Show which wires have been hit for a given blob

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    points : list of points
        points defining ConvexHull of blob

    Returns
    -------
    2d list of int
        A list that has lists of merged wire numbers. one list for every plane

    """
    firedWires = []
    for planeNo, plane in enumerate(planes):
        for pointNo, point in enumerate(points):
            wireNo = wireNumberFromPoint(plane, point)

            if pointNo == 0:
                min = wireNo
                max = wireNo
            elif wireNo > max:
                max = wireNo
            elif wireNo < min:
                min = wireNo

        firedWires.append(list(range(min, max + 1)))

    return firedWires
