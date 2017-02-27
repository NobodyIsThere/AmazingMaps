import amazing_maps as maps
import drawutils as d
import graph as g
import name_generator
import sys
import vectorutils as vec
    
def draw_mountain(x, y, w, h):
    """ Draw a mountain at (x, y) of size (w, h) """
    m = maps.draw_mountain(x, y, w, h)
    # First white-out the area within the mountain.
    m[0].reverse()
    outline = m[0] + m[1] #+ [m[2][-1]]
    m[0].reverse()
    noStroke()
    fill(255)
    beginShape()
    for p in outline:
        vertex(p[0], p[1])
    endShape(CLOSE)
    # Also white-out a small area beneath (helps when two mountains of different
    # sizes slightly overlap). 2 is a magic number.
    rect(m[0][-1][0], m[0][-1][1]-1,
         m[1][-1][0]-m[0][-1][0], h+2-(m[0][-1][1]-m[0][0][1]))
    stroke(0)
    d.create_and_produce(m, 3, 3, False, True)
    # Shade the mountain.
    slope_vec = vec.subtract((0.5*(m[1][-1][0]+m[1][0][0]), m[1][-1][1]),
                             m[1][0])
    slope_vec = vec.multiply(vec.normalise(slope_vec), 10)
    shading = maps.get_mountain_shading(m[2], m[1], slope_vec)
    d.create_and_produce(shading, 2, 2, False, True)

def draw_hill(x, y):
    """ Draw a small hill at (x, y) """
    hill_width = 16
    hill_height = 4
    # White-out (approximate) area under hill
    noStroke()
    fill(255)
    beginShape()
    vertex(x-hill_width/2, y)
    vertex(x, y-hill_height)
    vertex(x+hill_width/2, y)
    endShape(CLOSE)
    # And also a small rectangle underneath, just to be on the safe side.
    rect(x-hill_width/2, y, hill_width, 2)
    stroke(0)
    l = d.Line([(x-hill_width/2, y), (x+hill_width/2, y)])
    l.midpoints = [(x, y-hill_height)]
    l.w = 2
    l.sublines = 2
    l.start_small = True
    l.end_small = True
    d.produce([l])

def draw_river(points):
    if len(points) == 0:
        return
    l = d.Line(points[0:-1:2])
    l.midpoints = points[1:-1:2]
    l.points.append(points[-1])
    l.w = 2
    l.sublines = 2
    l.start_small = True
    d.produce([l])

