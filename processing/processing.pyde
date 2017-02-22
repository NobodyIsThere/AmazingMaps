import amazing_maps
import graph as g
import name_generator
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

def clarity(x, y, w, h):
    loadPixels()
    totals = {}
    for j in range(int(y), int(y+h)):
        for i in range(int(x), int(x+w)):
            c = pixels[j*width+i]
            if not c in totals.keys():
                totals[c] = 1
            else:
                totals[c] += 1
    return float(max(totals.values()))/w*h

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
    outline = m[0] + m[1] #+ [m[2][-1]]
    m[0].reverse()
    noStroke()
    beginShape()
    for p in outline:
        vertex(p[0], p[1])
    endShape(CLOSE)
    rect(m[0][-1][0], m[0][-1][1]-1, m[1][-1][0]-m[0][-1][0], 3)
    stroke(0)
    for i in m:
        l = Line(i)
        l.w = 3
        l.sublines = 3
        l.end_small = True
        produce([l])
    # Shade the mountain
    slope_vec = vec.subtract((0.5*(m[1][-1][0]+m[1][0][0]), m[1][-1][1]), m[1][0])
    slope_vec = vec.multiply(vec.normalise(slope_vec), 10)
    s = amazing_maps.get_mountain_shading(m[2], m[1], slope_vec)
    #stroke(255, 0, 0)
    for i in s:
        l = Line(i)
        l.w = 2
        l.sublines = 2
        l.end_small = True
        produce([l])
    #stroke(0)

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

def find_label_position(p, r, h, name):
    """ Find a place to put a label 'name' (size h) at a distance ~r away from p """
    w = textWidth(name)
    best_pos = (p[0], p[1]+r)
    best_align = (CENTER, TOP)
    best_clarity = 0.
    # S
    prop = clarity(p[0]-0.5*w, p[1]+r, w, h)
    if prop > best_clarity:
        best_clarity = prop
    # N
    prop = clarity(p[0]-0.5*w, p[1]-r-h, w, h)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0], p[1]-r)
        best_align = (CENTER, BOTTOM)
    # W
    prop = clarity(p[0]-r-w, p[1]-0.5*h, w, h)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]-r, p[1])
        best_align = (RIGHT, CENTER)
    # E
    prop = clarity(p[0]+r, p[1]-0.5*h, w, h)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]+r, p[1])
        best_align = (LEFT, CENTER)
    return best_pos, best_align

size(1280, 960)
#coastline_points = amazing_maps.draw_island((640, 480))
#l = Line(coastline_points)
#l.w = 2
#l.sublines = 2
#produce([l])
islands, grid = amazing_maps.get_islands((256, 192), 5)
print "Removing nested islands..."
same_island_dist = 20
to_remove = []
for i, island in enumerate(islands):
    x, y, max_x, max_y = vec.get_bounds([node.p for node in island])
    w = max_x-x
    h = max_y-y
    """stroke(255, 0, 0)
    noFill()
    rect(x, y, w, h)
    stroke(0)
    fill(255)"""
    for other_island in islands[i:]:
        if island is not other_island:
            ox, oy, max_x, max_y = vec.get_bounds([node.p for node in other_island])
            ow = max_x-ox
            oh = max_y-oy
            if (vec.rect_within((x, y, w, h), (ox, oy, ow, oh))
                    or vec.distance((x+0.5*w, y+0.5*h), (ox+0.5*ow, oy+0.5*oh)) < same_island_dist):
                to_remove.append(island)
                break
for island in to_remove:
    islands.remove(island)
print "Number of islands: ", len(islands)

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
default_mountain_width = 90
default_mountain_height = 40
bounding_scale = 1.5
mountain_positions = []
same_mountain_threshold = 10.
for island in islands:
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
                mountain_y = y-default_mountain_height*mountain_scale
                # Check that there is space for a mountain here
                if vec.rect_within((x-default_mountain_width*bounding_scale*0.5*mountain_scale,
                                    y-default_mountain_height*bounding_scale*mountain_scale,
                                    default_mountain_width*bounding_scale*mountain_scale,
                                    default_mountain_height*bounding_scale*mountain_scale),
                                    (min_x, min_y, max_x-min_x, max_y-min_y)):
                    # Check that there isn't already a mountain here
                    for mountain in mountain_positions:
                        if vec.distance((x, mountain_y), mountain) < same_mountain_threshold:
                            break
                    else:
                        draw_mountain(x+random(mountain_spacing_x)-mountain_spacing_x*0.5,
                                      mountain_y, default_mountain_width*mountain_scale,
                                      default_mountain_height*mountain_scale)
                        mountain_positions.append((x, mountain_y))
# Let's do cities now.
print "Creating cities..."
city_spacing = 30
city_size = 8
cities = []
fill(0)
for island in islands:
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    h_scale, h_sign = amazing_maps.get_heightmap_adjustment_for_island(island)
    for y in range(int(min_y), int(max_y), city_spacing):
        for x in range(int(min_x), int(max_x), city_spacing):
            h = h_scale*h_sign*amazing_maps.heightmap(x, y)
            if (h > 0 and h < 0.5) or g.closest_grid_node((x, y), grid).water_level > 1:
                # Good place for a city
                if random(1) > 0.9:
                    print "Drawing a city!"
                    rect(x-city_size/2, y-city_size/2, city_size, city_size)
                    cities.append((x, y))
# Labels
print "Labelling map..."
georgia = createFont("georgia.ttf", 32, True)
georgia_bold = createFont("georgia_bold.ttf", 32, True)
textFont(georgia)
h = 12
textSize(h)
for city in cities:
    name = name_generator.generate_name("city")
    name = name.upper()
    print name
    pos, align = find_label_position(city, 10, h, name)
    textAlign(align[0], align[1])
    text(name, pos[0], pos[1])
fill(255)
print ("Done.")