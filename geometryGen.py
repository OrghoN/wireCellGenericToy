#External Dependencies
import numpy as np
import itertools
import math

#Internal Dependencies
from dataTypes import *
import utilities

def createMergedWires(firedWirePrimitives):
    """Merged wires from a list of fired wire primitives

    Parameters
    ----------
    firedWirePrimitives : list of int
        List of primitive wire numberss

    Returns
    -------
    tuple[2] of int
        Merged Wire

    """
    firedWirePrimitives = sorted(set(firedWirePrimitives))
    gaps = [[s, e] for s, e in zip(
        firedWirePrimitives, firedWirePrimitives[1:]) if s + 1 < e]
    edges = iter(firedWirePrimitives[:1] +
                 sum(gaps, []) + firedWirePrimitives[-1:])
    return list(zip(edges, edges))

def mergeEvent(event):
    """Create Merged wires from list of wire primitives

    Parameters
    ----------
    event : list of list of ints
        List of wire primitives that defines a primitive event

    Returns
    -------
    list of list of tuple[2] of ints
        Merged Event

    """
    mergedEvent = []
    for plane in event:
        mergedEvent.append(createMergedWires(plane))

    return mergedEvent

def generateBlobs(planes,volume, numberOfBlobs):
    """Generate random true blobs

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    volume : DetectorVolume
        The width and height of the detector

    Returns
    -------
    list of Blob
        A list of all the blobs in the event

    """
    blobs = []

    #Arbitrary number of blobs from 2 to 15
    for i in range(0,numberOfBlobs):
        point0 = Point(np.random.random_sample() * volume.width,
                       np.random.random_sample() * volume.height)

        #30 set as arbitrary max length of blob
        xOffset = point0.x + np.random.random_sample() * 30
        yOffset = point0.y + np.random.random_sample() * 30

        if xOffset > volume.width:
            xOffset = volume.width
        if yOffset > volume.height:
            yOffset = volume.height

        point1 = Point(xOffset, yOffset)


        #charge calculations
        meanCharge = math.sqrt((point1.x-point0.x)*(point1.x-point0.x)+(point1.y-point0.y)*(point1.y-point0.y))
        sigmaCharge = math.sqrt(meanCharge)
        # meanCharge, sigmaCharge = 5, 0.5
        charge = np.random.normal(meanCharge, sigmaCharge)

        blobs.append(Blob(charge, list(itertools.chain(*mergeEvent(utilities.fireWires(planes,[point0,point1])))), [point0,point1]))

    return blobs

def generateEvent(planes, blobs):
    """Generate List of wire primitives that were fired based on true blobs

    Parameters
    ----------
    planes : list of PlaneInfo
        A list containing information for all the planes in the detector
    blobs : list of Blob
        A list containing true blobs in event

    Returns
    -------
    list of list of ints
        Primitive fired wires from every plane

    """
    event = []
    for blobNo, blob in enumerate(blobs):
        wires = utilities.fireWires(planes, blob.points)

        if blobNo == 0:
            event = wires
        event = [set(item[0]).union(item[1])
                 for item in list(zip(event, wires))]
    return event
