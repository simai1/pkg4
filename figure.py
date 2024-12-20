from algorithms import *
from config import *
import pygame
import sys
import math
from config import *
class Layer:

    def __init__(self, pixel_map, p1, p2, p3, center, radius, new_color, outline_color,visible = True):
        self.pixel_map = pixel_map
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.center = center
        self.radius = radius
        self.new_color = new_color
        self.outline_color = outline_color
        self.visible = visible

    def draw(self):
        if self.visible:
            # draw_triangle(self.pixel_map, self.p1,self.p2,self.p3)
            draw_triangle_hodjman(self.pixel_map, self.p1,self.p2,self.p3)
            algorithm_A_fill(self.pixel_map, self.center, self.radius, self.new_color, self.outline_color)
        