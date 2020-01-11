import traceback
from random import randint, random
from time import sleep

import pandas as pd
import numpy as np
import os

from sklearn.neural_network import MLPClassifier, MLPRegressor

# WORLD
WORLD_SIZE = 25

# ANIMAL
ANIMAL_NUMBER = 10
PARENT_PROEMINENCE = 0.5  # Percent
MUTATION = 0.05  # Percent
MAX_AGE = 500
RANDOM_ANIMALS = 0.3  # Percent
RANDOM_MEMORY = 0.3

# FOOD
FOOD_NUMBER = 200
FOOD_AMOUNT = 5
NEW_FOOD_CHANCE = 0.01

# RULES
MAX_INTERATIONS = 10000
SPEED = 0.01

# GLOBALS
animal_list = []
food_list = []


class Place:
    def __init__(self):
        self.objs = []

    def __repr__(self):
        if any(isinstance(x, Animal) for x in self.objs):
            return "@"
        elif any(isinstance(x, Food) for x in self.objs):
            return '*'

        else:
            return "_"


class Food:
    def __init__(self, amount=FOOD_AMOUNT):
        self.amount = amount
        self.location = []


class Animal:
    global mundo

    def __init__(self, id, x, y, life=100, food=0, stamina=100, dna=None,
                 **kwargs):
        self.id = id
        self.Life = life
        self.Food = food
        self.Stamina = stamina
        self.Age = 0
        self.Memory_s = []
        self.Memory_a = []
        self.All_memory = None
        if kwargs['old_memory']:
            self.All_memory = [x[:] for x in kwargs['old_memory']]
        self.Sense_radius = 1
        if not dna:
            layers = randint(2,100)
            neurons = randint(2,100)
            iters = randint(2,100)
            memorysize = randint(2,100)
            # [Layers, neurons, iters , memory]
            self.Dna = [layers, neurons, iters, memorysize]
        else:
            self.Dna = dna
        self._hidden_layers = [self.Dna[1] for _ in range(self.Dna[0])]
        self._max_memory = self.Dna[3]
        self.Brain = MLPRegressor(activation='logistic', alpha=1e-05,
                                  batch_size='auto',
                                  beta_1=0.9, beta_2=0.999,
                                  early_stopping=False,
                                  epsilon=1e-08,
                                  hidden_layer_sizes=self._hidden_layers,
                                  learning_rate='constant',
                                  learning_rate_init=0.001,
                                  max_iter=self.Dna[2]*100,
                                  momentum=0.9,
                                  nesterovs_momentum=True, power_t=0.5,
                                  random_state=1, shuffle=True,
                                  solver='adam', tol=0.0001,
                                  validation_fraction=0.1, verbose=False,
                                  warm_start=False)
        self.sensors = [randint(0, WORLD_SIZE - 1), randint(0, WORLD_SIZE - 1)]
        self.last_action = []
        self._alive = True
        self._rested = True
        self.x = x
        self.y = y
        self.genes = 15
        self.step = 1
        self.eat_count = 0
        self.think_count = 0
        if self.All_memory is None:
            start_sensor = [[randint(-5, 5), randint(-5, 5)] for _ in range(10)]
            start_out = [[randint(0,1), randint(-5, 5), randint(-5, 5)] for _ in
                         range(10)]
            self.All_memory = [start_sensor, start_out]
        else:
            if np.random.random() < RANDOM_MEMORY:
                # creating some random memories
                self.All_memory[0] += [[randint(-5, 5), randint(-5, 5)]]
                self.All_memory[1] += [[randint(0, 1), randint(-5, 5), randint(-5, 5)]]
            start_sensor = self.All_memory[0]
            start_out = self.All_memory[1]
        try:
            self.Brain.fit(start_sensor, start_out)
        except:
            print(start_sensor, start_out)
            raise ValueError

    @property
    def pos(self):
        return [self.x, self.y]

    @property
    def alive(self):
        return self._alive

    def summary(self):
        print(self.Age, self.Life, self.Food, self.Stamina, self._alive,
              self.Dna, len(self.All_memory[0]), len(self.Memory_s),
              self.eat_count, self.think_count)

    def walk(self, direction=None):
        # print(direction[0], direction[1])
        self.drain_energy(5)
        try:
            if not any(direction):
                direction = [randint(-1, 1), randint(-1, 1)]
        except:
            traceback.print_exc()
            raise ValueError
        steps = self.step
        if self._alive and self._rested:
            new_pos_x = self.x + int(np.sign(direction[0])) * steps
            new_pos_y = self.y + int(np.sign(direction[1])) * steps
            if (0 <= new_pos_x <= WORLD_SIZE - 1) and (0 <= new_pos_y <=
                                                       WORLD_SIZE - 1):
                mundo[new_pos_x, new_pos_y].objs.append(self)
                mundo[self.x, self.y].objs.remove(self)
                self.x = new_pos_x
                self.y = new_pos_y
                self.last_action = [0, direction[0], direction[1]]

    def drain_energy(self, energy):
        self.Stamina -= 1

    def check_food(self):
        here = mundo[self.x, self.y]
        if any(isinstance(x, Food) for x in here.objs):
            first_food = filter(lambda item: isinstance(item, Food),
                                here.objs)
            self.eat(next(first_food))

    def eat(self, food):
        self.eat_count += 1
        here = mundo[self.x, self.y]
        self.Food += food.amount
        try:
            here.objs.remove(food)
        except:
            traceback.print_exc()
            raise ValueError
        max_m = self._max_memory*2
        if len(self.Memory_s) < max_m and len(self.Memory_a) < max_m:
            self.Memory_s += [list(np.array(self.sensors) - np.array(
                self.pos))]
            self.Memory_a += [self.last_action]

    def attack(self):
        pass

    def flee(self):
        pass

    def remember(self):
        # put good lessons on memory
        self.All_memory[0] += self.Memory_s
        self.All_memory[1] += self.Memory_a

        # check memory capacity, forget the long past
        if self.All_memory:
            while len(self.All_memory[0]) > self._max_memory:
                self.All_memory[0].pop(0)
            while len(self.All_memory[1]) > self._max_memory:
                self.All_memory[1].pop(0)

    def think(self, *args):
        self.think_count += 1
        self.drain_energy(1)
        self.last_action = [1, 0, 0]
        if any(self.Memory_a) or any(self.Memory_s):
            # print("memoria de entrada", self.Memory_s)
            # print("memoria de saida", self.Memory_a)
            try:
                self.Brain.partial_fit(self.Memory_s, self.Memory_a)
            except:
                traceback.print_exc()
                print("Memoria", self.Memory_a,self.Memory_s)
                raise ValueError
            self.remember()
            self.Memory_s = []
            self.Memory_a = []

    def sense_food(self):
        min = 100.0
        nearest_food = 0
        if food_list:
            for food in food_list:
                vector_x = self.pos[0] - food.location[0]
                vector_y = self.pos[1] - food.location[1]
                distance = (abs(vector_x) ** 2 + abs(vector_y) ** 2) ** 0.5
                if distance < min:
                    min = distance
                    nearest_food = food
        return nearest_food.location

    def take_action(self, trial):
        actions = {
            0: self.walk,
            1: self.think,
        }

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
        # print(c1)
        # choice = randint(0, len(actions)-1)
        # choice(trial[0][1:])

    def update(self):
        if self.Age > MAX_AGE:
            self._alive = False
        if self._alive:
            self.sensors = np.array(self.sense_food()) - np.array(self.pos)
            saida = self.Brain.predict([self.sensors])
            self.take_action(saida)
            self.check_food()
            if self.Food > 0:
                self.Stamina += 5
                self.Food -= 1
                if self.Stamina > 100 and self.Life <= 100:
                    self.Life += 5
            if self.Food < 0:
                self.Food = 0
                self.Life -= 2
            if self._alive:
                self.Life -= 1
                if not self._rested:
                    self.Life -= 5
            if self.Life <= 0:
                self._alive = False
            if self.Stamina <= 0:
                self.Stamina = 0
                self._rested = False
            self.Age += 1


