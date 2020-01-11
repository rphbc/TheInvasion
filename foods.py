from primitives import Triangle, Vector, Point
from constants import *
import pyglet as pgt


class FoodManager:
    def __init__(self):
        self.batch = pgt.graphics.Batch()
        self.foods = []

    def add_food(self, n):
        for _ in range(n):
            food = Food(x=300, y=300, random=True)
            particle = self.batch.add(*food.body.vertex_list)
            food.body.object = particle
            self.foods.append(food)


class Food:
    def __init__(self, x=0, y=0, amount=FOOD_AMOUNT, random=False):
        self.body = Point(x=x, y=y, color=(0, 255, 0), random=random)
        self.position = Vector(0, 0)
        self.amount = amount