#add parent directory to import path
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

#Internal Dependencies
import utilities
from dataTypes import *

######## ########  ######  ########
   ##    ##       ##    ##    ##
   ##    ##       ##          ##
   ##    ######    ######     ##
   ##    ##             ##    ##
   ##    ##       ##    ##    ##
   ##    ########  ######     ##

def test_generatePlaneInfo():
   volume = DetectorVolume(1000.0, 1000.0)
   wirePitches = [5.0, 5.0, 5.0]
   wireTranslations = [0.0,0.0,0.0]
   angles = [1.0471975511965976, 2.0943951023931953, 3.141592653589793]

   ans = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, wireTranslation=0.0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, wireTranslation=0.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, wireTranslation=0.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]

   assert utilities.generatePlaneInfo(wirePitches, volume, angles, wireTranslations) == ans

def test_wireNumberFromPoint():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, wireTranslation=0.0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, wireTranslation=0.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, wireTranslation=0.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]

    points = [Point(x=261.7850716101253, y=245.02750845872833), Point(x=214.89166987825493, y=113.03402239905014), Point(x=0.2455514618699972, y=410.9473923892855), Point(x=581.1125709476491, y=493.9800164009199), Point(x=538.7063614584209, y=205.49539960120322)]

    ans = [[68, 116, 147], [41, 98, 157], [71, 171, 199], [143, 127, 83], [89, 81, 92]]

    for pointNo, point in enumerate(points):
        for planeNo, plane in enumerate(planes):
            assert utilities.wireNumberFromPoint(plane, point) == ans[pointNo][planeNo]
