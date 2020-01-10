import math

from primitives import Triangle, Vector
import pyglet as pgt


class CreatureManager:
    def __init__(self):
        self.batch = pgt.graphics.Batch()
        self.creatures = []

    def add_creature(self, n):
        for _ in range(n):
            creature = Animal(x=300, y=300, random=False)
            particle = self.batch.add(*creature.body.vertex_list)
            creature.body.object = particle
            self.creatures.append(creature)


class Animal:
    def __init__(self,x=0, y=0, random=False):
        self.body = Triangle(x=x, y=y, random=random)
        self.position = Vector(0, 0)
        self.velocity = Vector(0, 0)
        self.mass = 0

    def rotate(self):
        angle = self.position.angle
        self.body.rotate(angle=angle)

    def move(self, vel):
        self.velocity = vel
        self.body.move(self.velocity)
