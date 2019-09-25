import gdspy
import numpy as np
from math import*
from designTL import*


class Pfilter:
    
	def __init__(self, x1, y1, frequency, layer, w, s, TL, l_vert=300, lc_Purcell=200):
        #w and s are the characteristic widths of the resonator cavity.

		self.frequency = frequency
		self.length = 299792458/(4*frequency)*1e6/2.5249 #the speed of light is modified in the CPW
		self.d = w
		self.d1 = w+(2*s)
		self.d2 = 3*self.d1
		self.x1 = x1
		self.y1 = y1
		self.l_coupl = self.length/15 #the ratio between the coupling length and the total resonator length is constant
		self.layer = layer
		print('coupling length:', self.l_coupl)
		print('w=', self.d)
		print('s=', (self.d1-self.d)/2)
		print('w/s=', self.d/((self.d1-self.d)/2))
		print('w+2s=', self.d1)
		self.r_outer = (self.d1*4-self.d)/2 +self.d  
#		self.width = self.l_coupl - self.r_outer - (self.d2-self.d)/2 -self.d1*2
#		print('x coordinate of end of resonator', self.x1 + 2*self.r_outer + self.width +(self.d2-self.d))
		print('...') 
		self.TL_ground = TL
		self.DE = 40 + self.d1/5 #this is the width of the conductor that separates the resonator and the TL
		self.l_vert = l_vert
		self.lc_Purcell = lc_Purcell

	def WaveguideP(self, x1, y1, length, d_given):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.r_outer 
		r_inner = (self.d1*4-self.d)/2  #Difference between the two should be self.d
		r = 0.5*(r_outer + r_inner)
#		width = self.width
		l_reserved = self.l_coupl + 0.5*np.pi*r + np.pi*r + self.l_vert + self.lc_Purcell #0.5 pi for the quarter circle to the vertical piece
#		N = floor((self.length - l_reserved)/(np.pi*r + width)) #number of curves
		N = floor((self.length - l_reserved)/(np.pi*r + self.l_coupl))
		width = (self.length - l_reserved - N*np.pi*r)/N 
		while width > self.l_coupl - self.r_outer - (self.d2-self.d)/2 -self.d1*2:
			N = N + 1
			width = (self.length - l_reserved - N*np.pi*r)/N

		rect = gdspy.Rectangle((x1 + r_outer, y1 - delta), (x1 + r_outer + self.l_coupl, y1 + self.d + delta))
		sector = gdspy.Round((x1 + r_outer, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=0.5*np.pi, final_angle=1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(rect, sector, 'or')
		sector = gdspy.Round((x1 + r_outer + self.l_coupl, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi, final_angle=2.0*np.pi, tolerance=0.01)
		result = gdspy.boolean(result, sector, 'or')
		rect = gdspy.Rectangle((x1 + r_outer + self.l_coupl + r_inner - delta, y1 + r_outer), (x1 + r_outer + self.l_coupl + r_inner +self.d + delta, y1 + r_outer + self.l_vert + delta))
		result = gdspy.boolean(result, rect, 'or')     
           
		for i in range(N):
			rect = gdspy.Rectangle((x1 + r_outer, y1 + (r_outer + r_inner)*(i+1) - delta), 
									(x1 + r_outer + width, y1 + (r_outer + r_inner)*(i+1) + self.d + delta))
			xr = x1 + width + r_outer if i%2 == 0 else x1 + r_outer
			yr = y1 + r_outer*2 + (2*r_inner + self.d)*i + r_inner
			sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 0 else 0.5*np.pi, final_angle=2.5*np.pi if i%2 == 0 else 1.5*np.pi, tolerance=0.01)
			result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
		i = N-1
		xr1 = x1 + r_outer if i%2 == 1 else x1 + width + r_outer
		if d_given == self.d1:
			xr2 = x1 + r_outer + self.lc_Purcell if i%2 == 1 else x1 + r_outer + width - self.lc_Purcell 
		else:
			xr2 = x1 + r_outer + self.lc_Purcell + delta if i%2 == 1 else x1 + r_outer + width - self.lc_Purcell - delta
		rect = gdspy.Rectangle((xr1, y1 + (r_outer + r_inner)*(N+1) - delta), 
								(xr2, y1 + (r_outer + r_inner)*(N+1) + self.d + delta))
		result = gdspy.boolean(result, rect, 'or')
		return result, x1 +r_outer, y1 + (r_outer + r_inner)*(N+1) + self.d + delta
 

	def Generate1(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 + 0.5*self.d2 - 0.5*self.d - self.TL_ground + self.DE - (self.d2-self.d1)/2 if mode == 'up' else self.y1 - 0.5*self.d2 + 0.5*self.d +self.TL_ground - self.DE + (self.d2-self.d1)/2
		#print(yres)
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r1, xr1, yr1 = self.WaveguideP(xres, yres, self.length, self.d)
		if mode == 'up': 
			return r1  
		else:
			return r1.rotate(np.pi, [(self.x1 + x2res)*0.5, yres])
    
        
	def Generate2(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 + 0.5*self.d2 - 0.5*self.d - self.TL_ground + self.DE - (self.d2-self.d1)/2 if mode == 'up' else self.y1 - 0.5*self.d2 + 0.5*self.d +self.TL_ground - self.DE + (self.d2-self.d1)/2
		#print(yres)
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r2, xr2, yr2 = self.WaveguideP(xres, yres, self.length, self.d1)  
		if mode == 'up': 
			return r2
		else:
			return r2.rotate(np.pi, [(self.x1 + x2res)*0.5, yres])
        
	def Generate3(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 + 0.5*self.d2 - 0.5*self.d - self.TL_ground + self.DE - (self.d2-self.d1)/2 if mode == 'up' else self.y1 - 0.5*self.d2 + 0.5*self.d +self.TL_ground - self.DE + (self.d2-self.d1)/2
		#print(yres)
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r3, xr3, yr3 = self.WaveguideP(xres, yres, self.length, self.d2)
		if mode == 'up':
			self.restricted_area = r3
			return r3
		else:
			r3.rotate(np.pi, [(self.x1 + x2res)*0.5, yres])
			self.restricted_area = r3
			return r3
        

