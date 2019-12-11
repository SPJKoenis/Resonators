import gdspy
import numpy as np
from math import*
from design_coaxmons import*


class Resonator:

	def __init__(self, x1, y1, R2, outer_R_ground, inner_R_ground, frequency, d, d1, d2, layer = 0, l_coupl = 420, number = 0):
		self.x1 = x1
		self.y1 = y1
		self.frequency = frequency
		self.length = 299792458/(4*frequency)*1e6/2.5249
		self.d = d
		self.d1 = d1
		self.d2 = d2
		self.l_coupl = self.length/10
		#self.cell = gdspy.Cell('res' + str(number))
		self.layer = layer
		self.claw_center = coordinates(0,0)
		self.R2 = R2
		self.outer_R_ground = outer_R_ground
		self.inner_R_ground = inner_R_ground
		self.l_vert = outer_R_ground - R2
		print('resonator length: ', self.length)

	def Waveguide(self, x1, y1, length, d_given):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.d*3.5  #1.5
		r_inner = self.d*2.5  #0.5
		r = 0.5*(r_outer + r_inner)
		width = self.outer_R_ground*2 - 2*r_outer

		l_reserved = self.l_vert + self.l_coupl + 0.5*np.pi*r + np.pi*r
		l_rest = self.length - l_reserved
		N = 0.5
		width = (l_rest - (N-0.5)*np.pi*r)/N
		while width > 2*self.outer_R_ground -6*r_outer:
			N += 1
			width = (l_rest - (N-0.5)*np.pi*r)/N
		l_horiz = 0.5*width
		x1 = x1
		x2 = x1 + width
		N = floor(N)

		rect = gdspy.Rectangle((x1 + r_outer, y1 - delta), (x1 + r_outer + self.l_coupl + delta, y1 + self.d + delta))
		sector = gdspy.Round((x1 + r_outer, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=0.5*np.pi, final_angle=1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(rect, sector, 'or')
		for i in range(N):
			rect = gdspy.Rectangle((x1 + r_outer, y1 + (r_outer + r_inner)*(i+1) - delta),
									(x1 + r_outer + width, y1 + (r_outer + r_inner)*(i+1) + self.d + delta))
			xr = x1 + r_outer + width if i%2 == 0 else x1 + r_outer
			yr = y1 + r_outer*2 + (2*r_inner + self.d)*i + r_inner
			sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 0 else 0.5*np.pi, final_angle=2.5*np.pi if i%2 == 0 else 1.5*np.pi, tolerance=0.01)
			result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
		i = N-1
		xr1 = x1 + r_outer if i%2 == 1 else x2 + r_outer
		xr2 = x1 + r_outer + l_horiz if i%2 == 1 else x2 + r_outer - l_horiz
		rect = gdspy.Rectangle((xr1, y1 + (r_outer + r_inner)*(N+1) - delta),
								(xr2, y1 + (r_outer + r_inner)*(N+1) + self.d + delta))
		xr = x1 + r_outer + l_horiz if i%2 == 1 else x2 + r_outer - l_horiz
		yr = y1 + r_outer*2 + (2*r_inner + self.d)*N + r_inner
		sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 1 else np.pi, final_angle=2*np.pi if i%2 == 1 else 1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
		xr1 = xr + r_inner - delta if i%2 == 1 else xr - r_inner + delta
		xr2 = xr + r_outer + delta if i%2 == 1 else xr - r_outer - delta
		if delta ==0:
			rect = gdspy.Rectangle((xr1, yr), (xr2, yr + self.l_vert))
		else:
			rect = gdspy.Rectangle((xr1, yr), (xr2, yr + 3 + (self.outer_R_ground - self.inner_R_ground)))
		result = gdspy.boolean(result, rect, 'or')
		if delta == 0:
			result = gdspy.boolean(result, gdspy.Rectangle((x1 + r_outer + self.l_coupl, y1), (x1 + r_outer + self.l_coupl + self.d, y1 + self.d)), 'or')
		return result, (xr2 - xr1)*0.5 + xr1, yr + self.l_vert + self.R2

	def Generate(self, DE, TL_ground, d, middle_TL, mode = 'up', circle = False):
		xres = self.x1
		yres = self.y1 - TL_ground + 0.5*(self.d1-self.d) + DE
		r, xr, yr = self.Waveguide(xres, yres, self.length, d)
		#r2, xr2, yr2 = self.Waveguide(xres, yres, self.length, self.d1)
		#r3, xr3, yr3 = self.Waveguide(xres, yres, self.length, self.d2)
		self.restricted_area = r
		#if d == self.d2:
		#	r = gdspy.boolean(r, gdspy.Rectangle((xr - self.d/2, yr), (xr + self.d/2, yr + 7)), 'or')
		#self.claw_center.x += 4
		self.center = coordinates(xr, yr)
		if mode == 'up':
			return r
		else:
			r.mirror([self.x1, middle_TL], [self.x1+100, middle_TL])
			return r