def find_label_position(p, r, h, name):
    """
    Find a place to put a label with text 'name' (text size h) at a distance ~r
    away from p.
    """
    w = textWidth(name)
    border = 4
    w += border
    h += border
    best_pos = (p[0], p[1]+r)
    best_align = (CENTER, TOP)
    best_clarity = 0
    # S
    prop = int(d.clarity(p[0]-0.5*w, p[1]+r, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
    # N
    prop = int(d.clarity(p[0]-0.5*w, p[1]-r-h, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0], p[1]-r)
        best_align = (CENTER, BOTTOM)
    # W
    prop = int(d.clarity(p[0]-r-w, p[1]-0.5*h, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]-r, p[1])
        best_align = (RIGHT, CENTER)
    # E
    prop = int(d.clarity(p[0]+r, p[1]-0.5*h, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]+r, p[1])
        best_align = (LEFT, CENTER)
    # SE
    prop = int(d.clarity(p[0]+r, p[1]+r, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]+r, p[1]+r)
        best_align = (LEFT, TOP)
    # SW
    prop = int(d.clarity(p[0]-r-w, p[1]+r, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]-r, p[1]+r)
        best_align = (RIGHT, TOP)
    # NE
    prop = int(d.clarity(p[0]+r, p[1]-r-h, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]+r, p[1]-r)
        best_align = (LEFT, BOTTOM)
    # NW
    prop = int(d.clarity(p[0]-r-w, p[1]-r-h, w, h)*100)
    if prop > best_clarity:
        best_clarity = prop
        best_pos = (p[0]-r, p[1]-r)
        best_align = (RIGHT, BOTTOM)
    return best_pos, best_align

def remove_nested_islands(islands):
    """
    Sometimes we get islands inside other islands. Until I improve the island
    creation algorithm, just check for and remove these nested islands.
    """
    same_island_dist = 20 # Islands with centres closer than this are the same.
    to_remove = []
    for i, island in enumerate(islands):
        x, y, max_x, max_y = vec.get_bounds([node.p for node in island])
        w = max_x-x
        h = max_y-y
        for other_island in islands:
            if island is not other_island and other_island not in to_remove:
                ox, oy, max_x, max_y = vec.get_bounds(
                                            [node.p for node in other_island])
                ow = max_x-ox
                oh = max_y-oy
                if (vec.rect_within((x, y, w, h), (ox, oy, ow, oh))
                        or vec.distance((x+0.5*w, y+0.5*h),
                                        (ox+0.5*ow, oy+0.5*oh))
                            < same_island_dist):
                    to_remove.append(island)
                    break
    for island in to_remove:
        islands.remove(island)
    return islands

def draw_islands(islands):
    for island in islands:
        # Coastline hatching
        coastline_shading = maps.shade_coastline(island)
        d.create_and_produce(coastline_shading, 2, 3, True, True)
        # White-out island
        beginShape()
        for node in island:
            vertex(node.p[0], node.p[1])
        endShape(CLOSE)
        # Draw coastline
        l = d.Line([i.p for i in island] + [island[0].p])
        l.w = 3
        l.sublines = 6
        d.produce([l])

def draw_mountains(islands, grid):
    """ Draw rivers, hills and mountains. """
    mountain_spacing_x = 30
    mountain_spacing_y = 20
    default_mountain_width = 90
    default_mountain_height = 40
    bounding_scale = 1.5 # How much extra room to check for
    mountain_positions = []
    same_mountain_threshold = 10. # No mountains will be closer than this
    for island in islands:
        # Rivers
        min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
        h_scale, h_sign = maps.get_heightmap_adjustment_for_island(island)
        for y in range(int(min_y), int(max_y), mountain_spacing_y):
            for x in range(int(min_x), int(max_x), mountain_spacing_x):
                h = h_scale*h_sign*maps.heightmap(x, y)
                if h > 0.5:
                    # We could start a river here
                    if random(1) > 0.9:
                        river = maps.get_river(x, y, grid, h_scale, h_sign)
                        draw_river(river)
        # Hills and mountains
        for y in range(int(min_y), int(max_y), mountain_spacing_y):
            for x in range(int(min_x), int(max_x), mountain_spacing_x):
                h = h_scale*h_sign*maps.heightmap(x, y)
                if h > 0.5 and h < 0.75:
                    # We could draw a hill here.
                    if random(1) > 0.5:
                        hill_x = x + (random(mountain_spacing_x)
                                      -0.5*mountain_spacing_x)
                        if vec.rect_within((hill_x-8, y-4, 16, 4),
                                           (min_x, min_y,
                                                max_x-min_x, max_y-min_y)):
                            draw_hill(hill_x, y)
                if h > 0.75:
                    mountain_scale = min(h, 1)
                    mountain_y = y-default_mountain_height*mountain_scale
                    # Check that there is space for a mountain here
                    if vec.rect_within((x-default_mountain_width*
                                        bounding_scale*0.5*mountain_scale,
                                        y-default_mountain_height*
                                        bounding_scale*mountain_scale,
                                        default_mountain_width*
                                        bounding_scale*mountain_scale,
                                        default_mountain_height*
                                        bounding_scale*mountain_scale),
                                        (min_x, min_y,
                                             max_x-min_x, max_y-min_y)):
                        # Check that there isn't already a mountain here
                        for mountain in mountain_positions:
                            if (vec.distance((x, mountain_y), mountain)
                                    < same_mountain_threshold):
                                break
                        else:
                            draw_mountain(x+random(mountain_spacing_x)-
                                        mountain_spacing_x*0.5,
                                        mountain_y,
                                        default_mountain_width*mountain_scale,
                                        default_mountain_height*mountain_scale)
                            mountain_positions.append((x, mountain_y))
                            
def draw_cities(islands, grid):
    city_spacing = 30
    city_size = 8
    cities = []
    for island in islands:
        min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
        h_scale, h_sign = maps.get_heightmap_adjustment_for_island(island)
        for y in range(int(min_y), int(max_y), city_spacing):
            for x in range(int(min_x), int(max_x), city_spacing):
                h = h_scale*h_sign*maps.heightmap(x, y)
                if h > 0 and (h < 0.5 or
                            g.closest_grid_node((x, y), grid).water_level > 1):
                    # Good place for a city
                    if random(1) > 0.9:
                        stroke(255)
                        fill(0)
                        rect(x-city_size/2, y-city_size/2, city_size, city_size)
                        cities.append((x, y))
    return cities

size(1280, 960)
islands = []
grid = []
l = 0
while l < 400:
    noiseSeed(long(random(2147483647)))
    islands, grid = maps.get_islands((256, 192), 5)
    islands = remove_nested_islands(islands)
    l = sum([len(island) for island in islands])
    if l < 400:
        print "THAT'S NOT GOOD ENOUGH"
print "Number of islands: ", len(islands)
print "Drawing islands..."
draw_islands(islands)

# Now let's do some mountains
print "Adding mountain ranges and rivers..."
draw_mountains(islands, grid)

# Let's do cities now.
print "Creating cities..."
cities = draw_cities(islands, grid)

# Labels
print "Labelling map..."
sys.stdout.write("Naming cities...")
georgia = createFont("georgia.ttf", 32, True)
georgia_bold = createFont("georgia_bold.ttf", 32, True)
textFont(georgia)
h = 12
textSize(h)
fill(0)
for city in cities:
    name = name_generator.generate_name("city")
    name = name.upper()
    sys.stdout.write(name + '...')
    pos, align = find_label_position(city, 8, h, name)
    textAlign(align[0], align[1])
    text(name, pos[0], pos[1])

print ""
sys.stdout.write("Naming regions...")
region_spacing = 20
textFont(georgia_bold)
h = 16
textSize(h)
textAlign(LEFT, TOP)
next_name = name_generator.generate_name("city").upper()
w = textWidth(next_name)
for island in islands:
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    h_scale, h_sign = maps.get_heightmap_adjustment_for_island(island)
    for y in range(int(min_y), int(max_y), region_spacing):
        for x in range(int(min_x), int(max_x), region_spacing):
            elev = h_scale*h_sign*maps.heightmap(x, y)
            if (d.clarity(x-10, y-10, w+20, h+20) > 0.99 and elev > 0
                    and random(1) > 0.5):
                text(next_name, x, y)
                sys.stdout.write(next_name + "...")
                next_name = name_generator.generate_name("city").upper()
                w = textWidth(next_name)

print ""
sys.stdout.write("Naming islands...")
h = 18
textSize(h)
textAlign(CENTER, TOP)
for island in islands:
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    name = name_generator.generate_name("city").upper()
    w = textWidth(name)
    if d.clarity(0.5*(max_x+min_x-w), max_y+20, w, h) > 0.95:
        text(name, 0.5*(max_x+min_x), max_y+20)
        sys.stdout.write(name + "...")

print ""
print "Applying paper texture..."
blendMode(MULTIPLY)
img = loadImage("paper.jpg")
image(img, 0, 0, width, height)
blendMode(NORMAL)
print ("Done.")