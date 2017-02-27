import vectorutils as vec

class Line:
    w = 10
    sublines = w*2
    points = []
    tags = []
    midpoints = []
    start_small = False
    end_small = False
    def __init__(self, points):
        self.points = points
    def __repr__(self):
        return "Line " + str(self.points)

def get_spline_pos(p, r, prop):
    x = p[0] + r*prop*cos(prop*2*PI)
    y = p[1] + r*prop*sin(prop*2*PI)
    return (x, y)
        
def draw_spline(a, b, c):
    curve(a[0], a[1], a[0], a[1], b[0], b[1], c[0], c[1])
    curve(a[0], a[1], b[0], b[1], c[0], c[1], c[0], c[1])

def brush(l):
    x = l.points[0]
    min_size = 0.5*l.w
    for i, p in enumerate(l.points[1:]):
        midpoint = None
        if len(l.midpoints) > i:
            midpoint = l.midpoints[i]
        if midpoint == None:
            midpoint = vec.between(x, p, 0.5)
        midpoint_size = l.w/vec.distance(x, p)
        if midpoint_size < min_size:
            midpoint_size = min_size
        start_size = 0.5*l.w
        end_size = 0.5*l.w
        if x == l.points[0] and l.start_small:
            start_size = 0.
        if p == l.points[-1] and l.end_small:
            end_size = 0.
        for i in range(l.sublines):
            prop = float(i)/l.sublines
            spline_start = get_spline_pos(x, start_size, prop)
            spline_mid = get_spline_pos(midpoint, midpoint_size/2, prop)
            spline_end = get_spline_pos(p, end_size, prop)
            draw_spline(spline_start, spline_mid, spline_end)
        x = p

def clarity(x, y, w, h):
    if x+w > width or x<0 or y+h > height or y<0:
        return 0.
    loadPixels()
    totals = {}
    for j in range(int(y), int(y+h)):
        for i in range(int(x), int(x+w)):
            c = pixels[j*width+i]
            if not (c in totals.keys()):
                totals[c] = 1
            else:
                totals[c] += 1
    return float(max(totals.values()))/(w*h)

def create_and_produce(point_sets, w, sublines, start_small, end_small):
    for i in point_sets:
        l = Line(i)
        l.w = w
        l.sublines = sublines
        l.start_small = start_small
        l.end_small = end_small
        produce([l])

def produce(lines):
    for l in lines:
        brush(l)

def demo():
    l = Line([(15,6), (50,6), (40,20)])
    m = Line([(30,15), (12,40)])
    l.end_small = True
    m.end_small = True
    m.midpoints = [(27, 25)]
    
    n = Line([(6,50), (300,50)])
    produce([l, m, n])