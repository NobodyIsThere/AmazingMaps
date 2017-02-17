import processing as d
import vectorutils as vec
import sys

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
    