def alpha_and_omega():
    global mundo
    mundo = np.empty((WORLD_SIZE, WORLD_SIZE), dtype=object)
    mundo.flat = [Place() for _ in mundo.flat]


def life_breath(new_child=None, knowledge=None):
    crazys = int(RANDOM_ANIMALS * ANIMAL_NUMBER)
    for i in range(ANIMAL_NUMBER-crazys):
        pos_x = randint(0, WORLD_SIZE - 1)
        pos_y = randint(0, WORLD_SIZE - 1)
        if new_child:
            new_child_dna = mutate(new_child)
        else:
            new_child_dna = None
        a = Animal(i, pos_x, pos_y, dna=new_child_dna, old_memory=knowledge)
        animal_list.append(a)
        mundo[pos_x, pos_y].objs.append(a)
    for i in range(crazys):
        pos_x = randint(0, WORLD_SIZE - 1)
        pos_y = randint(0, WORLD_SIZE - 1)
        a = Animal(ANIMAL_NUMBER+1, pos_x, pos_y, dna=None,
                   old_memory=None)
        animal_list.append(a)
        mundo[pos_x, pos_y].objs.append(a)


def create_food(quantity=1):
    for _ in range(quantity):
        pos_x = randint(0, WORLD_SIZE - 1)
        pos_y = randint(0, WORLD_SIZE - 1)
        f = Food()
        food_list.append(f)
        mundo[pos_x, pos_y].objs.append(f)
        f.location = [pos_x, pos_y]


