from math import cos as cos
from math import sin as sin
from math import pi as PI

from OpenGL.GL import *


class Constraint:
    def __init__(self, id1, id2, distance):
        self.id1 = id1
        self.id2 = id2
        self.distance = distance
        self.stiffness = 0.1


class Particle:
    def __init__(self, x, y, particle_radii=0.1):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.px = x
        self.py = y
        self.r = particle_radii
        self.inv_mass = 1.0

    def draw(self):
        i = 0.0
        glLineWidth(1)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.x, self.y)
        while i <= 360.0:
            glVertex2f(
                self.r * cos(PI * i / 180.0) + self.x,
                self.r * sin(PI * i / 180.0) + self.y,
            )
            i += 360.0 / 18.0
        glEnd()
