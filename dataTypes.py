from collections import namedtuple

# define data Structures
Point = namedtuple('Point', ['x', 'y'])
Point.__doc__ = '''A 2-dimensional coordinate'''
Point.x.__doc__ = '''x coordinate'''
Point.y.__doc__ = '''y coordinate'''

Line = namedtuple('Line', ['point0', 'point1'])
Line.__doc__ = '''A line defined by two points'''
Line.point0.__doc__ = '''First Point'''
Line.point1.__doc__ = '''Second Point'''

PlaneInfo = namedtuple('PlaneInfo', ['angle', 'pitch', 'noOfWires', 'originTranslation', 'sin', 'cos', 'gradient'])
PlaneInfo.__doc__ = '''List of information about planes'''
PlaneInfo.angle.__doc__ = '''angle by whitch plane is roatated'''
PlaneInfo.pitch.__doc__ = '''wire pitch for the plane'''
PlaneInfo.noOfWires.__doc__ = '''number of wires in the plane'''
PlaneInfo.originTranslation.__doc__ = '''x offset for origin of the plane (y origin is always 0)'''
PlaneInfo.sin.__doc__ = '''sin of the plane angle'''
PlaneInfo.cos.__doc__ = '''cos of the plane angle'''
PlaneInfo.gradient.__doc__ = '''gradient of the wires in plane'''

DetectorVolume = namedtuple('DetectorVolume', ['width', 'height'])
DetectorVolume.__doc__ = '''2D dimensions of the detector'''
DetectorVolume.width.__doc__ = '''width of detector'''
DetectorVolume.height.__doc__ = '''height of detector'''

Cell = namedtuple('Cell', ['wires','points'])
Cell.__doc__='''Merged Cell in Detector'''
Cell.wires.__doc__='''binding wires of the Cell'''
Cell.points.__doc__='''points binding the Cell'''

Blob = namedtuple('Blob', ['charge', 'wires', 'points'])
Blob.__doc__ ='''Blob detected in tomographic slice'''
Blob.charge.__doc__ ='''Charge Associated with the Blob'''
Blob.wires.__doc__ = '''Wires that bind the Blob'''
Blob.points.__doc__ ='''Points that define the ConvexHull of the blob'''
