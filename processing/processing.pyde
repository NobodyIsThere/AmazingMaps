import amazing_maps
import graph as g
import sys
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
    
def draw_mountain(x, y, w, h):
    """ Example input: (100, 100, 100, 50) """
    m = amazing_maps.draw_mountain(x, y, w, h)
    m[0].reverse()
    outline = m[0] + m[1] + [m[2][-1]]
    m[0].reverse()
    noStroke()
    beginShape()
    for p in outline:
        vertex(p[0], p[1])
    endShape(CLOSE)
    stroke(0)
    for i in m:
        l = Line(i)
        l.w = 3
        l.sublines = 3
        l.end_small = True
        produce([l])
    # Shade the mountain
    s = amazing_maps.get_mountain_shading(m[2], m[1],
                                    vec.multiply(vec.normalise(vec.subtract(m[1][-1], m[1][0])), 10))
    for i in s:
        l = Line(i)
        l.w = 2
        l.sublines = 2
        l.end_small = True
        produce([l])

def draw_river(points):
    if len(points) == 0:
        return
    l = Line(points[0:-1:2])
    l.midpoints = points[1:-1:2]
    l.points.append(points[-1])
    l.w = 2
    l.sublines = 2
    l.start_small = True
    produce([l])

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
    print "Drawing island..."
    beginShape()
    for node in island:
        vertex(node.p[0], node.p[1])
    endShape(CLOSE)
    print "Outlining island..."
    l = Line([i.p for i in island] + [island[0].p])
    l.w = 2
    l.sublines = 2
    produce([l])
h_sign = 1.
if len(islands) == 0:
    noStroke()
    rect(0, 0, width, height)
    stroke(0)
    islands = [[g.Node((0,0)), g.Node((width, 0)), g.Node((width, height)), g.Node((0, height))]]
h_scale = 1.
# Now let's do some mountains
print "Adding mountain ranges..."
mountain_spacing_x = 30
mountain_spacing_y = 20
mountain_positions = []
same_mountain_threshold = 10.
for island in islands:
    if len(islands) > 1:
        p = vec.midpoint([node.p for node in island])
        centre_height = amazing_maps.heightmap(p[0], p[1])
        h_scale = abs(1./centre_height)
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    h_scale, h_sign = amazing_maps.get_heightmap_adjustment_for_island(island)
    for y in range(int(min_y), int(max_y), mountain_spacing_y):
        for x in range(int(min_x), int(max_x), mountain_spacing_x):
            h = h_scale*h_sign*amazing_maps.heightmap(x, y)
            if h > 0.5:
                # We could start a river here
                if random(1) > 0.9:
                    print "Drawing a river!"
                    river = amazing_maps.get_river(x, y, grid, h_scale, h_sign)
                    draw_river(river)
    for y in range(int(min_y), int(max_y), mountain_spacing_y):
        for x in range(int(min_x), int(max_x), mountain_spacing_x):
            h = h_scale*h_sign*amazing_maps.heightmap(x, y)
            if h > 0.75:
                sys.stdout.write('.')
                mountain_scale = min(h, 1)
                mountain_y = y-50*mountain_scale
                # Check that there is space for a mountain here
                if vec.rect_within((x-60*mountain_scale, y-60*mountain_scale, 120*mountain_scale, 60*mountain_scale),
                                    (min_x, min_y, max_x-min_x, max_y-min_y)):
                    # Check that there isn't already a mountain here
                    for mountain in mountain_positions:
                        if vec.distance((x, mountain_y), mountain) < same_mountain_threshold:
                            break
                    else:
                        draw_mountain(x+random(mountain_spacing_x)-mountain_spacing_x*0.5,
                                      mountain_y, 100*mountain_scale, 50*mountain_scale)
                        mountain_positions.append((x, mountain_y))
print ("Done.")