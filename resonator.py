import gdspy
import numpy as np
from math import*
from design import*


class Resonator:
    
	def __init__(self, x1, y1, x2, frequency, layer, d = 10, d1 = 22, d2 = 66, l_vert = 160, l_coupl = 420, number = 0):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.frequency = frequency
		self.length = 299792458/(4*frequency)*1e6
		print(self.length)
		self.d = d
		self.d1 = d1
		self.d2 = d2
		self.l_vert = l_vert
		self.l_coupl = l_coupl
		#self.cell = gdspy.Cell('res' + str(number))
		self.layer = layer
		self.claw_center = coordinates(0,0)

	def Waveguide(self, x1, y1, x2, length, d_given):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.d*3.5  #1.5
		r_inner = self.d*2.5  #0.5
		r = 0.5*(r_outer + r_inner)
		width = x2 - x1 - r_outer*2
		l_reserved = self.l_vert + self.l_coupl + 0.5*np.pi*r + np.pi*r
		N = floor((self.length - l_reserved)/(np.pi*r + width))
		l_horiz = self.length - l_reserved - (np.pi*r + width)*N
		if l_horiz > width:
			self.l_vert += l_horiz - 0.8*width
			l_horiz = 0.8*width
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

	def Qubit_Outer_Cross(self, x1, y1, width, height, thikness, gap):
		return gdspy.boolean(self.Qubit_Inner_Cross(x1, y1 + height/2 + gap, width, height, thikness, 2*gap),
		self.Qubit_Inner_Cross(x1, y1 + height/2 + gap, width, height, thikness, gap), 'not')

	def Qubit_Inner_Cross(self, x1, y1, width, height, thikness, gap):
		return gdspy.boolean(gdspy.Rectangle((x1 - gap, y1 - height*0.75 - gap), (x1 + thikness + gap, y1 + height*0.25 + gap)),  #gdspy.boolean(gdspy.Rectangle((x1 - gap, y1 - height*0.75 - gap), (x1 + thikness + gap, y1 + height*0.25 + gap)), 
							gdspy.Rectangle((x1 - width/2 + thikness/2 - gap, y1 - gap), (x1 + width/2 + thikness/2 + gap, y1 + thikness + gap)), 'or') 

	def Claw(self, xc, yc, w = 104, d1 = 7, h = 107, d2 = 20, gap = 4):
		vertical_constant = 176 #it was 176
		r1 = gdspy.boolean(gdspy.boolean(gdspy.Rectangle((xc - w/2 - gap, yc), (xc + w/2 + gap, yc + d1 + 2*gap)),
							gdspy.Rectangle((xc - w/2 - gap, yc), (xc - w/2 + d2 + gap, yc + h + 2*gap)), 'or'), 
							gdspy.Rectangle((xc + w/2 - d2 - gap, yc), (xc + w/2 + gap, yc + h + 2*gap)), 'or')
		r2 = gdspy.boolean(gdspy.boolean(gdspy.Rectangle((xc - w/2, yc + gap), (xc + w/2, yc + d1 + gap)),
							gdspy.Rectangle((xc - w/2, yc + gap), (xc - w/2 + d2, yc + h + gap)), 'or'), 
							gdspy.Rectangle((xc + w/2 - d2, yc + gap), (xc + w/2, yc + h + gap)), 'or')
		r3 = gdspy.boolean(gdspy.Rectangle((xc - w/2 - 4*gap, yc - 4*gap), (xc + w/2 + 4*gap, yc + h + 4*gap)), 
							self.Qubit_Outer_Cross(xc - w/2 + d2 + 2*gap + 16, yc + d1 + 3*gap + 16 + 0.25*h, 414, vertical_constant, 16, 16), 'or')
		self.claw_center = coordinates(xc, yc + vertical_constant + 3*gap + d1 + 16*3) #coordinates(xc - w/2 + d2 + 2*gap + 20, yc + vertical_constant + 3*gap + d1 + 16*3)
		self.restricted_area = gdspy.boolean(self.restricted_area, gdspy.Rectangle((xc - 250, yc - 4*gap), (xc + 250, yc + 284)), 'or') #r3
		return gdspy.boolean(gdspy.boolean(gdspy.boolean(gdspy.boolean(r3, r1, 'not'), 
							gdspy.Rectangle((xc - w/2 + d2 + 2*gap, yc + d1 + 3*gap), (xc + w/2 - d2 - 2*gap, yc + h + 4*gap)), 'not'),
							r2, 'or'), self.Qubit_Inner_Cross(xc - w/2 + d2 + 2*gap + 16, yc + d1 + 3*gap + vertical_constant/2 + 32 + 0.25*h, 414, vertical_constant, 16, 0), 'or')
							
	def Circular_Claw(self, xc, yc):
		r2 = 140
		r1 = 140 - 9
		angle = rotations(5*np.pi/4, 7*np.pi/4)
		c1 = gdspy.boolean(gdspy.Round((xc, yc + r2 + 40), r2 + 16, inner_radius = r2, initial_angle = 0.53*np.pi, final_angle = 2.5*np.pi, tolerance=0.01), 
							gdspy.Round((xc, yc + r2 + 40), r1), 'or')
		c2 = gdspy.boolean(gdspy.Round((xc, yc + r2 + 40), r2 + 44, inner_radius = r2 + 16, initial_angle = angle.phi1 - 0.04*np.pi, final_angle = angle.phi2 + 0.04*np.pi, tolerance=0.01), 
							gdspy.Round((xc, yc + r2 + 40), r2 + 40, inner_radius = r2 + 16, initial_angle = angle.phi1 - 0.01*np.pi, final_angle = angle.phi2 + 0.01*np.pi, tolerance=0.01), 'not')
		c2 = gdspy.boolean(gdspy.boolean(c2, gdspy.Rectangle((xc - self.d/2, yc + 1), (xc - self.d1/2, yc -10)), 'not'), gdspy.Rectangle((xc + self.d/2, yc + 1), (xc + self.d1/2, yc -10)), 'not')
		self.claw_center = coordinates(xc, yc + r1 + r2 + 40)
		self.restricted_area = gdspy.boolean(self.restricted_area, gdspy.boolean(gdspy.Round((xc, yc + r2 + 40), r2 + 16), 
											gdspy.Round((xc, yc + r2 + 40), r2 + 44, inner_radius = r2, initial_angle = angle.phi1 - 0.04*np.pi, final_angle = angle.phi2 + 0.04*np.pi, tolerance=0.01), 'or'), 'or')
		return gdspy.boolean(gdspy.Round((xc, yc + r2 + 40), r2 + 36, inner_radius = r2 + 20, initial_angle = angle.phi1, final_angle = angle.phi2, tolerance=0.01), gdspy.boolean(c1, c2, 'or'), 'or')
		
	def Circular_Claw2(self, xc, yc, r, w, t = 16, t_coupl = 4):
		r2 = r + w
		r1 = r
		d = 10
		d1 = 22
		print('xc',xc,'yc', yc,'r', r,'w', w,'r2', r2,'t', t)
		angle = rotations(5*np.pi/4, 7*np.pi/4)
		c1 = gdspy.boolean(gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t, inner_radius = r2, #initial_angle = 0.54*np.pi, #final_angle = 2.47*np.pi, 
										tolerance = 0.01), #number_of_points = 120), 
							gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r1, tolerance = 0.01), 'or') #number_of_points = 120), 'or')
		c2 = gdspy.boolean(gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t + t_coupl*2 + 16 + 4, 
										inner_radius = r2 + t - 5, 
										initial_angle = angle.phi1 - 0.04*np.pi, 
										final_angle = angle.phi2 + 0.04*np.pi, 
										tolerance = 0.01), #number_of_points = 120), 
							gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t + t_coupl*2 + 16, inner_radius = r2,# + 16, 
										initial_angle = angle.phi1 - 0.01*np.pi, 
										final_angle = angle.phi2 + 0.01*np.pi, 
										tolerance = 0.01), 'not') #number_of_points = 120), 'not')
		c2 = gdspy.boolean(gdspy.boolean(c2, gdspy.Rectangle((xc - d/2, yc + 1), (xc - d1/2, yc -10)), 'not'), 
							gdspy.Rectangle((xc + d/2, yc + 1), (xc + d1/2, yc -10)), 'not')
		self.claw_center = coordinates(xc, yc + r1 + r2 + t + t_coupl*2 + 16)
		self.restricted_area = gdspy.boolean(self.restricted_area, gdspy.boolean(gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t, tolerance = 0.01), #number_of_points = 120), 
																				gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t + t_coupl*2 + 16 + 4, 
																				initial_angle = angle.phi1 - 0.04*np.pi, 
																				final_angle = angle.phi2 + 0.04*np.pi, 
																				tolerance = 0.01), 'or'), 'or') #number_of_points = 120), 'or'), 'or')
		#return c2, claw_center
		res = gdspy.boolean(gdspy.Round((xc, yc + r2 + t + t_coupl*2 + 16), r2 + t + t_coupl + 16, 
										inner_radius = r2 + t + t_coupl, 
										initial_angle = angle.phi1, 
										final_angle = angle.phi2, tolerance = 0.01), #number_of_points = 120), 
							gdspy.boolean(c1, c2, 'or'), 'or')
		return gdspy.boolean(res, gdspy.Rectangle((xc - d/2, yc), (xc + d/2, yc + 5)), 'or')#, claw_center


	def Generate(self, mode = 'up', circle = False, r = 0, w = 0):
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
		if circle:
			claw = self.Circular_Claw2(xr3, yr3, r, w) #claw = self.Circular_Claw(xr3, yr3)
		else:
			claw = self.Claw(xr3, yr3)
        #cell.add(claw)
		res_gen = gdspy.boolean(gdspy.boolean((gdspy.boolean(gdspy.boolean(r3, claw, 'or'), r2, 'not', layer = self.layer)), r1, 'or'),
								gdspy.Rectangle((xr3 - self.d/2, yr3), (xr3 + self.d/2, yr3 + 7)), 'or')
		if mode == 'up': 
			#self.claw_center.x += 4
			return res_gen
		else:
			#print(self.claw_center.x, (xres + x2res)*0.5)
			self.claw_center.y -= 2*np.abs(self.claw_center.y - yres)
			self.claw_center.x += 2*np.abs(self.claw_center.x - (xres + x2res)*0.5)
			#print(self.claw_center)
			self.restricted_area.rotate(np.pi, [(xres + x2res)*0.5, yres])
			#self.claw_center.x -= 20
			return res_gen.rotate(np.pi, [(xres + x2res)*0.5, yres])
        #print(gdspy.boolean(gdspy.boolean(r3, claw, 'or'), r2, 'not', layer = self.layer))
        #resonator2.scale(1.1)
