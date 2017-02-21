import processing as d
import graph as g
import vectorutils as vec
import sys

WATER = "water"
LAND = "land"
COASTLINE = "coastline"

def heightmap(x, y):
    return 2*noise(x*0.0025, y*0.0025) - 1

def min_unvisited_neighbour(x, points, sea_level, grid_size):
    neighbours = [(x[0]-1, x[1]), (x[0], x[1]-1), (x[0]+1, x[1]), (x[0], x[1]+1)]
    min_neighbour = None
    min_height = 1
    for n in neighbours:
        n = vec.toInt(n)
        if n[0] < 0 or n[0] >= grid_size[0] or n[1] < 0 or n[1] >= grid_size[1]:
            continue
        elif vec.inList(n, points) and not vec.equal(n, points[0]):
            continue
        elif len(points) > 1 and vec.equal(n, points[-2]):
            continue
        else:
            elevation = abs(noise(n[0], n[1]) - noise(x[0], x[1]))
            if elevation < min_height:
                min_height = elevation
                min_neighbour = n
    return min_neighbour

def random_walk(x, step_size, max_angle, grid_size):
    points = [x]
    angle = vec.angle(vec.subtract((grid_size[0]/2, grid_size[1]/2), x))
    while x[0] >= 0 and x[0] < grid_size[0] and x[1] >= 0 and x[1] < grid_size[1]:
        found_next = False
        while not found_next:
            delta = randomGaussian()
            if delta < -max_angle:
                delta = -max_angle
            if delta > max_angle:
                delta = max_angle
            centroid = vec.midpoint(points)
            from_centroid = vec.normalise(vec.subtract(x, centroid))
            angle += delta
            v = (step_size*cos(angle), step_size*sin(angle))
            v = vec.add(v, from_centroid)
            if not vec.intersectsLine(x, vec.add(x, vec.multiply(v, 2)), points):
                found_next = True
        x = vec.add(x, v)
        points.append(x)
        sys.stdout.write('.')
    print ("")
    return points

def random_offset(max_diameter):
    """ Return a normally distributed number up to +-max_diameter/2 """
    o = 0.25*max_diameter * randomGaussian()
    if o < -0.5*max_diameter:
        o = -0.5*max_diameter
    if o > 0.5*max_diameter:
        o = 0.5*max_diameter
    return o
    return 0

