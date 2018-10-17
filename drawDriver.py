#External Dependencies
import sys
import ROOT as root
import math
import numpy as np

#Internal Dependencies
from dataTypes import *
import utilities
import geometryGen
import geometryReco
import draw
import matrixGeneration
import chargeSolving

def generateAngles(noOfPlanes):
    individualAngle = math.pi/noOfPlanes
    angles = []

    for planeNo in range(noOfPlanes):
        angles.append(individualAngle * (planeNo + 1))

    return angles


def main(argv):
 #######  ########  ######## ####  #######  ##    ##  ######
##     ## ##     ##    ##     ##  ##     ## ###   ## ##    ##
##     ## ##     ##    ##     ##  ##     ## ####  ## ##
##     ## ########     ##     ##  ##     ## ## ## ##  ######
##     ## ##           ##     ##  ##     ## ##  ####       ##
##     ## ##           ##     ##  ##     ## ##   ### ##    ##
 #######  ##           ##    ####  #######  ##    ##  ######

    #Set boolean options
    reco = True
    trueBlobs = True
    asMarker = False
    cellNumbering = False
    blobNumbering = False
    useCenterLines = "both"
    drawFake = True

    #saveOptions
    directory = "img"
    fileName = "planeComp"

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

    #Regularization Strength
    alpha = 0.1


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
    angles = generateAngles(len(wirePitches))

    planes = utilities.generatePlaneInfo(wirePitches, volume, angles)

    #Generating Random Blobs
    # blobs = geometryGen.generateBlobs(planes,volume, 5)

    blobs = [Blob(charge=16.817050314525563, wires=[(37, 43), (84, 87), (144, 146)], points=[Point(x=266.2702903438424, y=61.721582405888206), Point(x=279.06488600840225, y=88.56545278159894)]), Blob(charge=28.538433057496096, wires=[(96, 101), (49, 51), (50, 52)], points=[Point(x=736.3935059972442, y=131.76142968445015), Point(x=747.4521906990743, y=152.30731100309993)]), Blob(charge=33.031012508417305, wires=[(108, 114), (131, 132), (117, 123)], points=[Point(x=383.7691311506287, y=406.29539144323303), Point(x=411.0824425471208, y=422.2097468369453)]), Blob(charge=26.87037017812092, wires=[(63, 69), (110, 114), (145, 146)], points=[Point(x=265.28289648149183, y=214.44567715573982), Point(x=272.1466986953104, y=243.6909819161242)]), Blob(charge=34.00003693193055, wires=[(209, 213), (208, 208), (94, 98)], points=[Point(x=505.90296957755345, y=915.6380664123009), Point(x=527.2484490565548, y=929.1363967481078)])]


    print(blobs)

    #Creating Event
    event = geometryGen.generateEvent(planes,blobs)
    #Merging Event
    event = geometryGen.mergeEvent(event)

    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")

    if reco:
        cells = geometryReco.reconstructCells(planes,event)
        print("\033[93m","Number of Cells:", len(cells),"\033[0m")

        #create matrix associating wires and cells
        channelList, geometryMatrix = matrixGeneration.constructGeometryMatrix(planes, cells)
        # print("A")
        # print(geometryMatrix)
        # print(channelList)

        #covariance Matrix
        covarianceMatrix = np.identity(len(channelList))

        #create Chrage Matrices
        masterChargeList = matrixGeneration.constructChargeList(planes,blobs)
        recoWireMatrix = matrixGeneration.measureCharge(channelList,masterChargeList)
        # print("reco:y")
        # print(recoWireMatrix)

        #solve
        geometryMatrixU, recoWireMatrixU = matrixGeneration.addUncertainity(geometryMatrix,recoWireMatrix,covarianceMatrix)

        recoCellMatrix = chargeSolving.solve(recoWireMatrixU, geometryMatrixU, alpha)
        recoCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),recoCellMatrix))
        print("reco:x")
        print(recoCellMatrix)

        if trueBlobs:
            trueCellMatrix = matrixGeneration.generateTrueCellMatrix(blobs,cells)
            trueCells = list(map(lambda x: not math.isclose(x,0,rel_tol=1e-5),trueCellMatrix))
            print("x")
            print(trueCellMatrix)

            trueWireMatrix = geometryMatrix*trueCellMatrix
            # print("y")
            # print(trueWireMatrix)
        else:
            trueCells = []


##  ########     ###    ##      ## #### ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##  ##  ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##  ##  ####  ## ##
##     ## ########  ##     ## ##  ##  ##  ##  ## ## ## ##   ####
##     ## ##   ##   ######### ##  ##  ##  ##  ##  #### ##    ##
##     ## ##    ##  ##     ## ##  ##  ##  ##  ##   ### ##    ##
########  ##     ## ##     ##  ###  ###  #### ##    ##  ######


    #Scaling Canvas to have proper aspect ratio considering detector
    canvasWidth = 700
    c1 = root.TCanvas( "Detector", "Detector", 200, 10, canvasWidth, int(canvasWidth*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)

    # draw.zoomCell(cells[0],100,volume)
    # draw.zoomCell(cells[1],100,volume)
    # draw.zoomCell(cells[2],100,volume)
    # draw.zoomCell(cells[3],100,volume)


    #Generate Drawing Primitives
    drawnLines = draw.makeEventLines(planes,event, useCenterLines)
    drawnLines = draw.drawEventLines(drawnLines,volume, centerColor, centerStyle,edgeColor,edgeStyle)

    if reco:
        drawnCells = draw.drawCells(cells, asMarker,detectionColor, recoColor, cellWidth, recoCells, drawFake)

        if cellNumbering:
                cellText = draw.drawCellNumbers(cells, edgeColor, recoCells, drawFake)

    if trueBlobs:
        drawnBlobs = draw.drawBlobs(blobs, trueColor, blobWidth)

        if blobNumbering:
            blobText = draw.drawCellNumbers(blobs,trueColor)

    if isinstance(fileName, str) and len(fileName)>0:
        draw.saveImage(fileName,directory)
    # c1.AddExec( 'dynamic', 'TPython::Exec( "draw.zoom()" );' )
    # c1.Update()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
