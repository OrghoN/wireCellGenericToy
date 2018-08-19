#External Dependencies
import sys
import math

#Internal Dependencies
from dataTypes import *
import utilities
import geometryGen
import geometryReco

def generateAngles(noOfPlanes):
    individualAngle = math.pi/noOfPlanes
    angles = []

    for planeNo in range(noOfPlanes):
        angles.append(individualAngle * (planeNo + 1))

    return angles


def main(argv):
    #Defining Detector Geometry
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    wireTranslations = [0.0,0.0,0.0]
    angles = generateAngles(len(wirePitches))

    planes = utilities.generatePlaneInfo(wirePitches, volume, angles)

    #Generating Random Blobs
    blobs = geometryGen.generateBlobs(planes,volume)

    #Creating Event
    event = geometryGen.generateEvent(planes,blobs)
    #Merging Event
    event = geometryGen.mergeEvent(event)

    #reconstructing cells based on geometry information
    cells = geometryReco.reconstructCells(planes,event)

    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")
    print("\033[93m","Number of Cells:", len(cells),"\033[0m")

if __name__ == "__main__":
    main(sys.argv)
