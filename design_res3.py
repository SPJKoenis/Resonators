import gdspy
import numpy as np
from math import *


class coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return ('(' + str(self.x) + ', ' + str(self.y) + ')')


class rotations:
    def __init__(self, phi1, phi2):
        self.phi1 = phi1
        self.phi2 = phi2

    def __repr__(self):
        return ('(' + str(self.phi1) + ', ' + str(self.phi2) + ')')


def Vertical_Part(x, y, y_turn, d, rot, delta, right, mode='full'):
    r_outer = d * 2.5
    r_inner = d * 1.5
    if y_turn < y:
        direction = 1
    else:
        direction = -1
    if mode == 'cut': return gdspy.Rectangle((x - delta, y), (x + d + delta, y_turn))
    if (rot.phi2 - rot.phi1) > 0:
        if direction == 1:
            return gdspy.boolean(gdspy.Rectangle((x -d - delta, y), (x + delta, y_turn + r_outer)),
                                 gdspy.Round((x + r_inner, y_turn + r_outer), r_outer + delta, r_inner - delta,
                                             rot.phi1, rot.phi2, tolerance=0.01),
                                 'or'), coordinates(x + r_inner, y_turn)
        else:
            return gdspy.boolean(gdspy.Rectangle((x - delta, y), (x + d + delta, y_turn - r_outer)),
                                 gdspy.Round((x + r_inner + d, y_turn + r_outer), r_outer + delta, r_inner - delta,
                                             rot.phi1, rot.phi2, tolerance=0.01),
                                 'or'), coordinates(x + (r_inner + d), y_turn)
    else:
        if direction == 1:
            return gdspy.boolean(gdspy.Rectangle((x - delta, y), (x + d + delta, y_turn + r_outer)),
                                 gdspy.Round((x - r_inner, y_turn + r_outer), r_outer + delta,
                                             r_inner - delta, rot.phi1, rot.phi2, tolerance=0.01),
                                 'or'), coordinates(x - r_inner, y_turn)
        else:
            return gdspy.boolean(gdspy.Rectangle((x - delta, y), (x + d + delta, y_turn - r_inner)),
                                 gdspy.Round((x + r_outer, y_turn + direction * r_inner), r_outer + delta,
                                             r_inner - delta, rot.phi1, rot.phi2, tolerance=0.01),
                                 'or'), coordinates(x + r_outer, y_turn)


def Horizontal_Part(x, y, x_turn, d, rot, delta, right, mode='full'):
    r_outer = d * 2.5
    r_inner = d * 1.5
    if x_turn > x:
        direction = 1
    else:
        direction = -1
    if mode == 'cut': return gdspy.Rectangle((x, y - delta), (x_turn, y + d + delta))
    if (rot.phi2 - rot.phi1) * direction > 0:
        return gdspy.boolean(gdspy.Rectangle((x, y - delta), (x_turn - r_inner * direction, y + d + delta)),
                             gdspy.Round((x_turn - r_inner * direction, y + r_inner + d), r_outer + delta,
                                         r_inner - delta, rot.phi1, rot.phi2, tolerance=0.01),
                             'or'), coordinates(x_turn, y + r_inner + d)
    else:
        return gdspy.boolean(gdspy.Rectangle((x, y - delta), (x_turn - r_inner * direction, y + d + delta)),
                             gdspy.Round((x_turn - r_inner * direction, y - r_inner), r_outer + delta, r_inner - delta,
                                         rot.phi1, rot.phi2, tolerance=0.01),
                             'or'), coordinates(x_turn, y - r_inner)


def Line_With_Turns(coords, rots, d, d_given, start='horizontal', right=True):
    if start == 'horizontal':
        f = True
    else:
        f = False
    delta = (d_given - d) / 2
    rot = rotations(0, 0)
    for i, coord in enumerate(coords):
        # print(i, coord)
        if (i == 0):
            prev_coord = coord
            continue
        if i != (len(coords) - 1):
            rot = rots[i - 1]
        if (i == len(coords) - 1):
            if f:
                part = Horizontal_Part(prev_coord.x, prev_coord.y, coord.x, d, rot, delta, right, mode='cut')
            else:
                part = Vertical_Part(prev_coord.x, prev_coord.y, coord.y, d, rot, delta, right, mode='cut')
            break
        if f:
            part, prev_coord = Horizontal_Part(prev_coord.x, prev_coord.y, coord.x, d, rot, delta, right)
            f = False
        else:
            part, prev_coord = Vertical_Part(prev_coord.x, prev_coord.y, coord.y, d, rot, delta, right)
            f = True
        print(f, part)
        if (i == 1):
            result = part
        else:
            result = gdspy.boolean(part, result, 'or')
    if len(rots) > 0:
        return gdspy.boolean(part, result, 'or')
    else:
        return part


