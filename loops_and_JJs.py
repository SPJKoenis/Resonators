import gdspy
import numpy as np
from math import*
from design import*

class JJ:
	def __init__(self, a, b, c, d, h, w1, w2, layer):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.h = h 
		self.w1 = w1
		self.w2 = w2
		self.layer = layer 
        
	def Generate(self, x, y, mode = 'up'):
		#x = x + 4
		lower_part = gdspy.boolean(gdspy.Rectangle((x - self.w2/2, y - 2), (x + self.w2/2, y + 1)), 
									gdspy.boolean(gdspy.Rectangle((x - self.w2/2, y + 1), (x - self.w2/2 + self.c, y + int(self.h/2) - 0.16)), 
												gdspy.Rectangle((x + self.w2/2, y + 1), (x + self.w2/2 - self.d, y + int(self.h/2) - 0.16)), 'or'), 'or')
		#lower_part = gdspy.boolean(gdspy.boolean(lower_part, 
									#dspy.Rectangle((x + 2 - self.a, y + 5), (x + 2, y + 5 + self.b)), 'or'),
									#gdspy.Rectangle((x + 6 + self.c, y + 5), (x + 6, y + 5 + self.d)), 'or')
		upper_part = gdspy.boolean(gdspy.Rectangle((x - self.w1/2, y + self.h - 1), (x + self.w1/2, y + self.h + 2)), 
									gdspy.boolean(gdspy.Rectangle((x - self.w1/2, y + self.h - 1), (x - self.w1/2 + 0.5, y + int(self.h/2))), 
													gdspy.Rectangle((x + self.w1/2, y + self.h - 1), (x + self.w1/2 - 0.5, y + int(self.h/2))), 'or'), 'or')
		upper_part = gdspy.boolean(gdspy.boolean(upper_part, 
												gdspy.Rectangle((x - self.w1/2, y + int(self.h/2)), (x - 0.5, y + int(self.h/2) + self.a)), 'or'), #(x + 2.8 - self.w1/2, y + int(self.h/2) + self.a)), 'or'),
									gdspy.Rectangle((x + self.w1/2, y + int(self.h/2)), (x + 0.5, y + int(self.h/2) + self.b)), 'or') #(x + self.w1/2 - 2.8, y + int(self.h/2) + self.b)), 'or')
		self.ref_x = x
		self.ref_y = y + self.h
		res = gdspy.boolean(upper_part, lower_part, 'or', layer = self.layer)
		if mode == 'down':
			res.rotate(-np.pi, (x, y))
			self.ref_y = y - self.h 
		return res


