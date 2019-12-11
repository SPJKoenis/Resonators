import gdspy
import numpy as np
from math import *
from design_res3 import *


class Resonator:
    def __init__(self, x1, y1, frequency, w, s, TLi, TLv, TLg, DE, l_vert=0):
        # w and s are the characteristic widths of the resonator cavity.

        self.frequency = frequency
        self.length = 299792458 / (4 * frequency) * 1e6 / 2.5249  # the speed of light is modified in the CPW
        self.d = w
        self.d1 = w + (2 * s)
        self.d2 = 2.2 * self.d1
        self.x1 = x1
        self.y1 = y1
        self.l_vert = l_vert
        self.l_coupl = self.length / 6.9  # the ratio between the coupling length and the total resonator length is constant
        print('coupling length:', self.l_coupl)
        self.r_outer = (self.d1 * 1.7 - self.d) / 2 + self.d
        self.width = self.l_coupl - self.r_outer
        print('x coordinate of end of resonator', self.x1 + 2 * self.r_outer + self.width + (self.d2 - self.d))
        self.TL_ground = TLg
        self.TL_tot = TLi + 2 * (TLg + TLv)
        self.TL_vac = TLv
        self.DE = DE  # 5 + self.d1/4 +w/s*0.7 #this is the width of the conductor that separates the resonator and the TL
        print('DE=', self.DE)
        print('...')

    def Waveguide(self, x1, y1, length, d_given):  # , x_e, y_e):
        delta = (d_given - self.d) / 2
        r_outer = self.r_outer
        r_inner = (self.d1 * 1.7 - self.d) / 2  # Difference between the two should be self.d
        r = 0.5 * (r_outer + r_inner)
        width = self.width
        l_reserved = self.l_vert + self.l_coupl + 0.5 * np.pi * r + np.pi * r  # 0.5 pi for the quarter circle to the vertical piece
        N = floor((self.length - l_reserved) / (np.pi * r + width))  # number of curves
        l_horiz = self.length - l_reserved - (np.pi * r + width) * (N)
        if l_horiz > width:
            self.l_vert += l_horiz - width
            l_horiz = width
        rect = gdspy.Rectangle((x1 + r_outer, y1 - delta),
                               (x1 + r_outer + self.l_coupl + delta / 2.5, y1 + self.d + delta))
        sector = gdspy.Round((x1 + r_outer, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=0.5 * np.pi,
                             final_angle=1.5 * np.pi, tolerance=0.01)
        result = gdspy.boolean(rect, sector, 'or')
        for i in range(N):
            rect = gdspy.Rectangle((x1 + r_outer, y1 + (r_outer + r_inner) * (i + 1) - delta),
                                   (x1 + r_outer + width, y1 + (r_outer + r_inner) * (i + 1) + self.d + delta))
            xr = x1 + width + r_outer if i % 2 == 0 else x1 + r_outer
            yr = y1 + r_outer * 2 + (2 * r_inner + self.d) * i + r_inner
            sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta,
                                 initial_angle=1.5 * np.pi if i % 2 == 0 else 0.5 * np.pi,
                                 final_angle=2.5 * np.pi if i % 2 == 0 else 1.5 * np.pi, tolerance=0.01)
            result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
        i = N - 1
        xr1 = x1 + r_outer if i % 2 == 1 else x1 + width + r_outer
        xr2 = x1 + r_outer + l_horiz if i % 2 == 1 else x1 + width + r_outer - l_horiz
        rect = gdspy.Rectangle((xr1, y1 + (r_outer + r_inner) * (N + 1) - delta),
                               (xr2, y1 + (r_outer + r_inner) * (N + 1) + self.d + delta))
        xr = xr2
        yr = y1 + r_outer * 2 + (2 * r_inner + self.d) * N + r_inner
        # print(l_horiz, xr1, xr2, xr, yr)
        sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta,
                             initial_angle=1.5 * np.pi if i % 2 == 1 else np.pi,
                             final_angle=2 * np.pi if i % 2 == 1 else 1.5 * np.pi, tolerance=0.01)
        result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
        xr1 = xr + r_inner - delta if i % 2 == 1 else xr - r_inner + delta
        xr2 = xr + r_outer + delta if i % 2 == 1 else xr - r_outer - delta
        rect = gdspy.Rectangle((xr1, yr), (xr2, yr + self.l_vert))
        result = gdspy.boolean(result, rect, 'or')
        if delta == 0:
            result = gdspy.boolean(result, gdspy.Rectangle((x1 + r_outer + self.l_coupl, y1), (
            x1 + r_outer + self.l_coupl + (self.d1 - self.d) / 5, y1 + self.d)),
                                   'or')  # this defines the resonator end closest to the TL
        return result, (xr2 - xr1) * 0.5 + xr1, yr + self.l_vert

    def Generate1(self, mode, r=0, w=0):
        xres = self.x1 + 0.5 * self.d2
        yres = self.y1 - self.TL_ground + self.DE + (self.d1 - self.d) / 2
        x2res = self.x1 + 2 * self.r_outer + self.l_coupl
        r1, xr1, yr1 = self.Waveguide(xres, yres, self.length, self.d)
        if mode == 'up':
            return r1
        else:
            return r1.mirror([self.x1, self.y1 - self.TL_tot / 2], [x2res, self.y1 - self.TL_tot / 2])

    def Generate2(self, mode, r=0, w=0):
        xres = self.x1 + 0.5 * self.d2
        yres = self.y1 - self.TL_ground + self.DE + (self.d1 - self.d) / 2
        x2res = self.x1 + 2 * self.r_outer + self.l_coupl
        result2, xr2, yr2 = self.Waveguide(xres, yres, self.length, self.d1)
        upperend = gdspy.Rectangle((xr2 + self.d1 / 2, yr2), (xr2 - self.d1 / 2, yr2 + 9))
        result2 = gdspy.boolean(result2, upperend, 'or')
        if mode == 'up':
            return result2
        else:
            return result2.mirror([self.x1, self.y1 - self.TL_tot / 2], [x2res, self.y1 - self.TL_tot / 2])

    def Generate3(self, mode, r=0, w=0):
        xres = self.x1 + 0.5 * self.d2
        yres = self.y1 - self.TL_ground + self.DE + (self.d1 - self.d) / 2
        x2res = self.x1 + 2 * self.r_outer + self.l_coupl
        r3, xr3, yr3 = self.Waveguide(xres, yres, self.length, self.d2)

        #		upperend = gdspy.boolean(gdspy.Rectangle((xr3 - self.d2/2, yr3+7),(xr3 +self.d2/2, yr3+14)), gdspy.boolean(gdspy.Rectangle((xr3+self.d1/2, yr3), (xr3+self.d2/2,yr3+7)), gdspy.Rectangle((xr3 - self.d2/2, yr3), (xr3 - self.d1/2, yr3+7)), 'or'), 'or')
        upperend_full = gdspy.Rectangle((xr3 - self.d2 / 2, yr3), (xr3 + self.d2 / 2, yr3 + 18))
        result3 = gdspy.boolean(r3, upperend_full, 'or')
        self.restricted_area = gdspy.boolean(r3, upperend_full, 'or')  # important for grid later on

        if mode == 'up':
            return result3
            self.restricted_area = result3
        else:
            result3.mirror([self.x1, self.y1 - self.TL_tot / 2], [x2res, self.y1 - self.TL_tot / 2])
            self.restricted_area.mirror([self.x1, self.y1 - self.TL_tot / 2], [x2res, self.y1 - self.TL_tot / 2])
            return result3
