from random import randint

import pyglet
from pyglet.window import key

from creatures import CreatureManager
from primitives import Line, Triangle, Point, Vector

WIDTH = 800
HEIGHT = 600
NUM_CREATURES = 1

# batch = pyglet.graphics.Batch()


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        self.set_minimum_size(400, 300)
        # pyglet.gl.glClearColor(0.2, 0.3, 0.2, 1.0)
        self.line = Line()
        self.triangle = Triangle(100, 100)
        self.point = Point(200, 200)
        self.objects = []
        self.creatures = CreatureManager()

        # self.triangle = Triangle()
        # self.quad2 = Quad2()
        self.creatures.add_creature(NUM_CREATURES)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.D: # right
            vel = Vector(1, 0)
            for creature in self.creatures.creatures:
                creature.move(vel)
        if symbol == key.S: # down
            vel = Vector(0, -1)
            for creature in self.creatures.creatures:
                creature.move(vel)
        if symbol == key.A: # left
            vel = Vector(-1, 0)
            for creature in self.creatures.creatures:
                creature.move(vel)
        if symbol == key.W: # up
            vel = Vector(0, 1)
            for creature in self.creatures.creatures:
                creature.move(vel)

    # def add_object(self, n):
    #     for _ in range(n):
    #         particle = self.batch.add(1, pyglet.gl.GL_POINTS, None,
    #                              ('v2f', [randint(0, WIDTH),
    #                                              randint(0, HEIGHT)]),
    #                              ('c3B', [0, 0, 255]))
    #         self.objects.append(particle)
    #     print(self.objects)
        # batch.draw()

    def on_draw(self):
        self.clear()
        # self.quad2.vertices.draw(pyglet.gl.GL_TRIANGLES)
        self.line.vertices.draw(pyglet.gl.GL_LINES)
        self.triangle.vertices.draw(pyglet.gl.GL_TRIANGLES)
        self.point.vertices.draw(pyglet.gl.GL_POINTS)
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS,
                             ('v2i', (10, 15, 30, 35))
                             )
        self.creatures.batch.draw()

    # def on_resize(self, width, height):
    #     pyglet.gl.glViewport(0, 0, width, height)


i = 0

def randomize_points():
    global window

    for obj in window.objects:
        obj.vertices[0] = randint(0, WIDTH)
        obj.vertices[1] = randint(0, HEIGHT)

def loop(dt):
    global i
    window.clear()
    i += 1
    window.triangle.rotate(i)
    randomize_points()


if __name__ == "__main__":
    window = MyWindow(WIDTH, HEIGHT, "Meu Teste")
    clock = pyglet.app.event_loop.clock
    clock.schedule_interval(loop, 0.05)
    pyglet.app.run()
