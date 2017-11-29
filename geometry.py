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

#Basically classes without functions
Plane = namedtuple("Plane", "location direction")
Triangle = namedtuple("Triangle", "a b c color")

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

def rayToVector(r, t = 1):
    return r.direction * t + r.location

def isBounded(q, bounds, n, t):
    p = rayToVector(q, t)
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
#tt = Triangle(Vector(-1, -1, -1000), Vector(1, 0, -1000), Vector(1, 1, -1000))
p = Vector(0.6, 2, 0.4)
scene = list(map(lambda a: str(a), render(200, 200, pi / 3.5, [t, tt, ttt, floor])))
print("P3")
print("200 200")
print("255")
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
for line in chunker(scene, 200):
    #l = map(lambda a: "1" if a != "100000" else "0", line)
    print(" ".join(line))
    pass
#print(list(filter(lambda a: a != 100000, render(10, 10, pi / 4, [t]))))
#print(rayCast(Ray(Vector(0,0,0), p), [t]))
