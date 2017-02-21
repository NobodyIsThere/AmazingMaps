INFINITY = 999999999

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def angle(a):
    return atan2(a[1], a[0])

def get_bounds(points):
    min_x = points[0][0]
    min_y = points[0][1]
    max_x = points[0][0]
    max_y = points[0][1]
    for p in points[1:]:
        if p[0] < min_x:
            min_x = p[0]
        if p[0] > max_x:
            max_x = p[0]
        if p[1] < min_y:
            min_y = p[1]
        if p[1] > max_y:
            max_y = p[1]
    return min_x, min_y, max_x, max_y

def intercept(a, gradient):
    if a[0] == 0 or gradient == INFINITY:
        return a[1]
    else:
        return a[1] - gradient*a[0]

def intersects(a, b, c, d):
    """ Return True if ab intersects cd. """
    # l1 and l2 are the two lines but with the left-most points first.
    l1 = (a, b) if a[0] < b[0] else (b, a)
    l2 = (c, d) if c[0] < d[0] else (d, c)
    """if l1[0][0] < l2[0][0] and l1[1][0] < l2[0][0]:
        return False
    if l2[0][0] < l1[0][0] and l2[1][0] < l1[0][0]:
        return False
    if l1[0][1] < l2[0][1] and l1[0][1] < l2[1][1] and l1[1][1] < l2[0][1] and l1[1][1] < l2[1][1]:
        return False
    if l2[0][1] < l1[0][1] and l2[0][1] < l1[1][1] and l2[1][1] < l1[0][1] and l2[1][1] < l1[1][1]:
        return False"""
    # The lines might actually intersect!
    m1 = slope(l1)
    m2 = slope(l2)
    if m1 == m2:
        return False
    c1 = intercept(l1[0], m1)
    c2 = intercept(l2[0], m2)
    x = float(c2-c1)/(m1-m2)
    #stroke(255, 0, 0)
    #print m2, c2
    #point(x, m1*x + c1)
    #stroke(0, 0, 0)
    if x > l1[0][0] and x > l2[0][0] and x < l1[1][0] and x < l2[1][0]:
        #print ("intersection :(")
        return True
    return False

def intersectsLine(a, b, points):
    p_start = points[0]
    for p_end in points[1:]:
        if intersects(a, b, p_start, p_end):
            return True
        p_start = p_end
    return False

def line_pos(l, xy):
    """
    Find the other coordinate of intersection of the line l with x = x or y = y
    Note: assumes that the line is ordered according to increasing x or y.
    """
    if len(l) < 2:
        return (l[0][0], l[0][1])
    start_point = l[-2]
    end_point = l[-1]
    if xy[0] == None:
        # We're finding the x-coordinate
        for i, p in enumerate(l):
            if p[1] < xy[1]:
                if i < len(l)-1:
                    start_point = p
                    end_point = l[i+1]
        m = slope((start_point, end_point))
        x = start_point[0]
        if m != INFINITY:
            c = intercept(start_point, m)
            x = float(xy[1]-c)/m
        return (x, xy[1])
    if xy[1] == None:
        # Find the y-coordinate
        for i, p in enumerate(l):
            if p[0] < xy[0]:
                if i < len(l)-1:
                    start_point = p
                    end_point = l[i+1]
                    break
        m = slope((start_point, end_point))
        y = 0.5*(start_point[1] + end_point[1])
        if m != INFINITY:
            c = intercept(start_point, m)
            y = m*xy[0] + c
        return (xy[0], y)

def rect_within(a, b):
    """ Returns True if rect a (x, y, w, h) is within rect b """
    return (a[0] > b[0] and a[1] > b[1] and 
        a[0]+a[2] < b[0]+b[2] and a[1]+a[3] < b[1]+b[3])

def slope(l):
    """ Returns "m" as in y = mx + c for line l[0] -> l[1] """
    if l[1][0] - l[0][0] == 0:
        return INFINITY
    return float(l[1][1] - l[0][1])/(l[1][0] - l[0][0])

def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1])

def multiply(a, x):
    return (x*a[0], x*a[1])

def mag(a):
    return sqrt(a[0]**2 + a[1]**2)

def midpoint(points):
    sum_x = 0.
    sum_y = 0.
    for p in points:
        sum_x += p[0]
        sum_y += p[1]
    return (sum_x/len(points), sum_y/len(points))

def normalise(a):
    if mag(a) == 0:
        return a
    return multiply(a, 1./mag(a))

def between(a, b, prop):
    return (a[0] + prop*(b[0]-a[0]), a[1] + prop*(b[1]-a[1]))

def distance(a, b):
    return sqrt(pow(b[0]-a[0], 2) + pow(b[1]-a[1], 2))

def equal(a, b):
    return a[0] == b[0] and a[1] == b[1]
    
def inList(a, l):
    for i in l:
        if equal(a, i):
            return True
    return False

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