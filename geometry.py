from collections import namedtuple
from math import tan
from math import pi
from math import sqrt
import curses
import time

class Vector:
    x: float
    y: float
    z: float

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __mul__(self, other):
        if (isinstance(other, Vector)):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            return Vector(self.x * other, self.y * other, self.z * other)

    def __sub__(self, other):
        return self + other * -1

    #Cross product
    def __pow__(self, other):
        return Vector(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    def __str__(self):
        return "" + str(self.x) + " " + str(self.y) + " " + str(self.z) + ""

class Ray:
    location: Vector
    direction: Vector

    def __init__(self, loc, dir):
        self.location = loc
        self.direction = dir

    def __str__(self):
        return str(self.location) + " " + str(self.direction)

#Basically classes without functions and actual type checking
Plane = namedtuple("Plane", "location direction")
Triangle = namedtuple("Triangle", "a b c color")

#Returns the time when a ray intersects a plane. Could be positive, negative, or throw an error
def intersection(plane, ray):
    return (plane.location - ray.location) * plane.direction / (ray.direction * plane.direction)

#Uses intersection to determine if a ray collides with a plane while moving forwards
def colliding(plane, ray):
    try:
        t = intersection(plane, ray)
        if t < 0:
            return False
        else:
            return True
    except:
        return False

#Converts a ray to a simple vector
def rayToVector(r, t = 1):
    return r.direction * t + r.location

#Determines if a given point (given through a vector and a time) is inside of a triangle.
def isBounded(q, bounds, n, t):
    p = rayToVector(q, t)
    if ((bounds.b - bounds.a) ** (p - bounds.a)) * n > 0:
        if ((bounds.c - bounds.b) ** (p - bounds.b)) * n > 0:
            if ((bounds.a - bounds.c) ** (p - bounds.c)) * n > 0:
                return True
    #Checks if it collides from the other direction
    if ((bounds.b - bounds.a) ** (p - bounds.a)) * n < 0:
        if ((bounds.c - bounds.b) ** (p - bounds.b)) * n < 0:
            if ((bounds.a - bounds.c) ** (p - bounds.c)) * n < 0:
                return True
    return False

#Converts a triangle to a plane with normalized normal
def triToPlane(triangle):
    normal = (triangle.a - triangle.b) ** (triangle.b - triangle.c)
    return normal * (1/sqrt(normal.x ** 2 + normal.y ** 2 + normal.z ** 2))

#Fires a ray and finds the triangle it first intersects
def launchRay(ray, triangles):
    shortest = 100000
    color = Vector(0, 0, 0)
    tri = None
    for triangle in triangles:
        p = Plane(triangle.a, triToPlane(triangle))
        if colliding(p, ray):
            time = intersection(p, ray)
            if isBounded(ray, triangle, p.direction, time):
                if intersection(p, ray) < shortest:
                    shortest = time
                    tri = triangle
    return (shortest, tri)

#Given a ray and some triangles, determines a color based on shadows and colors
def rayCast(ray, triangles):
    (time, tri) = launchRay(ray, triangles)
    color = Vector(0, 0, 0)
    if time != 100000:
        p = Plane(tri.a, triToPlane(tri))
        secondT = launchRay(Ray(rayToVector(ray, time) + p.direction * 1e-4, Vector(-2, 5, 4) - (rayToVector(ray, time) + p.direction * 1e-4)), triangles)

        if secondT[0] != 100000:
            color = tri.color - Vector(150, 150, 150)
        else:
            color = tri.color 

        if color.y < 0 or color.z < 0 or color.x < 0:
            color = Vector(max(color.x, 0), max(color.y, 0), max(color.z, 0))

    return color

#Creates a ray for every pixel on the screen
def render(height, width, fov, tris):
    result = []
    hstep = 1 / height
    wstep = 1 / width
    aspectRatio = width / height
    for h in range(0,height):
        for w in range(0,width):
            pixelScreen = ((((w + 0.5) * wstep) * 2 - 1) * aspectRatio * tan(fov), (1 - ((h + 0.5) * hstep) * 2) * tan(fov))
            result.append(rayCast(Ray(Vector(0, 0, 0), Vector(pixelScreen[0], pixelScreen[1], 1)), tris))
    return result

t = Triangle(Vector(3, 3, 3), Vector(3, -3, 3), Vector(0, -3, 6), Vector(255, 0, 0))
tt = Triangle(Vector(0, -3, 6), Vector(0, 3, 6), Vector(3, 3, 3), Vector(0, 255, 0))
ttt = Triangle(Vector(0, 3, 5), Vector(0, 3, 3), Vector(3, 3, 3), Vector(0, 0, 255))
floor = Triangle(Vector(-10, -3, 10), Vector(30, -3, 0), Vector(-10, -3, -10), Vector(0, 255, 255))

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def initColors():
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)

