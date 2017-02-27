import processing as d
import graph as g
import vectorutils as vec
import sys

WATER = "water"
LAND = "land"
COASTLINE = "coastline"

def heightmap(x, y):
    return 2*noise(x*0.0025, y*0.0025) - 1

def random_offset(max_diameter):
    """ Return a normally distributed number up to +-max_diameter/2 """
    o = 0.25*max_diameter * randomGaussian()
    if o < -0.5*max_diameter:
        o = -0.5*max_diameter
    if o > 0.5*max_diameter:
        o = 0.5*max_diameter
    return o

def get_islands(image_size, grid_spacing):
    """ Return: island outlines plus the grid with info. """
    grid = []
    for i in range(image_size[0]):
        grid.append([])
        for j in range(image_size[1]):
            grid[i].append(g.Node( (i*grid_spacing+random_offset(grid_spacing),
                                  j*grid_spacing+random_offset(grid_spacing)) ))
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
            grid[i][j].tags = [LAND if heightmap(grid[i][j].p[0],
                                                 grid[i][j].p[1]) > 0
                                   else WATER]
    
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            # Set coastline tag if we are land and a neighbour is sea
            if LAND in grid[i][j].tags:
                for n in grid[i][j].neighbours:
                    if WATER in n.tags:
                        grid[i][j].tags.append(COASTLINE)
    
    # Fill in three random sides of the image to make it more likely that
    # coastlines will join up. (hackiness levels at 85%)
    sides = round(random(4))
    # NES, SEW, NWS, NEW = 0, 1, 2, 3
    # Fill E
    if sides == 0 or sides == 1 or sides == 3:
        for j in range(image_size[1]):
            if COASTLINE not in grid[image_size[0]-1][j].tags:
                grid[image_size[0]-1][j].tags.append(COASTLINE)
    # S
    if sides == 0 or sides == 1 or sides == 2:
        for i in range(image_size[0]):
            if COASTLINE not in grid[i][image_size[1]-1].tags:
                grid[i][image_size[1]-1].tags.append(COASTLINE)
    # W
    if sides == 1 or sides == 2 or sides == 3:
        for j in range(image_size[1]):
            if COASTLINE not in grid[0][j].tags:
                grid[0][j].tags.append(COASTLINE)
    # N
    if sides == 0 or sides == 2 or sides == 3:
        for i in range(image_size[0]):
            if COASTLINE not in grid[i][0].tags:
                grid[i][0].tags.append(COASTLINE)
    
    # Now reduce the coastline by repeatedly removing dead ends. (90%)
    removed = 1
    while removed > 0:
        removed = 0
        for i in range(image_size[0]):
            for j in range(image_size[1]):
                if COASTLINE in grid[i][j].tags:
                    num_neighbours = len([n for n in grid[i][j].neighbours
                                          if COASTLINE in n.tags])
                    if num_neighbours < 2:
                        grid[i][j].tags.remove(COASTLINE)
                        removed += 1
                        
    print "Finding islands..."
    # Now find the island outlines by choosing a point and then exploring until
    # you get back to your starting point. (110%)
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
                            found_neighbour = True
                            break
                    if not found_neighbour:
                        finished = True
                        if current_island[0] not in current_point.neighbours:
                            current_island = []
                    processed_coastline_points.append(current_point)
                if len(current_island) > 4:
                    islands.append(current_island)
    return islands, grid

def get_mountain_outline(a, b, first_target, steps):
    """
    Return a set of points representing a mountainside.
    (you need to do this for each side of the mountain)
    The points will lead from a to b.
    Last point not guaranteed to be exactly b.
    """
    step_size = sqrt(pow(abs(b[0]-a[0]),2)+pow(abs(b[1]-a[1]),2))/float(steps)
    current_point = a
    points = [current_point]
    target = first_target
    for i in range(int(steps)):
        v = vec.normalise(vec.subtract(target, current_point))
        v = vec.multiply(v, step_size)
        delta = random(TWO_PI)
        v = (v[0] + cos(delta), v[1] + sin(delta))
        current_point = vec.add(current_point, v)
        points.append(current_point)
        target = (lerp(first_target[0], b[0], float(i)/steps), b[1])
    return points

def get_mountain_midline(a, w, h):
    """
    Return a wiggly line that tries to stay within the isosceles triangle with
    top point a, height h and base width w.
    """
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
            lines.append([current_point,
                          vec.add(current_point,
                                  (-slope_vec[0], slope_vec[1]))])
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
        if start_pos[1] > right_line[0][1] and end_pos[1] > right_line[0][1]:
            lines.append([start_pos, end_pos])
        lines.append([start_pos, vec.between(start_pos, target, 0.5)])
    return lines

def draw_mountain(x, y, w, h):
    """ Return left line, right line, middle line. """
    resolution = 10.
    grid_points_w = w/resolution
    grid_points_h = h/resolution 
    left_line = get_mountain_outline((x, y), (x-w*0.5, y+h),
                                     (x-w*0.25, y+h), grid_points_w)
    right_line = get_mountain_outline((x, y), (x+w*0.5, y+h),
                                      (x+w*0.25, y+h), grid_points_w)
    middle_line = get_mountain_midline((x, y), w, h)
    middle_line[-1] = (middle_line[-1][0], right_line[-1][1])
    return [left_line, right_line, middle_line]

def get_heightmap_adjustment_for_island(island):
    # Test the bounding box points. Most of them should be in the sea.
    min_x, min_y, max_x, max_y = vec.get_bounds([node.p for node in island])
    total = 0.
    for x in range(int(min_x), int(max_x), 5):
        total += heightmap(x, min_y) if int(min_y) > 0 else 0.
        total += heightmap(x, max_y) if int(max_y) < height-10 else 0.
    for y in range(int(min_y), int(max_y), 5):
        total += heightmap(min_x, y) if int(min_x) > 0 else 0.
        total += heightmap(max_x, y) if int(max_x) < width-10 else 0.
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
    """
    Return points describing a river starting from the grid point closest
    to (x, y).
    """
    current_node = g.closest_grid_node((x, y), grid)
    points = [current_node.p]
    while (COASTLINE not in current_node.tags
               and h_scale*h_sign*heightmap(current_node.p[0],
                                                current_node.p[1]) > 0):
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
        current_node.water_level += 1
    return points

def shade_coastline(island):
    """ Return lists of points which are the coastline hatching. """
    lines = []
    outline = [i.p for i in island] + [island[0].p]
    c_start = outline[0]
    for c_end in outline:
        line_start = vec.add(vec.midpoint([c_start, c_end]),
                             (random_offset(5)-10, 0))
        line_end = vec.add(vec.midpoint([c_start, c_end]),
                           (random_offset(5)+10, 0))
        if len(lines) == 0 or abs(line_start[1] - lines[-1][0][1]) > 2:
            lines.append([line_start, line_end])
        c_start = c_end
    return lines