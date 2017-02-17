import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import vectorutils as vector

class Line:
    width = 5
    points = []
    tags = []
    start_small = False
    end_small = True
    def __init__(self, points):
        self.points = points

def brush(line, canvas, s):
    """ Brush line onto canvas at scale s. """
    current_point = line.points[0]
    x = current_point
    v = (0, 0)
    threshold = 1
    max_v = 4
    for next_point in line.points[1:]:
        while (vector.mag(vector.subtract(next_point, x)) > threshold):
            draw_lines(x, v, line.width, canvas, s)
            #import pdb; pdb.set_trace()
            f = vector.subtract(next_point, x)
            v = vector.add(v, f)
            if vector.mag(v) > max_v:
                v = vector.multiply(v, 1./vector.mag(v))
            x = vector.add(x, v)
            print x
        current_point = next_point

def calculateSize(objects, scale):
    """ Calculate maximum x and y of a group of objects. """
    max_x = 0
    max_y = 0
    for o in objects:
        for point in o.points:
            if point[0] + o.width + 1 > max_x:
                max_x = point[0] + o.width + 1
            if point[1] + o.width + 1 > max_y:
                max_y = point[1] + o.width + 1
    return (round(scale*max_x), round(scale*max_y))

def draw(objects):
    scale = 1
    canvas = np.zeros(calculateSize(objects, scale))
    for o in objects:
        brush(o, canvas, scale)
    plt.imshow(canvas)
    plt.show()

def demo():
    line = Line([(6, 6), (20, 6), (10, 20)])
    draw([line])

def draw_lines(x, v, w, canvas, s):
    """
    Draw w lines onto the canvas at x with direction v and scale factor s.
    """
    centre = vector.multiply(x, s)
    speed = vector.mag(v)
    for line in range(w):
        start = vector.subtract(centre, v)
        start = vector.add(vector.multiply(vector.perp(v),
            line-w/(2*(speed+1))), start)
        end = vector.add(centre, v)
        end = vector.add(vector.multiply(vector.perp(v),
            line-w/(2*(speed+1))), end)
	start = vector.toInt(start)
        end = vector.toInt(end)
        canvas[start[0], start[1]] = 1
        canvas[end[0], end[1]] = 1
