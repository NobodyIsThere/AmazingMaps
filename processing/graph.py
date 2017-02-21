import vectorutils as vec

class Node:
    p = (0,0)
    neighbours = None
    tags = None
    def __init__(self, p):
        self.p = p
        
    def __repr__(self):
        return "Node " + str(self.p) + "\n Neighbours: " + str(len(self.neighbours)) + "\n Tags: " + str(self.tags)
    
def closest_grid_node(p, grid):
    closest_node = grid[0][0]
    min_distance = vec.distance(p, closest_node.p)
    for row in grid:
        for node in row:
            d = vec.distance(node.p, p)
            if d < min_distance:
                min_distance = d
                closest_node = node
    return closest_node