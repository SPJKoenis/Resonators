import gdspy
import numpy as np
from resonator_coaxmon import*

class Coaxmon:
    def __init__(self, center, r1, r2, r3, R4, outer_ground, arc):
        self.center = center
        self.R1 = r1*R4
        self.R2 = r2*R4
        self.R3 = r3*R4
        self.R4 = R4
        self.freq = 7e9
        self.outer_ground = outer_ground
        self.arc = arc


    def Generate(self, mode, middle_TL):
        #resonator, center = Resonator(self.x, top_TL , self.R3, self.outer_ground, self.R4, self.freq).Generate(DE, TL_ground, d)
        ground = gdspy.Round((self.center.x,self.center.y), self.outer_ground, self.R4, initial_angle=0, final_angle=2*np.pi)
        #ground = gdspy.boolean(ground, r3, 'not') #substract incoming resonator from qubit ground

        coupler = gdspy.Round((self.center.x,self.center.y), self.R3, self.R2, initial_angle=(-self.arc-1/2)*np.pi, final_angle=(-1/2+self.arc)*np.pi)
        result = gdspy.boolean(ground, coupler, 'or')
        core = gdspy.Round((self.center.x,self.center.y), self.R1, inner_radius=0, initial_angle=0, final_angle=2*np.pi)
        result = gdspy.boolean(result, core, 'or')

        self.JJ_coordinates = coordinates(self.center.x, self.center.y + self.R1)
        self.AB1_coordinates = coordinates(self.center.x, self.center.y + self.R4)
        self.AB2_coordinates = coordinates(self.center.x, self.center.y - self.outer_ground)

        if mode == 'up':
            return result
        else:
            result.mirror([self.center.x, middle_TL], [self.center.x+100, middle_TL])
            return result


class Airbridge:
    def __init__(self, width, length, padsize, coordinate):
        self.x = coordinate.x
        self.y = coordinate.y
        self.padsize = padsize
        self.width = width
        self.length = length

    def Generate_contacts(self, layer, mode, mirror_x, mirror_y):

        #first the two contacts
        contact_1 = gdspy.Rectangle((self.x - self.length/2 - self.padsize/2, self.y), (self.x - self.length/2 + self.padsize/2, self.y + self.padsize))
        contact_2 = gdspy.Rectangle((self.x + self.length/2 - self.padsize/2, self.y), (self.x + self.length/2 + self.padsize/2, self.y + self.padsize))

        #now the bridge itself.


        result = gdspy.boolean(contact_1, contact_2, 'or', layer=layer)
        if mode == 'down':
            result.mirror([mirror_x, mirror_y], [mirror_x + 100, mirror_y])

        return result

    def Generate_bridge(self, layer, mode, mirror_x, mirror_y):
        bridge = gdspy.Rectangle((self.x - self.length/2, self.y + self.padsize/2 - self.width/2), (self.x + self.length/2, self.y + self.padsize/2 + self.width/2))
        if mode == 'down':
            bridge.mirror([mirror_x, mirror_y], [mirror_x + 100, mirror_y])
        return bridge