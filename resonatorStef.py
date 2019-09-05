import gdspy
import numpy as np
from math import*
from design import*


class Resonator:
    
	def __init__(self, x1, y1, x2, frequency, layer, w, s, d2 = 66, l_vert = 0, l_coupl = 300, number = 0):
        #w and s are the characteristic widths of the resonator cavity.
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.frequency = frequency
		self.length = 299792458/(4*frequency)*1e6
		self.d = w
		self.d1 = w+s+s
		self.d2 = d2
		self.l_vert = l_vert
		self.l_coupl = self.length/36
		#self.cell = gdspy.Cell('res' + str(number))
		self.layer = layer
		self.claw_center = coordinates(0,0)
		print('length:', self.length)
		print('w=', self.d)
		print('s=', (self.d1-self.d)/2)
		print('w/s=', self.d/((self.d1-self.d)/2))
		print('w+2s=', self.d1)

	def Waveguide(self, x1, y1, x2, length, d_given):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.d*3.5  #1.5
		r_inner = self.d*2.5  #0.5
		r = 0.5*(r_outer + r_inner)
		#width = x2 - x1 - r_outer*2
		width = (self.l_coupl*(self.d1)/20) - r_outer*2
		l_reserved = self.l_vert + self.l_coupl + 0.5*np.pi*r + np.pi*r #0.5 pi for the quarter circle to the vertical piece
		N = ceil((self.length - l_reserved)/(np.pi*r + width)) #number of curves
		l_horiz = self.length - l_reserved - (np.pi*r + width)*(N-1)
		#if l_horiz > width:
		#	self.l_vert += l_horiz - 0.8*width
		#	l_horiz = 0.8*width
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
		xr1 = x1 + r_outer if i%2 == 1 else x2 - r_outer
		xr2 = x1 + r_outer + l_horiz if i%2 == 1 else x2 - r_outer - l_horiz
		rect = gdspy.Rectangle((xr1, y1 + (r_outer + r_inner)*(N+1) - delta), 
								(xr2, y1 + (r_outer + r_inner)*(N+1) + self.d + delta))
		xr = x1 + r_outer + l_horiz if i%2 == 1 else x2 - r_outer - l_horiz
		yr = y1 + r_outer*2 + (2*r_inner + self.d)*N + r_inner
		#print(l_horiz, xr1, xr2, xr, yr)
		sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 1 else np.pi, final_angle=2*np.pi if i%2 == 1 else 1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
		xr1 = xr + r_inner - delta if i%2 == 1 else xr - r_inner + delta
		xr2 = xr + r_outer + delta if i%2 == 1 else xr - r_outer - delta 
		rect = gdspy.Rectangle((xr1, yr), (xr2, yr + self.l_vert))
		result = gdspy.boolean(result, rect, 'or')
		if delta == 0:
			result = gdspy.boolean(result, gdspy.Rectangle((x1 + r_outer + self.l_coupl, y1), (x1 + r_outer + self.l_coupl + self.d, y1 + self.d)), 'or')
		return result, (xr2 - xr1)*0.5 + xr1, yr + self.l_vert


	def Generate(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 + 0.5*self.d2 - 0.5*self.d if mode == 'up' else self.y1 - 0.5*self.d2 + 0.5*self.d
		#print(yres)
		x2res = self.x2 - 0.5*self.d2
		r1, xr1, yr1 = self.Waveguide(xres, yres, x2res, self.length, self.d)
		r2, xr2, yr2 = self.Waveguide(xres, yres, x2res, self.length, self.d1)
		r3, xr3, yr3 = self.Waveguide(xres, yres, x2res, self.length, self.d2)
		print('r3: ',r3, 'xr3: ', xr3, 'yr3: ', yr3)
		self.restricted_area = r3
		print('r ', r, 'w ', w)
		res_gen = gdspy.boolean(gdspy.boolean((gdspy.boolean(r3, r2, 'not', layer = self.layer)), r1, 'or'),
								gdspy.Rectangle((xr3 - self.d/2, yr3), (xr3 + self.d/2, yr3 + 7)), 'or')
		if mode == 'up': 
			return res_gen
		else:
			self.restricted_area.rotate(np.pi, [(xres + x2res)*0.5, yres])
			return res_gen.rotate(np.pi, [(xres + x2res)*0.5, yres])
        #print(gdspy.boolean(gdspy.boolean(r3, claw, 'or'), r2, 'not', layer = self.layer))
        #resonator2.scale(1.1)
