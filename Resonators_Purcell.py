import gdspy
import numpy as np
from math import*
from designTL import*


class Resonator:
    
	def __init__(self, x1, y1, frequency, layer, w, s, TL, coupling_ground, coupl_length, l_vert, frequencyP, TL_tot = 45, TL_vac=3, l_vertP=100, lc_Purcell=252, sep=12):
        #w and s are the characteristic widths of the resonator cavity. See the notebook for a more detailed explanation of the parameters

		self.frequency = frequency
		self.length = 299792458/(4*frequency)*1e6/2.5249 #the speed of light is modified in the CPW
		self.d = w
		self.d1 = w+(2*s) #the w+2s width: the width of the inner resonator conductor and the two vacuums that separate it from the outer conductor
		self.d2 = 3*self.d1 #the outer conductor is chosen to have a width of w+2s
		self.x1 = x1
		self.y1 = y1
		self.l_coupl = coupl_length #the ratio between the coupling length and the total resonator length is constant
		self.layer = layer
		self.r_outer = (self.d1*2-self.d)/2 +self.d  
		self.TL_ground = TL #this is the width of the outer conductor of the TL
		self.TL_tot = TL_tot
		self.TL_vac = TL_vac
		self.DE = 4 #this is the separation width between the central conductor of the TL and the central conductor of the bottom resonator in the coupling section. This separation width can be either drawn as a conductor or as a vacuum, depending on the parameter coupling_ground = ground/noground
		self.l_vert = l_vert #this is the open end length of the bottom resonator, measured from the end of the curve after the coupling section
		self.lc_Purcell = lc_Purcell #this is the coupling length between the bottom and top resonator
		self.sep = sep
		self.frequencyP = frequency
		self.lengthP = 299792458/(4*self.frequencyP)*1e6/2.5249 #the speed of light is modified in the CPW
		self.l_vertP = l_vertP
		self.coupling_ground = coupling_ground     
		print('total resonator length:', self.length)
		print('coupling length:', self.l_coupl)
		print('w=', self.d)
		print('s=', (self.d1-self.d)/2)
		print('w/s=', self.d/((self.d1-self.d)/2))
		print('w+2s=', self.d1)
		print('Purcell coupling length:', self.lc_Purcell)
		print('...')    

	def Waveguide(self, x1, y1, d_given):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.r_outer 
		r_inner = (self.d1*2-self.d)/2  #Difference between r_outer and r_inner should be self.d
		r = 0.5*(r_outer + r_inner)
		l_reserved = self.l_coupl +0.25*np.pi*r + np.pi*r + self.l_vert + self.lc_Purcell #0.25 pi for the quarter circle to the open end section of the resonator.
		N = ceil((self.length - l_reserved)/(np.pi*r + self.l_coupl))

		width = (self.length - l_reserved - N*np.pi*r)/N 
		while width > self.l_coupl - self.r_outer - 1*self.d1 -self.d2/2: #Makes sure that the open end and short end sections at least have some separation between them
			N = N + 1
			width = (self.length - l_reserved - N*np.pi*r)/N
		self.widthP = width #we give the top resonator the same width as the bottom one to save space
		height = (r_outer + r_inner)*N*5
		l_reservedv = height + self.TL_ground - self.DE + 100 + np.pi*r +0.25*np.pi*r #0.25 pi for 
		Nv = floor((self.l_vert - l_reservedv)/(height + np.pi*r)) #the number of curves for the open end section
		v_left = self.l_vert - l_reservedv - Nv*(height + np.pi*r)
        
		rect = gdspy.Rectangle((x1 + r_outer, y1 - delta), (x1 + r_outer + self.l_coupl, y1 + self.d + delta))
		sector = gdspy.Round((x1 + r_outer, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=0.5*np.pi, final_angle=1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(rect, sector, 'or')
		sector = gdspy.Round((x1 + r_outer + self.l_coupl, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi, final_angle=2.0*np.pi, tolerance=0.01)
		result = gdspy.boolean(result, sector, 'or')
		rect = gdspy.Rectangle((x1 + r_outer + self.l_coupl + r_inner - delta, y1 + r_outer), (x1 + r_outer + self.l_coupl + r_inner +self.d + delta, y1 + r_outer + height + self.TL_ground - self.DE + 100))
		result = gdspy.boolean(result, rect, 'or')     
        
        
		for i in range(Nv): #this loop draws the open end section of the resonator
			rect = gdspy.Rectangle((x1 + r_outer + self.l_coupl + r_inner + (r_outer + r_inner)*(i+1) - delta, y1 + r_outer +  self.TL_ground - self.DE + 100), (x1 + r_outer + self.l_coupl + r_inner +self.d + (r_outer + r_inner)*(i+1) + delta, y1 + r_outer + height + self.TL_ground - self.DE + 100))
			yr = y1 + height + r_outer + self.TL_ground - self.DE + 100 if i%2 == 0 else y1 + r_outer + self.TL_ground - self.DE + 100
			xr = x1 + r_outer*2 + (2*r_inner + self.d)*i + r_inner + self.l_coupl
			sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=2.0*np.pi if i%2 == 0 else 1.0*np.pi, final_angle=3.0*np.pi if i%2 == 0 else 2.0*np.pi, tolerance=0.01)
			result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
            
		i = Nv
		yr = y1 + height + r_outer + self.TL_ground - self.DE + 100 if i%2 == 0 else y1 + r_outer + self.TL_ground - self.DE + 100
		xr = x1 + r_outer*2 + (2*r_inner + self.d)*i + r_inner + self.l_coupl
		sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=2.0*np.pi if i%2 == 0 else 1.0*np.pi, final_angle=3.0*np.pi if i%2 == 0 else 2.0*np.pi, tolerance=0.01)
		yr1 = y1 + r_outer + self.TL_ground - self.DE + 100 if i%2 == 1 else y1 + height + r_outer + self.TL_ground - self.DE + 100
		yr2 = y1 + r_outer + self.TL_ground - self.DE + 100 + v_left + delta if i%2 == 1 else y1 + r_outer + self.TL_ground - self.DE + 100 + height - v_left - delta
		rect = gdspy.Rectangle((x1 + r_outer + self.l_coupl + r_inner + (r_outer + r_inner)*(i+1) - delta, yr1), 
								(x1 + r_outer + self.l_coupl + r_inner +self.d + (r_outer + r_inner)*(i+1) + delta, yr2))
		result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')

		for i in range(N): #This part draws the short end part of the resonator, leading to the coupling section with the other resonator
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
		if i%2 == 1: #the short end of the resonator is on the right-hand side
			R = True
			return result, xr1 - r_outer, y1 + (r_outer + r_inner)*(N+1) + self.d + (self.d2-self.d)/2, R
		else:
			R = False
			return result, x1 + width - self.lc_Purcell - (self.d2-self.d)/2, y1 + (r_outer + r_inner)*(N+1) + self.d + (self.d2-self.d)/2, R

#This part of the code describes the waveguide of the second resonator that is coupled to the first resonator (Purcell filter) and ends in a claw that can be coupled to a qubit. It differs from the first resonator (Purcell filter) in that it is mirrored, starts with a short end, doesn't have a l1 (open end) length, and ends in a claw.
	def WaveguideP(self, x1, y1, d_given, R):#, x_e, y_e):
		delta = (d_given - self.d)/2
		r_outer = self.r_outer 
		r_inner = (self.d1*2-self.d)/2
		r = 0.5*(r_outer + r_inner)
		width = self.widthP
		l_reserved = 0.5*np.pi*r + np.pi*r  + self.lc_Purcell + self.l_vertP #0.5 pi for the quarter circle to the vertical piece
		N = floor((self.lengthP - l_reserved)/(np.pi*r + width)) #number of curves
		l_hor = self.lengthP - N*(np.pi*r + width) - l_reserved
		if l_hor > width:
			self.l_vertP += l_hor - width
			l_hor = width           
		if d_given == self.d1:
			rect = gdspy.Rectangle((x1 + r_outer, y1 - delta), (x1 + r_outer + self.lc_Purcell, y1 + self.d + delta))
		else:
			rect = gdspy.Rectangle((x1 + r_outer, y1 - delta), (x1 + r_outer + self.lc_Purcell + delta, y1 + self.d + delta))
		sector = gdspy.Round((x1 + r_outer, y1 + r_outer), r_outer + delta, r_inner - delta, initial_angle=0.5*np.pi, final_angle=1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(rect, sector, 'or')
           
		for i in range(N):
			rect = gdspy.Rectangle((x1 + r_outer, y1 + (r_outer + r_inner)*(i+1) - delta), 
									(x1 + r_outer + width, y1 + (r_outer + r_inner)*(i+1) + self.d + delta))
			xr = x1 + width + r_outer if i%2 == 0 else x1 + r_outer
			yr = y1 + r_outer*2 + (2*r_inner + self.d)*i + r_inner
			sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 0 else 0.5*np.pi, final_angle=2.5*np.pi if i%2 == 0 else 1.5*np.pi, tolerance=0.01)
			result = gdspy.boolean(result, gdspy.boolean(sector, rect, 'or'), 'or')
		i = N-1
		xr1 = x1 + r_outer if i%2 == 1 else x1 + width + r_outer
		xr2 = x1 + r_outer + l_hor if i%2 == 1 else x1 + width + r_outer - l_hor 
		rect = gdspy.Rectangle((xr1, y1 + (r_outer + r_inner)*(N+1) - delta), 
								(xr2, y1 + (r_outer + r_inner)*(N+1) + self.d + delta))
		result = gdspy.boolean(result, rect, 'or')
		xr = xr2
		yr = y1 + r_outer*2 + (2*r_inner + self.d)*N + r_inner
		sector = gdspy.Round((xr, yr), r_outer + delta, r_inner - delta, initial_angle=1.5*np.pi if i%2 == 1 else np.pi, final_angle=2*np.pi if i%2 == 1 else 1.5*np.pi, tolerance=0.01)
		result = gdspy.boolean(sector, result, 'or')
		xr1 = xr + r_inner - delta if i%2 == 1 else xr - r_inner + delta
		xr2 = xr + r_outer + delta if i%2 == 1 else xr - r_outer - delta 
		if d_given == self.d:
			rect = gdspy.Rectangle((xr1, yr), (xr2, yr + self.l_vertP + delta)) #+4
		else:
			rect = gdspy.Rectangle((xr1, yr), (xr2, yr + self.l_vertP + delta)) #+delta was added
		result = gdspy.boolean(result, rect, 'or')        
#		if d_given == self.d2:
#			if R == True:
#				claw = self.Claw((xr2 - xr1)*0.5 + xr1, yr + self.l_vertP)
#				result = gdspy.boolean(result, claw, 'or')  
#			else:
#				claw = self.Claw((xr1 - xr2)*0.5 + xr2, yr + self.l_vertP)
#				result = gdspy.boolean(result, claw, 'or') 
       
		if R == True:
			return result
		else:
			result.mirror(((x1*2 + r_outer*2 + self.lc_Purcell + (self.d2-self.d)/2)/2, -10000), ((x1*2 + r_outer*2 + self.lc_Purcell + (self.d2-self.d)/2)/2, 10000))
			return result            
        
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
		self.restricted_area = gdspy.Rectangle((xc - 250, yc - 4*gap), (xc + 250, yc + 284)) #r3
		result_claw = gdspy.boolean(gdspy.boolean(gdspy.boolean(gdspy.boolean(r3, r1, 'not'), 
							gdspy.Rectangle((xc - w/2 + d2 + 2*gap, yc + d1 + 3*gap), (xc + w/2 - d2 - 2*gap, yc + h + 4*gap)), 'not'),
							r2, 'or'), self.Qubit_Inner_Cross(xc - w/2 + d2 + 2*gap + 16, yc + d1 + 3*gap + vertical_constant/2 + 32 + 0.25*h, 414, vertical_constant, 16, 0), 'or')

		return result_claw       

	def Qubit_Outer_Cross(self, x1, y1, width, height, thickness, gap):
		return gdspy.boolean(self.Qubit_Inner_Cross(x1, y1 + height/2 + gap, width, height, thickness, 2*gap),
		self.Qubit_Inner_Cross(x1, y1 + height/2 + gap, width, height, thickness, gap), 'not')

	def Qubit_Inner_Cross(self, x1, y1, width, height, thickness, gap):
		return gdspy.boolean(gdspy.Rectangle((x1 - gap, y1 - height*0.75 - gap), (x1 + thickness + gap, y1 + height*0.25 + gap)),  #gdspy.boolean(gdspy.Rectangle((x1 - gap, y1 - height*0.75 - gap), (x1 + thikness + gap, y1 + height*0.25 + gap)), 
							gdspy.Rectangle((x1 - width/2 + thickness/2 - gap, y1 - gap), (x1 + width/2 + thickness/2 + gap, y1 + thickness + gap)), 'or') 
  
	def Generate1(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 - self.TL_ground - self.TL_vac + self.DE 
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r1, xr1, yr1, R = self.Waveguide(xres, yres , self.d)
		r1P = self.WaveguideP(xr1, yr1 - (self.d2-self.d)/2 + self.sep, self.d, R)
		result1 = gdspy.boolean(r1, r1P, 'or')        
		if mode == 'up': 
			return result1  
		else:
			return result1.mirror([self.x1, self.y1 - self.TL_tot/2], [x2res, self.y1 - self.TL_tot/2])
    
        
	def Generate2(self, mode = 'up', r = 0, w = 0):
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 - self.TL_ground - self.TL_vac + self.DE 
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r2, xr2, yr2, R = self.Waveguide(xres, yres, self.d1)
		r2P = self.WaveguideP(xr2, yr2 - (self.d2-self.d)/2 + self.sep, self.d1, R)
		result2 = gdspy.boolean(r2, r2P, 'or')
		if self.coupling_ground == 'noground':
			rect = gdspy.Rectangle((xres + self.r_outer, self.y1 - self.TL_ground), (xres + self.r_outer + self.l_coupl, self.y1 - self.TL_ground + self.DE))
			result2 = gdspy.boolean(result2, rect, 'or')            
		if mode == 'up': 
			return result2
		else:
			return result2.mirror([self.x1, self.y1 - self.TL_tot/2], [x2res, self.y1 - self.TL_tot/2])
        
	def Generate3(self, mode = 'up', r = 0, w = 0): 
		xres = self.x1 + 0.5*self.d2
		yres = self.y1 - self.TL_ground - self.TL_vac + self.DE 
		x2res = self.x1 + 2*self.r_outer + self.l_coupl
		r3, xr3, yr3, R = self.Waveguide(xres, yres, self.d2)
		r3P = self.WaveguideP(xr3, yr3 - (self.d2-self.d)/2 + self.sep, self.d2, R)
		result3 = gdspy.boolean(r3, r3P, 'or')   
#		self.restricted_area = gdspy.boolean(self.restricted_area, result3, 'or')    
		self.restricted_area = result3     
		if mode == 'up':
			return result3
			self.restricted_area = result3    
		else:
			result3.mirror([self.x1, self.y1 - self.TL_tot/2], [x2res, self.y1 - self.TL_tot/2])
#			self.restricted_area.rotate(np.pi, [(self.x1 + x2res)*0.5, yres])
			self.restricted_area = result3
			return result3
 
        

