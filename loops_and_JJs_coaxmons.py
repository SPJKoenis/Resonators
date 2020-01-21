import gdspy
import numpy as np
from math import*
from design_coaxmons import*

class JJ:
	def __init__(self, a, b, c, d, w1, w2, layer, h1=6, h2=10, sep = 0.5):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.h1 = h1
		self.h2 = h2
		self.w1 = w1
		self.w2 = w2
		self.layer = layer
		self.sep = sep

	def Generate(self, x, y, mode, mirror_x, mirror_y):
		lower_part = gdspy.boolean(gdspy.Rectangle((x - self.w2/2, y -3), (x + self.w2/2, y + 1)), # there is 2 micron overlap between the junction and the qubit core
									gdspy.boolean(gdspy.Rectangle((x - self.w2/2, y + 1), (x - self.w2/2 + self.c, y + self.h1)),
												gdspy.Rectangle((x + self.w2/2, y + 1), (x + self.w2/2 - self.d, y + self.h1)), 'or'), 'or')
		#lower_part = gdspy.boolean(gdspy.boolean(lower_part,
									#dspy.Rectangle((x + 2 - self.a, y + 5), (x + 2, y + 5 + self.b)), 'or'),
									#gdspy.Rectangle((x + 6 + self.c, y + 5), (x + 6, y + 5 + self.d)), 'or')
		height = self.h1 + self.h2 + self.sep
		upper_part = gdspy.boolean(gdspy.Rectangle((x - self.w1/2-0.1, y + height), (x - self.w1/2 + 4.1, y + height +3)),gdspy.Rectangle((x + self.w1/2-4.1, y + height), (x + self.w1/2+0.1, y + height + 3)), 'or')
		upper_part = gdspy.boolean(upper_part, gdspy.boolean(gdspy.Rectangle((x - self.w1/2, y + height - 4), (x - self.w1/2 + 1, y + height)),gdspy.Rectangle((x + self.w1/2-1, y + height - 4.5), (x + self.w1/2, y + height)), 'or'), 'or')
		upper_part = gdspy.boolean(upper_part, gdspy.boolean(gdspy.Rectangle((x - self.w1/2, y + height - 4), (x + self.w1/2, y + height - 4.5)),
									gdspy.boolean(gdspy.Rectangle((x - self.w1/2, y + height - 1), (x - self.w1/2 + 1, y + self.h1 + self.sep)),
													gdspy.Rectangle((x + self.w1/2, y + height - 1), (x + self.w1/2 - 1, y + self.h1 + self.sep)), 'or'), 'or'), 'or')
		upper_part = gdspy.boolean(gdspy.boolean(upper_part,
												gdspy.Rectangle((x - self.w1/2, y + self.h1 + self.sep), (x - 2, y + self.h1 + self.sep + self.a)), 'or'), #(x + 2.8 - self.w1/2, y + int(self.h/2) + self.a)), 'or'),
									gdspy.Rectangle((x + self.w1/2, y + self.h1 + self.sep), (x + 2, y + self.h1 + self.sep + self.b)), 'or') #(x + self.w1/2 - 2.8, y + int(self.h/2) + self.b)), 'or')
		self.ref_x = x -0.5
		self.ref_y = y + height
		self.height = height
		res = gdspy.boolean(upper_part, lower_part, 'or', layer = self.layer)
		if mode == 'down':
			res.mirror([mirror_x, mirror_y], [mirror_x + 100, mirror_y])
			self.ref_y = mirror_y - (y+height - mirror_y)
			self.ref_x = x +0.5

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

	def Generate(self, coords, R, mode = 'up'):
		end = gdspy.boolean(gdspy.boolean(gdspy.Rectangle((self.x2, self.y2), (self.x2 + self.d2/2, self.y2 - R)),
										gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d1), self.y2), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - R)), 'not'),
							gdspy.Rectangle((self.x2 + 0.5*(self.d2 - self.d), self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - R)), 'or')
		#end = gdspy.boolean(end, gdspy.Rectangle((self.x2, self.y2), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - 5.5)), 'or')
		trans = gdspy.boolean(gdspy.Polygon([(self.x2, self.y2 - R), (self.x2 + self.d2, self.y2 - R),
											(self.x2 + 0.5*(self.d2_tl + self.d2), self.y2 - R - 50), (self.x2 - 0.5*(self.d2_tl - self.d2), self.y2 - R - 50)]),
							gdspy.Polygon([(self.x2 + 0.5*(self.d2 - self.d1), self.y2 - R), (self.x2 + 0.5*(self.d2 + self.d1), self.y2 - R),
											(self.x2 + 0.5*(self.d2_tl + self.d2) - 0.5*(self.d2_tl - self.d1_tl), self.y2 - R - 50),
											(self.x2 - 0.5*(self.d2_tl - self.d2) + 0.5*(self.d2_tl - self.d1_tl), self.y2 - R - 50)]), 'not')
		trans = gdspy.boolean(trans, gdspy.Polygon([(self.x2 + 0.5*(self.d2 - self.d), self.y2 - R), (self.x2 + 0.5*(self.d2 + self.d), self.y2 - R),
									(self.x2 + 0.5*(self.d2_tl + self.d_tl) - 0.5*(self.d2_tl - self.d2), self.y2 - R - 50), (self.x2 + 0.5*(self.d2_tl - self.d_tl) - 0.5*(self.d2_tl - self.d2), self.y2 - R - 50)]), 'or')
		self.restricted_area = gdspy.boolean(gdspy.Rectangle((self.x2, self.y2), (self.x2 + self.d2, self.y2 - R)),
											gdspy.Polygon([(self.x2, self.y2 - R), (self.x2 + self.d2, self.y2 - R),
											(self.x2 + 0.5*(self.d2_tl + self.d2), self.y2 - R - 50), (self.x2 - 0.5*(self.d2_tl - self.d2), self.y2 - R - 50)]), 'or')
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
			if self.start_points.y < 2500:
				rots = [rotations(np.pi, np.pi/2), rotations(3*np.pi/2, 2*np.pi)]
			else:
				rots = [rotations(1*np.pi, (1+1/2)*np.pi), rotations(1*np.pi/2, 0)]
		else:
			self.start_points.x += 0.5*(self.d2_tl - self.d_tl)
			coords = [ref] + coords
			coords.append(self.start_points)
			if self.start_points.y < 2500:
				rots = [rotations(1*np.pi, (1+1/2)*np.pi), rotations(1*np.pi/2, 0)]
			else:
				rots = [rotations(np.pi, np.pi/2), rotations(3*np.pi/2, 2*np.pi)]
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
