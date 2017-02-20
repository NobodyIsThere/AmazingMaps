import processing as d
import graph as g
import vectorutils as vec
import sys

WATER = "water"
LAND = "land"
COASTLINE = "coastline"

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
            grid[i][j].tags = [LAND if noise(grid[i][j].p[0]*0.005, grid[i][j].p[1]*0.005) > 0.4
                                   else WATER]
    
    print "Finding coastline..."
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            # Set coastline tag if we are land and a neighbour is sea
            if LAND in grid[i][j].tags:
                for n in grid[i][j].neighbours:
                    if WATER in n.tags:
                        grid[i][j].tags.append(COASTLINE)
    
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
                if len(current_island) > 2:
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

def shade_coastline(coastline):
    """ Return LINES which are the coastline shading. """
    