class Pads:
    def __init__(self, a, b, number, d_arr, d1_arr, d2_arr, layer, coords=[]):
        self.number = number
        self.coords = coords
        self.d_arr = d_arr
        self.d1_arr = d1_arr
        self.d2_arr = d2_arr
        self.a = a
        self.b = b
        self.reference_points = []
        self.layer = layer
        self.restricted_area = []

    def Contact_Pad(self, x, y, d, d1, d2):
        #		d2 = 100
        r1 = gdspy.Polygon([(x, y), (x + d2, y), (x + d2 + 400, y - 60), (x + d2 + 400, y - 550),
                            (x - 400, y - 550), (x - 400, y - 60)])
        self.restricted_area.append(r1)
        delta = 0.5 * (d2 - d1)
        r2 = gdspy.Polygon([(x + delta, y), (x + d1 + delta, y), (x + d1 + delta + 300, y - 160),
                            (x + d1 + delta + 300, y - 550 + delta),
                            (x - 300 + delta, y - 550 + delta), (x - 300 + delta, y - 160)])
        delta = 0.5 * (d2 - d)
        r3 = gdspy.Polygon([(x + delta, y), (x + d + delta, y), (x + d + delta + 200, y - 160),
                            (x + d + delta + 200, y - 450 + delta),
                            (x - 200 + delta, y - 450 + delta), (x - 200 + delta, y - 160)])
        return gdspy.boolean(gdspy.boolean(r1, r2, 'not'), r3, 'or')

    def Generate_Ground(self):
        r1 = gdspy.Rectangle((0, 0), (self.a, self.b))
        r2 = gdspy.Rectangle((400, 400), (self.a - 400, self.b - 400))
        result = gdspy.boolean(r1, r2, 'not')
        self.restricted_area.append(result)
        for coord, d, d1, d2 in zip(self.coords, self.d_arr, self.d1_arr, self.d2_arr):
            Pad = self.Contact_Pad(coord.x, coord.y, d, d1, d2)
            # to_bool = gdspy.Rectangle((coord.x - 220, coord.y), (coord.x + 220 + d2, coord.y - 700))
            self.reference_points.append(coord)
            if coord.x < 900:
                Pad.rotate(-np.pi / 2, [coord.x, coord.y])
                Pad.translate(0, d2)
                self.restricted_area[len(self.restricted_area) - 1].rotate(-np.pi / 2, [coord.x, coord.y])
                self.restricted_area[len(self.restricted_area) - 1].translate(0, d2)
            # to_bool = gdspy.Rectangle(Pad.get_bounding_box()[0].tolist(), Pad.get_bounding_box()[1].tolist())
            elif coord.x > self.b - 900:
                Pad.rotate(np.pi / 2, [coord.x, coord.y])
                self.restricted_area[len(self.restricted_area) - 1].rotate(np.pi / 2, [coord.x, coord.y])
            # to_bool = gdspy.Rectangle(Pad.get_bounding_box()[0].tolist(), Pad.get_bounding_box()[1].tolist())
            elif coord.y > self.b / 2:
                Pad.mirror([0, coord.y + d2 / 2], [self.b, coord.y + d2 / 2])
                self.restricted_area[len(self.restricted_area) - 1].mirror([0, coord.y + d2 / 2],
                                                                           [self.b, coord.y + d2 / 2])
                self.reference_points[len(self.reference_points) - 1].y = Pad.get_bounding_box()[0, 1]
            # Pad.translate(d2, 0)
            # to_bool = to_bool.mirror([0, coord.y + d2/2], [b, coord.y + d2/2])
            to_bool = gdspy.Rectangle(Pad.get_bounding_box()[0].tolist(), Pad.get_bounding_box()[1].tolist())
            result = gdspy.boolean(gdspy.boolean(result, to_bool, 'not'), Pad, 'or', layer=self.layer)
        return result


