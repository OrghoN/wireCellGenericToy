#External Dependencies
import sys
import ROOT as root
import math

#Internal Dependencies
from dataTypes import *
import utilities
import geometryGen
import geometryReco
import draw
import matrixGeneration

def generateAngles(noOfPlanes):
    individualAngle = math.pi/noOfPlanes
    angles = []

    for planeNo in range(noOfPlanes):
        angles.append(individualAngle * (planeNo + 1))

    return angles


def main(argv):

########  ########     ###    ##      ##     #######  ########  ######## ####  #######  ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##    ##     ## ##     ##    ##     ##  ##     ## ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##    ##     ## ##     ##    ##     ##  ##     ## ####  ## ##
##     ## ########  ##     ## ##  ##  ##    ##     ## ########     ##     ##  ##     ## ## ## ##  ######
##     ## ##   ##   ######### ##  ##  ##    ##     ## ##           ##     ##  ##     ## ##  ####       ##
##     ## ##    ##  ##     ## ##  ##  ##    ##     ## ##           ##     ##  ##     ## ##   ### ##    ##
########  ##     ## ##     ##  ###  ###      #######  ##           ##    ####  #######  ##    ##  ######

    #Set boolean options
    reco = True
    trueBlobs = True
    asMarker = False
    cellNumbering = True
    blobNumbering = False
    useCenterLines = "both"

    #Set Colors
    trueColor = root.kGreen
    blobWidth = 4

    recoColor = root.kRed
    detectionColor = root.kBlue
    cellWidth = 4

    centerColor = root.kBlue
    centerStyle = 2

    edgeColor = root.kBlack
    edgeStyle = 1


 ######   ########  #######  ##     ## ######## ######## ########  ##    ##
##    ##  ##       ##     ## ###   ### ##          ##    ##     ##  ##  ##
##        ##       ##     ## #### #### ##          ##    ##     ##   ####
##   #### ######   ##     ## ## ### ## ######      ##    ########     ##
##    ##  ##       ##     ## ##     ## ##          ##    ##   ##      ##
##    ##  ##       ##     ## ##     ## ##          ##    ##    ##     ##
 ######   ########  #######  ##     ## ########    ##    ##     ##    ##

    #Defining Detector Geometry
    volume = DetectorVolume(1000.0, 1000.0)
    wirePitches = [5.0, 5.0, 5.0]
    wireTranslations = [0.0,0.0,0.0]
    angles = generateAngles(len(wirePitches))

    planes = utilities.generatePlaneInfo(wirePitches, volume, angles)

    #Generating Random Blobs
    # blobs = geometryGen.generateBlobs(planes,volume)

    # print(blobs)

    # blobs = [Blob(charge=4.828952447681453, wires=[(223, 226), (201, 204), (75, 80)], points=[Point(x=595.8786446454473, y=945.6709058084462), Point(x=621.5301267341816, y=946.3718554738933)]), Blob(charge=5.560288337141905, wires=[(108, 115), (58, 62), (46, 49)], points=[Point(x=750.7271773750969, y=195.37723530628503), Point(x=765.5255337579047, y=223.83891845934124)]), Blob(charge=4.721229266692435, wires=[(111, 117), (79, 82), (64, 67)], points=[Point(x=661.5830993014157, y=262.0096618341117), Point(x=676.7919427580774, y=289.05867096940364)]), Blob(charge=4.361531266668869, wires=[(46, 48), (74, 75), (126, 128)], points=[Point(x=359.032000205643, y=63.416651609800034), Point(x=366.50877374091743, y=66.2727800933862)]), Blob(charge=5.313535752893215, wires=[(45, 48), (140, 142), (191, 197)], points=[Point(x=14.838339866517725, y=255.45321903504325), Point(x=43.02000124931331, y=256.34181203064566)]), Blob(charge=5.674107403614195, wires=[(156, 160), (200, 202), (142, 144)], points=[Point(x=279.0889741992674, y=742.3297689987869), Point(x=289.6831786575615, y=759.9990050223491)])]

    blobs = [Blob(charge=5.560288337141905, wires=[(108, 115), (58, 62), (46, 49)], points=[Point(x=750.7271773750969, y=195.37723530628503), Point(x=765.5255337579047, y=223.83891845934124)]), Blob(charge=4.361531266668869, wires=[(46, 48), (74, 75), (126, 128)], points=[Point(x=359.032000205643, y=63.416651609800034), Point(x=366.50877374091743, y=66.2727800933862)]), Blob(charge=5.313535752893215, wires=[(45, 48), (140, 142), (191, 197)], points=[Point(x=14.838339866517725, y=255.45321903504325), Point(x=43.02000124931331, y=256.34181203064566)])]


    #Creating Event
    event = geometryGen.generateEvent(planes,blobs)
    #Merging Event
    event = geometryGen.mergeEvent(event)

    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")

    if reco:
        cells = geometryReco.reconstructCells(planes,event)
        print("\033[93m","Number of Cells:", len(cells),"\033[0m")

        if trueBlobs:
            trueCellMatrix = matrixGeneration.generateTrueCellMatrix(blobs,cells)
            trueCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),trueCellMatrix))
        else:
            trueCells = []

########  ########     ###    ##      ## #### ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##  ##  ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##  ##  ####  ## ##
##     ## ########  ##     ## ##  ##  ##  ##  ## ## ## ##   ####
##     ## ##   ##   ######### ##  ##  ##  ##  ##  #### ##    ##
##     ## ##    ##  ##     ## ##  ##  ##  ##  ##   ### ##    ##
########  ##     ## ##     ##  ###  ###  #### ##    ##  ######


    #Scaling Canvas to have proper aspect ratio considering detector
    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

    # draw.zoomCell(cells[0],100,volume)
    draw.zoomCell(cells[1],100,volume)
    # draw.zoomCell(cells[2],100,volume)
    # draw.zoomCell(cells[3],100,volume)


    #Generate Drawing Primitives
    drawnLines = draw.makeEventLines(planes,event, useCenterLines)
    drawnLines = draw.drawEventLines(drawnLines,volume, centerColor, centerStyle,edgeColor,edgeStyle)

    if reco:
        drawnCells = draw.drawCells(cells, asMarker,detectionColor, recoColor, cellWidth, trueCells)

        if cellNumbering:
                cellText = draw.drawCellNumbers(cells)

    if trueBlobs:
        drawnBlobs = draw.drawBlobs(blobs, trueColor, blobWidth)

        if blobNumbering:
            blobText = draw.drawCellNumbers(blobs,trueColor)

    # c1.AddExec( 'dynamic', 'TPython::Exec( "draw.zoom()" );' )
    # c1.Update()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
