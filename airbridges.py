import gdspy
import numpy as np

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
        bridge = gdspy.Rectangle((self.x - self.length/2, self.y + self.padsize/2 - self.width/2), (self.x + self.length/2, self.y + self.padsize/2 + self.width/2), layer=layer)
        if mode == 'down':
            bridge.mirror([mirror_x, mirror_y], [mirror_x + 100, mirror_y])
        return bridge


class Airbridge_TL:
    def __init__(self, x, y, width, length, padsize):
        self.x = x
        self.y = y
        self.padsize = padsize
        self.width = width
        self.length = length

    def Generate_contacts(self, layer):

        #first the two contacts
        contact_1 = gdspy.Rectangle((self.x, self.y - self.length/2 - self.padsize/2), (self.x + self.padsize, self.y - self.length/2 + self.padsize/2))
        contact_2 = gdspy.Rectangle((self.x, self.y + self.length/2 - self.padsize/2), (self.x + self.padsize, self.y + self.length/2 + self.padsize/2))

        #now the bridge itself.


        result = gdspy.boolean(contact_1, contact_2, 'or', layer=layer)

        return result

    def Generate_bridge(self, layer):
        bridge = gdspy.Rectangle((self.x + self.padsize/2 - self.width/2, self.y - self.length/2), (self.x + self.padsize/2 + self.width/2, self.y + self.length/2), layer=layer)

        return bridge