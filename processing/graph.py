class Node:
    p = (0,0)
    neighbours = None
    tags = None
    def __init__(self, p):
        self.p = p
        
    def __repr__(self):
        return "Node " + str(self.p) + "\n Neighbours: " + str(len(self.neighbours)) + "\n Tags: " + str(self.tags)