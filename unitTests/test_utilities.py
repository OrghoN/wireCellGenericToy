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

   angles = [1.0471975511965976, 2.0943951023931953, 3.141592653589793]

   ans = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]

   assert utilities.generatePlaneInfo(wirePitches, volume, angles) == ans

def test_wireNumberFromPoint():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]

    points = [Point(x=261.7850716101253, y=245.02750845872833), Point(x=214.89166987825493, y=113.03402239905014), Point(x=0.2455514618699972, y=410.9473923892855), Point(x=581.1125709476491, y=493.9800164009199), Point(x=538.7063614584209, y=205.49539960120322)]

    ans = [[68, 116, 147], [41, 98, 157], [71, 171, 199], [143, 127, 83], [89, 81, 92]]

    for pointNo, point in enumerate(points):
        for planeNo, plane in enumerate(planes):
            assert utilities.wireNumberFromPoint(plane, point) == ans[pointNo][planeNo]

def test_pointInWire():
    plane = PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')
    points = [Point(995,500),Point(990,500),Point(985,500),Point(980,500),Point(975,500)]

    for pointNo, point in enumerate(points):
        assert utilities.pointInWire(plane,point,(pointNo,pointNo+1))

def test_fireWires():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]

    points = [Point(x=261.7850716101253, y=245.02750845872833), Point(x=214.89166987825493, y=113.03402239905014), Point(x=0.2455514618699972, y=410.9473923892855), Point(x=581.1125709476491, y=493.9800164009199), Point(x=538.7063614584209, y=205.49539960120322)]

    ans = [[41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171], [83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199]]

    assert utilities.fireWires(planes, points) == ans

def test_getChannelNo():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]
    wireNo = 100
    planeNo = 1

    ans = 373

    assert utilities.getChannelNo(planes, wireNo, planeNo) == ans
