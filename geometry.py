from collections import namedtuple
from math import tan
from math import pi
from math import sqrt

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

Plane = namedtuple("Plane", "location direction")
Triangle = namedtuple("Triangle", "a b c, color")

a = Plane(Vector(3, 1, 1), Vector(1, 1, 1))

def intersection(plane, ray):
    return (plane.location - ray.location) * plane.direction / (ray.direction * plane.direction)
def colliding(plane, ray):
    try:
        t = intersection(plane, ray)
        if t < 0:
            return False
        else:
            return True
    except:
        return False
def rayToVector(r):
    return r.direction + r.location
def isBounded(p, bounds, n, t):
    p = rayToVector(p) * t
    if ((bounds.b - bounds.a) ** (p - bounds.a)) * n > 0:
        if ((bounds.c - bounds.b) ** (p - bounds.b)) * n > 0:
            if ((bounds.a - bounds.c) ** (p - bounds.c)) * n > 0:
                return True
    if ((bounds.b - bounds.a) ** (p - bounds.a)) * n < 0:
        if ((bounds.c - bounds.b) ** (p - bounds.b)) * n < 0:
            if ((bounds.a - bounds.c) ** (p - bounds.c)) * n < 0:
                return True
    return False
def triToPlane(triangle):
    normal = (triangle.a - triangle.b) ** (triangle.b - triangle.c)
    return normal * (1/sqrt(normal.x ** 2 + normal.y ** 2 + normal.z ** 2))
def rayCast(ray, triangles, primary = True, self = None):
    shortest = 100000
    color = Vector(255, 255, 255)
    for triangle in triangles:
        if triangle == self:
            continue
        p = Plane(triangle.a, triToPlane(triangle))
        if colliding(p, ray):
            time = intersection(p, ray)
            if isBounded(ray, triangle, p.direction, time):
                if intersection(p, ray) < shortest:
                    shortest = time
                    if primary:
                        secondT = rayCast(Ray(Vector(100, -100, 0), (rayToVector(ray) * time + p.direction * 0) - Vector(100, -100, 0)), triangles, False, triangle)
                        if secondT[1] != 100000:
                            if str(secondT[0]) == "255 0 0" and str(triangle.color) == "0 255 255":
                                #print(str(Ray(rayToVector(ray) * time + p.direction * 1e-3, Vector(-1, 1, 0))))
                                pass
                            color = secondT[0] #triangle.color - Vector(100, 100, 100)
                        else:
                            color = triangle.color 
                    else:
                        color = triangle.color 
    color = Vector(max(color.x, 0), max(color.y, 0), max(color.z, 0))
    return (color, shortest)

def render(height, width, fov, tris):
    result = []
    hstep = 1 / height
    wstep = 1 / width
    aspectRatio = width / height
    for h in range(0,height):
        for w in range(0,width):
            pixelScreen = ((((w + 0.5) * wstep) * 2 - 1) * aspectRatio * tan(fov), (1 - ((h + 0.5) * hstep) * 2) * tan(fov))
            result.append(rayCast(Ray(Vector(0, 0, 0), Vector(pixelScreen[0], pixelScreen[1], 1)), tris)[0])
    return result

t = Triangle(Vector(3, 3, 3), Vector(3, -3, 3), Vector(0, -3, 6), Vector(255, 0, 0))
tt = Triangle(Vector(0, -3, 6), Vector(0, 3, 6), Vector(3, 3, 3), Vector(0, 255, 0))
ttt = Triangle(Vector(0, 3, 5), Vector(0, 3, 3), Vector(3, 3, 3), Vector(0, 0, 255))
floor = Triangle(Vector(-10, -3, 10), Vector(30, -3, 0), Vector(-10, -3, -10), Vector(0, 255, 255))
#tt = Triangle(Vector(-1, -1, -1000), Vector(1, 0, -1000), Vector(1, 1, -1000))
p = Vector(0.6, 2, 0.4)
scene = list(map(lambda a: str(a), render(200, 200, pi / 3.5, [t, tt, ttt, floor])))
print("P3")
print("200 200")
print("1")
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
for line in chunker(scene, 200):
    #l = map(lambda a: "1" if a != "100000" else "0", line)
    print(" ".join(line))
    pass
#print(list(filter(lambda a: a != 100000, render(10, 10, pi / 4, [t]))))
#print(rayCast(Ray(Vector(0,0,0), p), [t]))
