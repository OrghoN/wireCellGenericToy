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

def test_lineIntersection():
    line0 = Line(point0=Point(x=500.0, y=6.123233995736766e-14), point1=Point(x=500.0, y=1.0000000000000613))
    line1 = Line(point0=Point(x=250.00000000000006, y=433.0127018922193), point1=Point(x=251.00000000000006, y=432.43535162302965))

    ans = Point(x=500.0, y=288.6751345948028)

    assert geometryReco.lineIntersection(line0,line1)

def test_wireIntersection():
    plane0 = PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263)
    plane1 = PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')

    wire0 = (100,103)
    wire1 = (100,110)

    ans = [Point(x=500.0, y=288.6751345948028), Point(x=500.0, y=311.7691453623879), Point(x=445.0, y=320.4293994002336), Point(x=445.0, y=343.5234101678187)]

    assert geometryReco.wireIntersection(plane0, wire0, plane1, wire1) == ans

def test_sortPoints():
    points = [Point(x=261.7850716101253, y=245.02750845872833), Point(x=214.89166987825493, y=113.03402239905014), Point(x=0.2455514618699972, y=410.9473923892855), Point(x=581.1125709476491, y=493.9800164009199), Point(x=538.7063614584209, y=205.49539960120322)]

    ans = [Point(x=581.1125709476491, y=493.9800164009199), Point(x=0.2455514618699972, y=410.9473923892855), Point(x=214.89166987825493, y=113.03402239905014), Point(x=538.7063614584209, y=205.49539960120322)]

    assert geometryReco.sortPoints(points) == ans

def test_checkCell():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]
    wires0 = [(41, 143), (81, 171), (83, 199)]
    wires1 = [(0, 0), (100, 100), (100, 100)]

    ans0 = Cell(wires=[(41, 143), (81, 171), (83, 199)], points=[Point(x=0.0, y=236.71361036774397), Point(x=300.000000000005, y=63.508529610854275), Point(x=585.0, y=228.05335632990193), Point(x=585.0, y=493.6344801571189), Point(x=360.0000000000362, y=623.5382907247695), Point(x=0.0, y=415.6921938164742)])
    ans1 = Cell(False,False)

    assert geometryReco.checkCell(planes, wires0) == ans0
    assert geometryReco.checkCell(planes, wires1) == ans1

def test_reconstructCells():
    planes = [PlaneInfo(angle=1.0471975511965976, pitch=5.0, noOfWires=273, originTranslation=0, sin=0.8660254037844386, cos=0.5000000000000001, gradient=-0.5773502691896263), PlaneInfo(angle=2.0943951023931953, pitch=5.0, noOfWires=273, originTranslation=1000.0, sin=0.8660254037844387, cos=-0.4999999999999998, gradient=0.5773502691896255), PlaneInfo(angle=3.141592653589793, pitch=5.0, noOfWires=200, originTranslation=1000.0, sin=1.2246467991473532e-16, cos=-1.0, gradient='INF')]
    event = [[(41, 143),(100, 100)],[(81, 171),(100, 100)],[(83, 199), (100, 100)]]

    ans = [Cell(wires=[(41, 143), (81, 171), (83, 199)], points=[Point(x=0.0, y=236.71361036774397), Point(x=300.000000000005, y=63.508529610854275), Point(x=585.0, y=228.05335632990193), Point(x=585.0, y=493.6344801571189), Point(x=360.0000000000362, y=623.5382907247695), Point(x=0.0, y=415.6921938164742)]), Cell(wires=[(79, 143), (81, 144), (100, 100)], points=[Point(x=500.0, y=542.7092530382392), Point(x=495.0, y=545.5960043841875), Point(x=495.0, y=176.09183210283334), Point(x=500.0, y=178.9785834487816)]), Cell(wires=[(41, 118), (100, 100), (83, 159)], points=[Point(x=585.0, y=343.5234101678276), Point(x=200.0000000000065, y=121.24355652981569), Point(x=204.99999999999383, y=118.3568051838749), Point(x=585.0, y=337.74990747594586)]), Cell(wires=[(99, 100), (100, 100), (100, 100)], points=[Point(x=495.0, y=285.78838324887727), Point(x=500.0, y=288.6751345948255), Point(x=500.0, y=294.44863728670725), Point(x=495.0, y=291.561885940759)]), Cell(wires=[(100, 100), (82, 171), (83, 171)], points=[Point(x=140.0000000000449, y=496.52123150305124), Point(x=585.0, y=239.60036171368245), Point(x=585.0, y=245.37386440559328), Point(x=145.0000000000573, y=499.40798284900666)]), Cell(wires=[(100, 100), (99, 102), (100, 100)], points=[Point(x=495.0, y=291.56188594075104), Point(x=500.0, y=288.6751345948028), Point(x=500.0, y=294.4486372867136), Point(x=495.0, y=297.3353886326619)]), Cell(wires=[(100, 100), (100, 100), (99, 101)], points=[Point(x=500.0000000000055, y=294.44863728671044), Point(x=494.9999999999931, y=291.561885940755), Point(x=499.99999999998033, y=288.67513459481415), Point(x=504.9999999999927, y=291.56188594076957)]), Cell(wires=[(100, 100), (100, 100), (100, 100)], points=[Point(x=494.9999999999931, y=291.561885940755), Point(x=500.0, y=288.6751345948028), Point(x=500.0000000000055, y=294.44863728671044), Point(x=500.0, y=294.4486372867136)])]

    assert geometryReco.reconstructCells(planes,event) == ans