def get_islands(image_size, grid_spacing):
    """ Return: island outlines, heightmap as a graph """
    print "Creating grid..."
    grid = []
    for i in range(image_size[0]):
        grid.append([])
        for j in range(image_size[1]):
            grid[i].append( g.Node( (i*grid_spacing+random_offset(grid_spacing),
                                  j*grid_spacing+random_offset(grid_spacing)) ) )
            
    print "Adding neighbours..."
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            # Add right, down, left, up neighbours
            grid[i][j].neighbours = []
            if i < image_size[0]-1:
                grid[i][j].neighbours.append(grid[i+1][j])
            if j < image_size[1]-1:
                grid[i][j].neighbours.append(grid[i][j+1])
            if i > 0:
                grid[i][j].neighbours.append(grid[i-1][j])
            if j > 0:
                grid[i][j].neighbours.append(grid[i][j-1])
            # Add SE, SW, NW, NE neighbours
            if i < image_size[0]-1 and j < image_size[1]-1:
                grid[i][j].neighbours.append(grid[i+1][j+1])
            if i > 0 and j < image_size[1]-1:
                grid[i][j].neighbours.append(grid[i-1][j+1])
            if i > 0 and j > 0:
                grid[i][j].neighbours.append(grid[i-1][j-1])
            if i < image_size[0]-1 and j > 0:
                grid[i][j].neighbours.append(grid[i+1][j-1])
            # Set tags
            grid[i][j].tags = [LAND if heightmap(grid[i][j].p[0], grid[i][j].p[1]) > 0
                                   else WATER]
    
    print "Finding coastline..."
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            # Set coastline tag if we are land and a neighbour is sea
            if LAND in grid[i][j].tags:
                for n in grid[i][j].neighbours:
                    if WATER in n.tags:
                        grid[i][j].tags.append(COASTLINE)
    
    print "Filling random sides..."
    sides = round(random(4))
    # SE, SW, NW, NE = 0, 1, 2, 3
    # Fill right
    if sides == 0 or sides == 3:
        for j in range(image_size[1]):
            if COASTLINE not in grid[image_size[0]-1][j].tags:
                grid[image_size[0]-1][j].tags.append(COASTLINE)
    # Down
    if sides == 0 or sides == 1:
        for i in range(image_size[0]):
            if COASTLINE not in grid[i][image_size[1]-1].tags:
                grid[i][image_size[1]-1].tags.append(COASTLINE)
    # Left
    if sides == 1 or sides == 2:
        for j in range(image_size[1]):
            if COASTLINE not in grid[0][j].tags:
                grid[0][j].tags.append(COASTLINE)
    # Up
    if sides == 2 or sides == 3:
        for i in range(image_size[0]):
            if COASTLINE not in grid[i][0].tags:
                grid[i][0].tags.append(COASTLINE)
    
    print "Reducing coastline..."
    removed = 1
    while removed > 0:
        removed = 0
        for i in range(image_size[0]):
            for j in range(image_size[1]):
                if COASTLINE in grid[i][j].tags:
                    num_neighbours = len([n for n in grid[i][j].neighbours if COASTLINE in n.tags])
                    if num_neighbours < 2:
                        grid[i][j].tags.remove(COASTLINE)
                        removed += 1
                        
    print "Finding islands..."
    # Now find the island outlines
    processed_coastline_points = []
    islands = []
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            if (COASTLINE in grid[i][j].tags
                    and grid[i][j] not in processed_coastline_points):
                current_point = grid[i][j]
                current_island = [current_point]
                finished = False
                while not finished:
                    found_neighbour = False
                    for n in current_point.neighbours:
                        if n not in current_island and COASTLINE in n.tags:
                            current_island.append(n)
                            current_point = n
                            point(n.p[0], n.p[1])
                            found_neighbour = True
                            break
                    if not found_neighbour:
                        finished = True
                        if current_island[0] not in current_point.neighbours:
                            current_island = []
                    processed_coastline_points.append(current_point)
                    sys.stdout.write('.')
                if len(current_island) > 4:
                    islands.append(current_island)
    return islands, grid

def draw_island(grid_size):
    heightmap = [[0 for i in range(grid_size[1])] for j in range(grid_size[0])]
    side = round(random(4))
    x = (0,0)
    if side == 0:
        x = (0, round(random(grid_size[1])))
    if side == 1:
        x = (round(random(grid_size[0])), 0)
    if side == 2:
        x = (grid_size[0]-1, round(random(grid_size[1])))
    if side == 3:
        x = (round(random(grid_size[0])), grid_size[1]-1)
    points = [x]
    sea_level = noise(x[0], x[1])
    for i, row in enumerate(heightmap):
        for j, item in enumerate(row):
            heightmap[i][j] = noise(i, j)
    points = random_walk(x, 5, QUARTER_PI, grid_size)
    
    
    #while (min_unvisited_neighbour(x, points, sea_level, grid_size)):
    #    x = min_unvisited_neighbour(x, points, sea_level, grid_size)
    #    print("Point " + str(x))
    #    print("Elevation: " + str(noise(x[0], x[1])) + "/" + str(sea_level))
    #    print("Points: " + str(points))
    #    points.append(x)
        
    return points

def get_mountain_outline(a, b, first_target, steps):
    step_size = abs(b[0] - a[0])/float(steps)
    current_point = a
    points = [current_point]
    target = first_target
    for i in range(int(steps)):
        v = vec.normalise(vec.subtract(target, current_point))
        v = vec.multiply(v, step_size)
        delta = randomGaussian()
        v = (v[0] + cos(delta), v[1] + sin(delta))
        current_point = vec.add(current_point, v)
        points.append(current_point)
        target = vec.add(target, vec.multiply(vec.normalise(vec.subtract(b, target)), step_size))
    return points

