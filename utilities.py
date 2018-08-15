#External Dependencies
import math

#internal Dependencies
from dataTypes import *

def rotate(point, angle):
    # counterClockwise turn of axis
    return Point(point.x * math.cos(angle) + point.y * (math.sin(angle)), point.x * (-math.sin(angle)) + point.y * math.cos(angle))


def generatePlaneInfo(wirePitches, volume, angles, wireTranslations):
    """Generates information about planes based on wire pitches and volume assuming equal angle between each plane and the next

    Parameters
    ----------
    wirePitches : int or tuple of int or float
        A list of wire pitches, each number corresponding to the pitch of each plane
    volume : DetectorVolume
        The width and height of the detector

    Returns
    -------
    list of PlaneInfo
        List of information regarding the planes.

    """
    planes = []

    translationPoint = Point(volume.width, 0)

    for planeNo, pitch in enumerate(wirePitches):
        # basic angle calculations
        angle = angles[planeNo]
        cos = math.cos(angle)
        sin = math.sin(angle)

        # Origin and number of wire calculations
        if (rotate(translationPoint, angle).x < 0):
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
                                originTranslation, wireTranslations[planeNo], sin, cos, gradient))

    return planes
