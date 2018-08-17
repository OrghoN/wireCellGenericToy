#add parent directory to import path
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

#Internal Dependencies
import geometryReco
from dataTypes import *


def test_makeLines():
    plane = PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')
    wire = (100,103)

    ans = [Line(point0=Point(x=500.0, y=6.123233995736766e-14), point1=Point(x=500.0, y=1.0000000000000613)), Line(point0=Point(x=480.0, y=6.368163355566237e-14), point1=Point(x=480.0, y=1.0000000000000637))]

    assert geometryReco.makeLines(plane, wire) == ans