class Loop:
    
	def __init__(self, x2, y2, d, d1, d2, d_tl, d1_tl, d2_tl, mode, start_points, layer):
		self.x2 = x2 - 0.5*(d2 + d) if mode == 'up' else x2 - 0.5*(d2 - d)
		self.y2 = y2
		self.d = d
		self.d1 = d1
		self.d2 = d2
		self.d_tl = d_tl
		self.d1_tl = d1_tl
		self.d2_tl = d2_tl
		self.layer = layer
		self.mode = mode
		self.start_points = start_points
        
	def Generate(self, coords, rots, mode = 'up'):
		end = gdspy.boolean(gdspy.boolean(gdspy.Rectangle((self.x2, self.y2), (self.x2 + self.d2, self.y2 - 150)),
										gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d1), self.y2), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - 150)), 'not'),
							gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d), self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 150)), 'or')
		end = gdspy.boolean(end, gdspy.Rectangle((self.x2, self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 5.5)), 'or')
		trans = gdspy.boolean(gdspy.Polygon([(self.x2, self.y2 - 150), (self.x2 + self.d2, self.y2 - 150),
											(self.x2 + 0.5*(self.d2_tl + self.d2), self.y2 - 200), (self.x2 - 0.5*(self.d2_tl - self.d2), self.y2 - 200)]),
							gdspy.Polygon([(self.x2 + 0.5*(self.d2 - self.d1), self.y2 - 150), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - 150),
											(self.x2 + 0.5*(self.d2_tl + self.d2) - 0.5*(self.d2_tl - self.d1_tl), self.y2 - 200), 
											(self.x2 - 0.5*(self.d2_tl - self.d2) + 0.5*(self.d2_tl - self.d1_tl), self.y2 - 200)]), 'not')
		trans = gdspy.boolean(trans, gdspy.Polygon([(self.x2 + 0.5*(self.d2 - self.d), self.y2 - 150), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 150),
									(self.x2 + 0.5*(self.d2_tl + self.d_tl) - 0.5*(self.d2_tl - self.d2), self.y2 - 200), (self.x2 + 0.5*(self.d2_tl - self.d_tl) - 0.5*(self.d2_tl - self.d2), self.y2 - 200)]), 'or')
		self.restricted_area = gdspy.boolean(gdspy.Rectangle((self.x2, self.y2), (self.x2 + self.d2, self.y2 - 150)),
											gdspy.Polygon([(self.x2, self.y2 - 150), (self.x2 + self.d2, self.y2 - 150),
											(self.x2 + 0.5*(self.d2_tl + self.d2), self.y2 - 200), (self.x2 - 0.5*(self.d2_tl - self.d2), self.y2 - 200)]), 'or')
		self.restricted_area = gdspy.boolean(gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d1), self.y2 + 3), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - 50)), self.restricted_area, 'or')	   
		if self.mode != 'up': 
			res = gdspy.boolean(end, trans, 'or', layer = self.layer).rotate(np.pi, (self.x2 + 0.5*self.d2, self.y2))
			self.restricted_area.rotate(np.pi, (self.x2 + 0.5*self.d2, self.y2))
			ref = coordinates(res.get_bounding_box()[0, 0] + 0.5*(self.d2_tl - self.d_tl), res.get_bounding_box()[1, 1])
		else:
			res = gdspy.boolean(end, trans, 'or', layer = self.layer)
			ref = coordinates(res.get_bounding_box()[0, 0] + 0.5*(self.d2_tl - self.d_tl), res.get_bounding_box()[0, 1])
		#print(self.start_points, ref)
		if self.start_points.x < ref.x:
			coords = [coordinates(self.start_points.x + 0.5*(self.d2_tl - self.d_tl), self.start_points.y)] + coords
			coords.append(ref)
		else:
			self.start_points.x += 0.5*(self.d2_tl - self.d_tl)
			coords = [ref] + coords
			coords.append(self.start_points)
		coords[1].x = coords[0].x
		coords[len(coords) - 2].x = coords[len(coords) - 1].x
		print(type(coords), coords)
		print(type(res))
		self.restricted_area = gdspy.boolean(Line_With_Turns(coords, rots, self.d_tl, self.d2_tl, start = 'vertical', right = True), self.restricted_area, 'or')
		return gdspy.boolean(res, gdspy.boolean(gdspy.boolean(Line_With_Turns(coords, rots, self.d_tl, self.d2_tl, start = 'vertical', right = True), 
                                           Line_With_Turns(coords, rots, self.d_tl, self.d1_tl, start = 'vertical', right = True), 'not'),
                             Line_With_Turns(coords, rots, self.d_tl, self.d_tl, start = 'vertical', right = True), 'or'), 'or',
                             layer = self.layer)
        


#class Loop:
    
	#def __init__(self, x2, y2, d, d1, d2, d_tl, d1_tl, d2_tl, layer):
		#self.x2 = x2 - 0.5*(d2 - d)
		#self.y2 = y2
		#self.d = d
		#self.d1 = d1
		#self.d2 = d2
		#self.d_tl = d_tl
		#self.d1_tl = d1_tl
		#self.d2_tl = d2_tl
		#self.layer = layer
        
	#def Generate(self, mode = 'up'):
		#end = gdspy.boolean(gdspy.boolean(gdspy.Rectangle((self.x2, self.y2), (self.x2 + self.d2, self.y2 - 150)),
										  #gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d1), self.y2), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - 150)), 'not'),
							#gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d), self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 150)), 'or')
		#end = gdspy.boolean(end, gdspy.Rectangle((self.x2, self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 5.5)), 'or')
		#self.restricted_area = gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d1), self.y2 + 3), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - 50)) 
		#if mode == 'up':
			#end.rotate(np.pi, (self.x2 + 0.5*self.d2, self.y2))
			#self.restricted_area.rotate(np.pi, (self.x2 + 0.5*self.d2, self.y2))
		#return end
        