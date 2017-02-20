import amazing_maps
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

size(1280, 960)
#coastline_points = amazing_maps.draw_island((640, 480))
#l = Line(coastline_points)
#l.w = 2
#l.sublines = 2
#produce([l])
islands, grid = amazing_maps.get_islands((256, 192), 5)
for island in islands:
    print "Shading coastline..."
    coastline_shading = amazing_maps.shade_coastline(island)
    for c in coastline_shading:
        #print c
        l = Line(c)
        #print l
        l.w = 2
        l.sublines = 2
        l.start_small = True
        l.end_small = True
        produce([l])
    print "Drawing islands..."
    beginShape()
    for node in island:
        vertex(node.p[0], node.p[1])
    endShape(CLOSE)
    print "Outlining islands..."
    l = Line([i.p for i in island] + [island[0].p])
    l.w = 2
    l.sublines = 2
    produce([l])
# Now let's do some mountains


print ("Done.")