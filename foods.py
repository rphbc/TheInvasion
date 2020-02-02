import uuid

from primitives import Triangle, Vector, Point
from constants import *
import pyglet as pgt
import numpy as np


class FoodManager:
    def __init__(self):
        self.batch = pgt.graphics.Batch()
        self.foods = {}

    def add_food(self, n):
        for _ in range(n):
            food = Food(x=300, y=300, random=True)
            particle = self.batch.add(*food.body.vertex_list)
            food.body.object = particle
            self.foods[food.id] = food

    def consume_food(self, uuid):
        energy = self.foods[uuid].amount
        self.delete_food(uuid)
        return energy

    def delete_food(self, uuid):
        print(f"deleting food {self.foods[uuid]} at"
              f" {self.foods[uuid].body.vertex}")
        self.foods[uuid].body.object.delete()
        del self.foods[uuid]


class Food:
    def __init__(self, x=0, y=0, amount=FOOD_AMOUNT, random=False):
        self.id = uuid.uuid4()
        self.body = Point(x=x, y=y, color=(0, 255, 0), random=random)
        if random:
            self.position = Vector(self.body.x, self.body.y)
        else:
            self.position = Vector(x, y)
        self.amount = amount

    def __str__(self):
        return f"{self.id} - {self.position}"

    def __repr__(self):
        return f"{self.id} - {self.position}"