def get_mountain_midline(a, w, h):
    max_y = a[1] + h
    current_point = a
    points = [current_point]
    while current_point[1] < max_y-15:
        max_w = 0.1*w*float(current_point[1]-a[1])/h
        current_point = (current_point[0] + randomGaussian()*max_w,
                         current_point[1] + 0.5*random(max_y-current_point[1]))
        points.append(current_point)
    if points[-1][1] > max_y:
        points = points[:-1]
    return points

def get_mountain_shading(midline, right_line, slope_vec):
    lines = []
    if len(midline) < 3:
        return []
    prev_point = midline[0]
    current_point = midline[1]
    for next_point in midline[2:]:
        if (current_point[0] <= prev_point[0] and
            current_point[0] < next_point[0]):
            lines.append([current_point, vec.add(current_point, (-slope_vec[0], slope_vec[1]))])
        prev_point = current_point
        current_point = next_point
    min_y = midline[0][1]
    max_y = midline[-1][1]
    max_x = right_line[-1][0]
    target = vec.between(midline[-1], right_line[-1], 0.5)
    for y in range(int(min_y)+2, int(max_y), 2):
        start_pos = vec.line_pos(midline, (None, y))
        end_pos = vec.line_pos(right_line, (None, y))
        end_pos = vec.between(start_pos, end_pos, 0.6)
        lines.append([start_pos, end_pos])
        lines.append([start_pos, vec.between(start_pos, target, 0.5)])
    return lines

def draw_mountain(x, y, w, h):
    """ Return left line, right line, middle line. """
    resolution = 16.
    grid_points_w = w/resolution
    grid_points_h = h/resolution 
    left_line = get_mountain_outline((x, y), (x-w*0.5, y+h), (x-w*0.25, y+h), grid_points_w)
    right_line = get_mountain_outline((x, y), (x+w*0.5, y+h), (x+w*0.25, y+h), grid_points_w)
    middle_line = get_mountain_midline((x, y), w, h)
    middle_line[-1] = (middle_line[-1][0], right_line[-1][1])
    return [left_line, right_line, middle_line]

def get_heightmap_adjustment_for_island(island):
    # Test the bounding box points. Most of them should be in the sea.
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    total = 0.
    for x in range(int(min_x), int(max_x), 5):
        total += heightmap(x, min_y) if int(min_y) > 0 else 0.
        total += heightmap(x, max_y) if int(max_y) < height else 0.
    for y in range(int(min_y), int(max_y), 5):
        total += heightmap(min_x, y) if int(min_x) > 0 else 0.
        total += heightmap(max_x, y) if int(max_x) < width else 0.
    h_sign = 1 if total < 0 else -1
    max_height = 0.
    for x in range(int(min_x), int(max_x), 5):
        for y in range(int(min_y), int(max_y), 5):
            if h_sign*heightmap(x, y) > max_height:
                max_height = h_sign*heightmap(x, y)
    if max_height == 0.:
        max_height = 1.
    h_scale = 1./max_height
    return h_scale, h_sign

def get_river(x, y, grid, h_scale, h_sign):
    current_node = g.closest_grid_node((x, y), grid)
    points = [current_node.p]
    while (COASTLINE not in current_node.tags
               or h_scale*h_sign*heightmap(current_node.p[0], current_node.p[1]) > 0):
        next_node = current_node.neighbours[0]
        next_h = h_scale*h_sign*heightmap(next_node.p[0], next_node.p[1])
        for n in current_node.neighbours[1:]:
            h = h_scale*h_sign*heightmap(n.p[0], n.p[1])
            if h < next_h:
                next_h = h
                next_node = n
        if len(points) > 1 and next_node.p == points[-2]:
            return []
        current_node = next_node
        points.append(current_node.p)
    return points

def shade_coastline(island):
    """ Return lists of points which are the coastline shading. """
    lines = []
    outline = [i.p for i in island] + [island[0].p]
    c_start = outline[0]
    for c_end in outline:
        line_start = vec.add(vec.midpoint([c_start, c_end]), (random_offset(5)-10, 0))
        line_end = vec.add(vec.midpoint([c_start, c_end]), (random_offset(5)+10, 0))
        if len(lines) == 0 or abs(line_start[1] - lines[-1][0][1]) > 1:
            lines.append([line_start, line_end])
        c_start = c_end
    return lines