import numpy as np

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1])

def multiply(a, x):
    return (x*a[0], x*a[1])

def mag(a):
    return np.sqrt(a[0]**2 + a[1]**2)

def perp(a):
    if a[0] == 0:
        return (1, 0);
    if a[1] == 0:
        return (0, 1);
    perp_vector = (1, -a[0]/a[1])
    perp_vector = multiply(perp_vector, 1/mag(perp_vector))
    return perp_vector

def toInt(a):
    return (int(a[0]), int(a[1]))