class Transmission_Line:
    def __init__(self, pads, start_pad, finish_pad, d, d1, d2, layer):
        self.start = coordinates(pads.reference_points[start_pad].x, pads.reference_points[start_pad].y + (d2 - d) / 2)
        self.end = coordinates(pads.reference_points[finish_pad].x, pads.reference_points[finish_pad].y + (d2 - d) / 2)
        self.d = d
        self.d1 = d1
        self.d2 = d2
        self.layer = layer
        self.restricted_area = []
        self.r_outer = (self.d1 * 4 - self.d) / 2 + self.d
        self.r_inner = (self.d1 * 4 - self.d) / 2

    def GenerateTL(self, d, coords, rots, start='horizontal', right=False):
        delta = (d - self.d) / 2

        coords = [coordinates(self.start.x + self.d2, self.start.y),
                  coordinates(self.start.x + self.d2, 3900 - self.d / 2),
                  coordinates(self.end.x - self.d2 - 100, 3900 - self.d / 2),
                  coordinates(self.end.x - self.d2 - 100, 2500 - self.d / 2),
                  coordinates(self.start.x + self.d2 + 100, 2500 - self.d / 2),
                  coordinates(self.start.x + self.d2 + 100, 1100 - self.d / 2),
                  coordinates(self.end.x - self.d2, 1100 - self.d / 2), coordinates(self.end.x - self.d2, self.end.y)]
        rots = [rotations(-np.pi / 2, 0), rotations(np.pi, np.pi / 2), rotations(np.pi / 2, 0),
                rotations(0, -1 / 2 * np.pi), rotations(np.pi / 2, np.pi), rotations(np.pi, 3 / 2 * np.pi),
                rotations(3 / 2 * np.pi, 2 * np.pi), rotations(np.pi, np.pi / 2)]

        # coordinates(9400, 1100-TL_total/2)
        coords = [self.start] + coords
        coords.append(self.end)
        print(coords)
        result = Line_With_Turns(coords, rots, self.d, d, start=start, right=right)
        # rec = gdspy.Rectangle((coords[1].x, coords[0].y-d/2 +self.d/2), (coords[1].x + 270, coords[0].y + d/2 + self.d/2))
        # result = gdspy.boolean(result, rec, 'or')
        # sec = gdspy.Round((coords[1].x + 270, coords[0].y + self.d - self.r_outer), self.r_outer + delta, self.r_inner - delta, np.pi*2.5, 2*np.pi)
        # result = gdspy.boolean(result, sec, 'or')
        # rec = gdspy.Rectangle((coords[1].x + 270 + self.r_inner -delta, coords[0].y + self.d/2 + self.d/2 - self.r_outer), (coords[1].x + 270 + self.r_inner + self.d + delta, coords[0].y + self.d - 1400 + self.r_inner))
        # result = gdspy.boolean(result, rec, 'or')
        # sec = gdspy.Round((coords[1].x + 270 + self.r_inner + self.d - self.r_outer, coords[0].y + self.d - 1400 + self.r_inner), self.r_outer + delta, self.r_inner - delta, 2*np.pi, 1.5*np.pi)
        # result = gdspy.boolean(result, sec, 'or')
        # rec = gdspy.Rectangle((coords[1].x + 270 + self.r_inner + self.d - self.r_outer, coords[0].y + self.d - 1400 + delta), (coords[0].x-270, coords[0].y + self.d - 1400 - self.d - delta))
        # result = gdspy.boolean(result, rec, 'or')
        # sec = gdspy.Round((coords[0].x-270, coords[0].y + self.d - 1400 - self.r_outer), self.r_outer + delta, self.r_inner - delta, 0.5*np.pi, 1*np.pi)
        # result = gdspy.boolean(result, sec, 'or')
        # rec = gdspy.Rectangle((coords[0].x-270 - self.r_inner + delta, coords[0].y + self.d - 1400 - self.r_outer), (coords[0].x-270 - self.r_inner - self.d - delta, coords[0].y + self.d - 2800 + self.r_inner))
        # result = gdspy.boolean(result, rec, 'or')
        # sec = gdspy.Round((coords[0].x-270 , coords[0].y + self.d - 2800 + self.r_inner), self.r_outer + delta, self.r_inner - delta, 1*np.pi, 1.5*np.pi)
        # result = gdspy.boolean(result, sec, 'or')
        # rec = gdspy.Rectangle((coords[0].x-270, coords[1].y + self.d + delta), (coords[1].x, coords[1].y - delta))
        # result = gdspy.boolean(result, rec, 'or')

        if d == self.d2:
            self.restricted_area.append(result)
        return result

    def GenerateTL1(self, coords, rots, start='horizontal', right=False):
        coords = [self.start] + coords
        coords.append(self.end)
        return Line_With_Turns(coords, rots, self.d, self.d, start=start, right=right)

    def GenerateTL2(self, coords, rots, start='horizontal', right=False):
        coords = [self.start] + coords
        coords.append(self.end)
        return Line_With_Turns(coords, rots, self.d, self.d1, start=start, right=right)

    def GenerateTL3(self, coords, rots, start='horizontal', right=False):
        coords = [self.start] + coords
        coords.append(self.end)
        self.restricted_area.append(Line_With_Turns(coords, rots, self.d, self.d2, start=start, right=right))
        return Line_With_Turns(coords, rots, self.d, self.d2, start=start, right=right)
