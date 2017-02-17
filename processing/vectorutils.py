def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def angle(a):
    return atan2(a[1], a[0])

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
    if l1[0][0] == 0:
        c1 = l1[0][1]
    else:
        c1 = l1[0][1] - m1*l1[0][0]
    if l2[0][0] == 0:
        c2 = l2[0][1]
    else:
        c2 = l2[0][1] - m2*l2[0][0]
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

def slope(l):
    """ Returns "m" as in y = mx + c for line l[0] -> l[1] """
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