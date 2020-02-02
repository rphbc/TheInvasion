import traceback
import uuid
from random import randint

import pyglet
import pyglet as pgt
from matplotlib import path as pltpath
import numpy as np
from sklearn.neural_network import MLPRegressor

from constants import WIDTH, HEIGHT, MAX_SPEED, VISION_RADIUS, ROAM, \
    RANDOM_MEMORY
from primitives import Triangle, Vector, Circle


class CreatureManager:
    def __init__(self):
        self.batch = pgt.graphics.Batch()
        self.creatures = {}

    def add_creature(self, n):
        for _ in range(n):
            creature = Animal(x=300, y=300, random=True,
                              show_vision=True)
            particle = self.batch.add(*creature.body.vertex_list)
            creature.body.object = particle
            self.creatures[creature.id] = creature

    def update(self, food_manager):
        if self.creatures:
            for creature in self.creatures.values():
                creature.update(food_manager)
                if creature.life <= 0:
                    self.kill_creature(creature.id)
                    break
            self.batch.draw()
            # print(self.creatures)

    def kill_creature(self, uuid):
        self.creatures[uuid].body.object.delete()
        del self.creatures[uuid]
        # print(uuid)


class Animal:
    def __init__(self, x=0, y=0, random=False, show_vision=False, dna=None,
                 **kwargs):
        self.id = uuid.uuid4()
        self.life = 100
        self._alive = True
        self.genes = 15
        self.age = 0
        self.memory_s = []
        self.memory_a = []
        self.all_memory = None
        if kwargs.get('old_memory', None):
            self.all_memory = [x[:] for x in kwargs['old_memory']]
        if not dna:
            layers = randint(2, 100)
            neurons = randint(2, 100)
            iters = randint(2, 100)
            memorysize = randint(2, 100)
            # [Layers, neurons, iters , memory]
            self.dna = [layers, neurons, iters, memorysize]
        else:
            self.dna = dna

        self._hidden_layers = [self.dna[1] for _ in range(self.dna[0])]
        self._max_memory = self.dna[3]
        self.brain = MLPRegressor(activation='logistic', alpha=1e-05,
                                  batch_size='auto',
                                  beta_1=0.9, beta_2=0.999,
                                  early_stopping=False,
                                  epsilon=1e-08,
                                  hidden_layer_sizes=self._hidden_layers,
                                  learning_rate='constant',
                                  learning_rate_init=0.001,
                                  max_iter=self.dna[2] * 100,
                                  momentum=0.9,
                                  nesterovs_momentum=True, power_t=0.5,
                                  random_state=1, shuffle=True,
                                  solver='adam', tol=0.0001,
                                  validation_fraction=0.1, verbose=False,
                                  warm_start=False)

        if random:
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
        self.body = Triangle(x=x, y=y, random=False)
        self.vision = Circle(x=x, y=y, radius=VISION_RADIUS)
        self.show_vision = show_vision
        self.position = Vector(x, y)
        self.velocity = Vector(0, 0)
        self.aceleration = Vector(0, 0)
        self.mass = 10
        self.visible_objects = []
        self.last_action = [0, 0, 0]

        if self.all_memory is None:
            start_sensor = [[randint(-5, 5), randint(-5, 5)] for _ in range(10)]
            start_out = [[randint(0, 1), randint(-5, 5), randint(-5, 5)] for _
                         in
                         range(10)]
            self.all_memory = [start_sensor, start_out]
        else:
            if np.random.random() < RANDOM_MEMORY:
                # creating some random memories
                self.all_memory[0] += [[randint(-5, 5), randint(-5, 5)]]
                self.all_memory[1] += [[randint(0, 1), randint(-5, 5),
                                        randint(-5, 5)]]
            start_sensor = self.all_memory[0]
            start_out = self.all_memory[1]
        try:
            self.brain.fit(start_sensor, start_out)
        except:
            print(start_sensor, start_out)
            raise ValueError

    def rotate(self):
        angle = self.position.angle
        self.body.rotate(angle=angle)

    def move(self, vel):
        self.spend_energy(0.1)
        self.velocity = vel
        self.position += vel
        if self.position.x >= WIDTH:
            self.position.x = WIDTH
        if self.position.y >= HEIGHT:
            self.position.y = HEIGHT
        if self.position.x <= 0:
            self.position.x = 0
        if self.position.y <= 0:
            self.position.y = 0
        self.body.move(self.position, vel)

    def check_near_food(self, foods):
        creature_path = pltpath.Path([*np.array_split(self.vision.vertex,
                                                      self.vision.points)])
        food_positions = [food.body.vertex for food in
                          foods]
        collide = creature_path.contains_points(food_positions)
        if any(collide):
            food_positions = np.array(list(foods))
            near_food = food_positions[collide]
            self.visible_objects = near_food
        else:
            self.visible_objects = []
        # print(self.visible_objects)

    def check_collision(self, food_manager):
        foods = food_manager.foods.values()
        body_path = pltpath.Path([*np.array_split(self.body.vertex2D, 3)])
        food_positions = [food.body.vertex for food in foods]
        collide = body_path.contains_points(food_positions)
        if any(collide):
            food_positions = np.array(list(foods))
            target_food = food_positions[collide]
            energy = food_manager.consume_food(target_food[0].id)
            self.eat(energy)
        else:
            target_food = []
        # print(self.life)

    def breath(self):
        self.spend_energy(0.1)

    def eat(self, energy):
        self.spend_energy(0.1)
        self.life += energy
        max_m = self._max_memory * 2
        if len(self.memory_s) < max_m and len(self.memory_a) < max_m:
            self.memory_s += [list(self.visible_objects[0].position -
                                   self.position)]
            self.memory_a += [self.last_action]

    def spend_energy(self, energy):
        self.life -= energy

    def update(self, food_manager):
        self.breath()
        foods = food_manager.foods.values()
        if self.show_vision:
            self.vision.update(self.position[0], self.position[1])
            pyglet.graphics.draw(*self.vision.vertex_list)
        self.check_near_food(foods)
        self.check_collision(food_manager)
        saida = None
        if any(self.visible_objects):
            saida = self.brain.predict([self.visible_objects[0].position._v])
        self.take_action(saida)

    def take_action(self, trial):
        actions = {
            0: self.walk,
            1: self.think,
        }
        if trial is not None:
            trial = np.round(trial)
            # print(trial)
            try:
                choice = actions.get(int(trial[0][0]), self.walk)
                choice(trial[0][1:])
            except:
                choice = actions[0]
                choice()
                traceback.print_exc()
                raise ValueError
        else:  # if no trial, walk
            choice = actions[0]
            choice()

    def walk(self, direction=None):
        self.spend_energy(0.1)

        if direction is None:
            acc = Vector(randint(-MAX_SPEED, MAX_SPEED), randint(-MAX_SPEED,
                                                                 MAX_SPEED))
        else:
            acc = Vector(*direction)
        if self.velocity.x >= MAX_SPEED and acc.x < 0:
            self.velocity.x += acc.x
        elif self.velocity.x <= -MAX_SPEED and acc.x > 0:
            self.velocity.x += acc.x
        if self.velocity.y >= MAX_SPEED and acc.y < 0:
            self.velocity.y += acc.y
        elif self.velocity.y <= -MAX_SPEED and acc.y > 0:
            self.velocity.y += acc.y
        if -MAX_SPEED <= self.velocity.x <= MAX_SPEED:
            self.velocity.x += acc.x
        if -MAX_SPEED <= self.velocity.y <= MAX_SPEED:
            self.velocity.y += acc.y
        self.last_action = [0, acc[0], acc[1]]
        self.move(self.velocity)
        # print(f" velocidade: {self.velocity}, acc: {acc}")

    def think(self, *args):
        # self.think_count += 1
        self.spend_energy(0.1)
        self.last_action = [1, 0, 0]
        if any(self.memory_a) or any(self.memory_s):
            # print("memoria de entrada", self.Memory_s)
            # print("memoria de saida", self.Memory_a)
            try:
                self.brain.partial_fit(self.memory_s, self.memory_a)
            except:
                traceback.print_exc()
                print("Memoria", self.memory_a, self.memory_s)
                raise ValueError
            self.remember()
            self.memory_s = []
            self.memory_a = []

    def remember(self):

        # put good lessons on memory
        self.all_memory[0] += self.memory_s
        self.all_memory[1] += self.memory_a

        # check memory capacity, forget the long past
        if self.all_memory:
            while len(self.all_memory[0]) > self._max_memory:
                self.all_memory[0].pop(0)
            while len(self.all_memory[1]) > self._max_memory:
                self.all_memory[1].pop(0)

