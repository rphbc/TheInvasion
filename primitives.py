import pyglet
import math
import numpy as np
from scipy.spatial.transform import Rotation as Rot
from random import randint
from constants import *


class Vector:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self._v = [x, y]

    def __add__(self, vector):
        if isinstance(vector, Vector):
            return Vector(vector.x + self.x, vector.y + self.y)
        return TypeError("Arguments must be Vectors")

    def __sub__(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return 'Vector(x=%s, y=%s)' % (self.x, self.y)

    def __str__(self):
        return 'Vector(x=%s, y=%s)' % (self.x, self.y)

    # def __call__(self, key):
    #     return self._v[key]

    def __getitem__(self, index):
        return self._v[index]

    def __setitem__(self, index, value):
        self._v[index] = value

    @property
    def length(self):
        return math.hypot(self.x, self.y)

    @property
    def length_sqr(self):
        return self.x * self.x + self.y * self.y

    # @property
    # def x(self):
    #     return self._v[0]
    #
    # @property
    # def y(self):
    #     return self._v[1]

    @property
    def angle(self):
        if self.length == 0:
            return 0
        else:
            return round(math.degrees(math.atan2(self.y, self.x)), 2)

    def normalized(self):
        return Vector(self.x / self.length, self.y / self.length)


class Point:
    def __init__(self, x, y, color=(255, 255, 255), random=False):
        if random:
            self.x, self.y = randint(100, WIDTH-100), randint(100, HEIGHT-100)
        else:
            self.x = x
            self.y = y
        self.vertex = [self.x, self.y]
        self.color = color
        self.object = None
        self.vertices = pyglet.graphics.vertex_list(1,
                                                    ('v2i', self.vertex),
                                                    ('c3B', self.color),
                                                    )

    @property
    def vertex_list(self):
        return 1, pyglet.graphics.GL_POINTS, None, ('v2i', self.vertex), \
               ('c3B', self.color)


class Triangle:
    def __init__(self, x=0, y=0, size=10, color=(255, 0, 0) * 3, random=False):
        if random:
            self.x, self.y = randint(100, WIDTH-100), randint(100, HEIGHT-100)
        else:
            self.x = x
            self.y = y
        self.rotated = 0
        self.centroid = [x, y]
        self.size = size
        self.v1 = [0, 0, 0]
        self.v2 = [0, 0, 0]
        self.v3 = [0, 0, 0]
        self.vertex = self.v1 + self.v2 + self.v3
        self.color = color
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', self.vertex),
            ('c3B', self.color)
        )
        self.object = None
        self.localize()

    def localize(self):
        self.centroid = self.x, self.y
        self.v1 = [self.x - (self.size // 3) / 0.577350269,
                   self.y - self.size // 3,
                   0.0]
        self.v2 = [self.x + (self.size // 3) / 0.577350269,
                   self.y - self.size // 3,
                   0.0]
        self.v3 = [self.x,
                   self.y + self.size,
                   0.0]
        self.v1 = list(map(int, self.v1))
        self.v2 = list(map(int, self.v2))
        self.v3 = list(map(int, self.v3))
        self.vertex = self.v1 + self.v2 + self.v3
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', self.vertex),
            ('c3B', self.color)
        )

    def move(self, vel):
        self.x += vel.x
        self.y += vel.y
        self.localize()
        self.rotate(vel.angle - 90)
        self.object.vertices = self.vertex

    def rotate(self, angle):
        self.rotated = angle
        R = Rot.from_euler('z', self.rotated, degrees=True)
        v1 = -(self.size // 3) / 0.577350269, -self.size // 3, 0
        v2 = (self.size // 3) / 0.577350269, -self.size // 3, 0
        v3 = 0, self.size, 0
        v1 = R.apply(v1)
        v2 = R.apply(v2)
        v3 = R.apply(v3)
        self.v1 = v1[0] + self.centroid[0], v1[1] + self.centroid[
            1], 0
        self.v2 = v2[0] + self.centroid[0], v2[1] + self.centroid[
            1], 0
        self.v3 = v3[0] + self.centroid[0], v3[1] + self.centroid[
            1], 0
        self.v1 = list(map(int, self.v1))
        self.v2 = list(map(int, self.v2))
        self.v3 = list(map(int, self.v3))
        self.vertex = self.v1 + self.v2 + self.v3
        # print(self.vertex)
        self.vertices = pyglet.graphics.vertex_list(
            3,
            ('v3f', self.vertex),
            ('c3B', self.color)
        )

    @property
    def vertex_list(self):
        return 3, pyglet.graphics.GL_TRIANGLES, None, ('v3f', self.vertex), \
               ('c3B', self.color)


class Quad:
    def __init__(self):
        self.vertices = pyglet.graphics.vertex_list_indexed(
            4,
            [0, 1, 2, 2, 3, 0],
            ('v3f', [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5,
                     0.5, 0.0]),
            ('c3f',
             [1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, ])
        )


class Quad2:
    def __init__(self):
        self.indices = [0, 1, 2, 2, 3, 0]
        self.vertex = [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5,
                       0.5, 0.0]
        self.color = [1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0,
                      0.0, ]
        self.vertices = pyglet.graphics.vertex_list_indexed(4,
                                                            self.indices,
                                                            ('v3f',
                                                             self.vertex),
                                                            ('c3f', self.color))


class Line:
    def __init__(self):
        self.vertex = [WIDTH // 2, 0, WIDTH // 2, HEIGHT]
        # self.vertex = [0.0, -1.0, 0.0, 1]
        self.colors = [0, 0, 255, 0, 0, 255]

        self.vertices = pyglet.graphics.vertex_list(2,
                                                    ('v2f', self.vertex),
                                                    ('c3B', self.colors),
                                                    )
