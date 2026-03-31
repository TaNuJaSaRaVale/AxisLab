import math
from typing import Union

class Shape:
    def area(self) -> float: 
        return 0.0
    def perimeter(self) -> float: 
        return 0.0

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        
    def distance_to(self, other: "Point") -> float:
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return float(f"{distance:.2f}")
        
    def midpoint(self, other: "Point") -> "Point":
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)
        
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

class Line:
    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2
        
    def length(self) -> float:
        return self.p1.distance_to(self.p2)

    def slope(self) -> Union[float, str]:
        if self.p2.x - self.p1.x == 0:
            return "Undefined (Vertical Line)"
        s = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)
        return float(f"{s:.2f}")

class Triangle(Shape):
    def __init__(self, p1: Point, p2: Point, p3: Point) -> None:
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.side_a = p2.distance_to(p3)
        self.side_b = p1.distance_to(p3)
        self.side_c = p1.distance_to(p2)
        
    def perimeter(self) -> float:
        p = self.side_a + self.side_b + self.side_c
        return float(f"{p:.2f}")
        
    def area(self) -> float:
        # Heron's formula
        s = self.perimeter() / 2
        calculation = s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c)
        if calculation <= 0:
            return 0.0 # Invalid triangle
        area_val = math.sqrt(calculation)
        return float(f"{area_val:.2f}")

class Circle(Shape):
    def __init__(self, center: Point, radius: float) -> None:
        self.center = center # Point object
        self.radius = float(radius)
        
    def area(self) -> float:
        a = math.pi * (self.radius ** 2)
        return float(f"{a:.2f}")
        
    def circumference(self) -> float:
        c = 2 * math.pi * self.radius
        return float(f"{c:.2f}")

class Polygon(Shape):
    def __init__(self, points: list[Point]) -> None:
        if len(points) < 3:
            raise ValueError("Polygon must have at least 3 points")
        self.points = points

    def perimeter(self) -> float:
        p = 0.0
        n = len(self.points)
        for i in range(n):
            p += self.points[i].distance_to(self.points[(i + 1) % n])
        return float(f"{p:.2f}")

    def area(self) -> float:
        # Shoelace formula for simple polygon area
        a = 0.0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            a += self.points[i].x * self.points[j].y
            a -= self.points[j].x * self.points[i].y
        return float(f"{abs(a) / 2.0:.2f}")