def loadImages(fileName):
    with open(fileName) as f:
        tris = f.readlines()
        return list(map(lambda a: stringToTri(a), tris))

def stringToTri(s):
    split = list(map(lambda a: stringToVector(a), s.split(",")))
    return Triangle(split[0], split[1], split[2], split[3])

def stringToVector(s):
    split = s.split(" ")
    return Vector(float(split[0]), float(split[1]), float(split[2]))

def getUserInput(stdscr):
    key = stdscr.getch()
    if key == 10:
        return ""
    else:
        return chr(key) + getUserInput(stdscr)
    pass

def main(stdscr):
    stdscr.clear()
    initColors()

    #Get user input
    curses.echo()
    stdscr.addstr(3, 0, "Enter a file name for the scene:")
    stdscr.move(4, 0)
    tris = loadImages(getUserInput(stdscr))
    curses.noecho()
    stdscr.clear()
    stdscr.addstr(3, 0, "Rendering...")
    stdscr.refresh()

    # Prepare and render
    pad = curses.newpad(curses.LINES + 1, curses.COLS + 1)
    scene = render(curses.LINES, curses.COLS, pi/4, tris)
    stdscr.clear()
    loc = [0, 0]
    lines = list(chunker(scene, curses.COLS))
    for l in lines:
        loc[0] = 0
        for c in l:
            color = 1
            brightness = 0
            char = " "
            if c.x != 0 and c.y != 0 and c.z != 0:
                color = 0
                brightness = c.x
            elif c.x != 0 and c.y != 0 and c.z == 0:
                color = 1
                brightness = c.x
            elif c.x != 0 and c.y == 0 and c.z == 0:
                color = 2
                brightness = c.x
            elif c.x == 0 and c.y != 0 and c.z != 0:
                color = 3
                brightness = c.z
            elif c.x == 0 and c.y != 0 and c.z == 0:
                color = 4
                brightness = c.y
            elif c.x != 0 and c.y == 0 and c.z != 0:
                color = 5
                brightness = c.z
            elif c.x == 0 and c.y == 0 and c.z != 0:
                color = 6
                brightness = c.z
            elif c.x == 0 and c.y == 0 and c.z == 0:
                color = 7
                brightness = 0

            if brightness > 200:
                char = "@"
            elif brightness > 0:
                char = ":"

            pad.addstr(loc[1], loc[0], char, curses.color_pair(color))
            loc[0] += 1
        loc[1] += 1

    stdscr.refresh()
    pad.refresh(0, 0, 0, 0, curses.LINES-1, curses.COLS-1)
    stdscr.refresh()
    stdscr.getkey()

curses.wrapper(main)

# p = Vector(0.6, 2, 0.4)
# scene = list(map(lambda a: str(a), render(64, 112, pi / 4, [t, tt, ttt, floor])))
# print("P3")
# print("112 64")
# print("255")
# for line in chunker(scene, 112):
#     print(" ".join(line))
#     pass
