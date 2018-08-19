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
    cellNumbering = False
    blobNumbering = False
    useCenterLines = "both"

    #Set Colors
    trueColor = root.kGreen
    centerColor = root.kBlue
    centerStyle = 2
    cellColor = root.kRed


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
    blobs = geometryGen.generateBlobs(planes,volume)

    # blobs = [Blob(charge=4.58748705679011, wires=[(153, 159), (90, 93), (33, 37)], points=[Point(x=813.8436039106869, y=417.60082990853977), Point(x=830.2734426303631, y=440.38585607276224)]), Blob(charge=5.4507416355248655, wires=[(76, 79), (61, 62), (82, 85)], points=[Point(x=571.9607228368554, y=112.88215335645768), Point(x=588.5515032286443, y=118.44586995598164)]), Blob(charge=5.495377296955472, wires=[(17, 22), (105, 105), (183, 188)], points=[Point(x=58.71312010523644, y=68.38897935986054), Point(x=84.83345663997831, y=82.47157029824348)]), Blob(charge=5.241463033926113, wires=[(136, 138), (110, 111), (71, 75)], points=[Point(x=624.9752668698684, y=427.14556360556423), Point(x=640.3274801472991, y=431.31931873656487)]), Blob(charge=4.208319477076222, wires=[(131, 135), (160, 162), (125, 130)], points=[Point(x=348.07442850616644, y=559.1636459012446), Point(x=373.85269822519103, y=567.3346897979171)]), Blob(charge=5.333965066328843, wires=[(116, 118), (54, 56), (37, 37)], points=[Point(x=810.1658190815788, y=203.6702859033279), Point(x=814.233160795954, y=216.24453035143915)]), Blob(charge=5.475988684715355, wires=[(108, 114), (173, 175), (161, 165)], points=[Point(x=174.52867097725323, y=527.7379959165255), Point(x=193.57279642227633, y=547.4596105178639)])]

    #Creating Event
    event = geometryGen.generateEvent(planes,blobs)
    #Merging Event
    event = geometryGen.mergeEvent(event)

    print("\033[93m","Number of true Blobs:",len(blobs),"\033[0m")

    if reco:
        cells = geometryReco.reconstructCells(planes,event)
        print("\033[93m","Number of Cells:", len(cells),"\033[0m")

########  ########     ###    ##      ## #### ##    ##  ######
##     ## ##     ##   ## ##   ##  ##  ##  ##  ###   ## ##    ##
##     ## ##     ##  ##   ##  ##  ##  ##  ##  ####  ## ##
##     ## ########  ##     ## ##  ##  ##  ##  ## ## ## ##   ####
##     ## ##   ##   ######### ##  ##  ##  ##  ##  #### ##    ##
##     ## ##    ##  ##     ## ##  ##  ##  ##  ##   ### ##    ##
########  ##     ## ##     ##  ###  ###  #### ##    ##  ######

    #Generate Drawing Primitives
    drawnLines = draw.makeEventLines(planes,event, useCenterLines)
    drawnLines = draw.drawEventLines(drawnLines,volume)

    if reco:
        drawnCells = draw.drawCells(cells, asMarker)

        if cellNumbering:
                cellText = draw.drawCellNumbers(cells)

    if trueBlobs:
        drawnBlobs = draw.drawBlobs(blobs)

        if blobNumbering:
            blobText = draw.drawCellNumbers(blobs)

    #Paint Drawing Primitives
    #Scaling Canvas to have proper aspect ratio considering detector
    c1 = root.TCanvas( "Detector", "Detector", 200, 10, 700, int(700*(volume.height/volume.width)) )
    c1.Range(0,0,volume.width,volume.height)
    # c1.Range(150,480,250,580)

    #paint Lines
    for line in drawnLines:
        if line[1]:
            line[0].SetLineColor(centerColor)
            line[0].SetLineStyle(centerStyle)
        line[0].Draw()

    #paint Cells
    if reco:
        for drawnCellNo, drawnCell in enumerate(drawnCells):
            for marker in drawnCell:
                if asMarker:
                    marker.SetMarkerColor(cellColor)
                    marker.Draw()
                else:
                    marker.SetLineWidth(4)
                    marker.SetLineColor(cellColor)
                    marker.Draw()

            if cellNumbering:
                for text in cellText:
                    # text.SetTextColor(cellColor)
                    text.Draw()
    if trueBlobs:
        for marker in drawnBlobs:
            marker.SetLineWidth(4)
            marker.SetLineColor(trueColor)
            marker.Draw()

        if blobNumbering:
            for text in blobText:
                text.SetTextColor(trueColor)
                text.Draw()

    # c1.AddExec( 'dynamic', 'TPython::Exec( "draw.zoom()" );' )
    # c1.Update()

    root.gApplication.Run()


if __name__ == "__main__":
    main(sys.argv)
