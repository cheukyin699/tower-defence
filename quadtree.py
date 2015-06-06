# File: quadtree.py

class QuadTree:
    # Maximum capacity for it
    MaxCapacity = 25
    def __init__(self, SIZE):
        # Some values
        self.vals = []

        # Children
        self.topleft = None
        self.topright = None
        self.lowerleft = None
        self.lowerright = None