def left_hand_of_god():
    global animal_list, food_list
    del animal_list[:]
    del food_list[:]


def best_score():
    global animal_list
    scores = animal_list

    scores.sort(key=lambda x: x.think_count, reverse=True)
    scores.sort(key=lambda x: x.eat_count, reverse=True)
    scores.sort(key=lambda x: x.Age, reverse=True)
    print("Ganhador é o animal %s com %s de vida" % (scores[0].id, scores[
        0].Age))
    return scores


def mate(parents):
    parentA, parentB = parents
    old_memory = []
    for i in range(len(parentA.Dna)):
        if random() <= PARENT_PROEMINENCE:
            parentA.Dna[i] = parentB.Dna[i]
    old_memory = parentA.All_memory[:]
    child = parentA
    return child, old_memory


def mutate(fetus):
    new_dna = []
    for gene in fetus.Dna:
        if random() <= MUTATION:
            new_dna.append(randint(2, 100))
        else:
            new_dna.append(gene)
    return new_dna


# alpha_and_omega()
mundo = np.empty((WORLD_SIZE, WORLD_SIZE), dtype=object)
mundo.flat = [Place() for _ in mundo.flat]
life_breath()
create_food(FOOD_NUMBER)
count = 0

# print(mundo)
# animal_list[0].walk(1, [randint(-1, 1), randint(-1, 1)])
all_dead = False
while count < MAX_INTERATIONS:
    while not all_dead:
        dead_count = 0
        for animal in animal_list:
            try:
                animal.update()
                if not animal.alive:
                    dead_count += 1
            except:
                traceback.print_exc()
                raise EnvironmentError
        if dead_count >= len(animal_list):
            all_dead = True
        os.system('clear')
        if np.random.random() < NEW_FOOD_CHANCE:
            create_food()
        print('iteração do mundo número: %s/%s' % (count+1, MAX_INTERATIONS))
        print(mundo)
        for animal in animal_list:
            animal.summary()
        sleep(SPEED)

    ganhadores = best_score()
    child, memory = mate(ganhadores[:2])
    # child = mutate(child)
    left_hand_of_god()
    mundo = np.empty((WORLD_SIZE, WORLD_SIZE), dtype=object)
    mundo.flat = [Place() for _ in mundo.flat]
    life_breath(child, memory)
    create_food(FOOD_NUMBER)
    all_dead = False
    count += 1

# best_score()
# for animal in animal_list:
#     print(animal.Food)
# print(mundo)
# print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')
