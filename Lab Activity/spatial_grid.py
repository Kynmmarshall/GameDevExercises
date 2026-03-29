# spatial_grid.py
# SpatialGrid for efficient collision detection

from collections import defaultdict

class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = defaultdict(set)

    def _get_cell_coords(self, rect):
        x0 = rect.x // self.cell_size
        y0 = rect.y // self.cell_size
        x1 = (rect.x + rect.width) // self.cell_size
        y1 = (rect.y + rect.height) // self.cell_size
        return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]

    def clear(self):
        self.cells.clear()

    def insert(self, rect, obj):
        for cell in self._get_cell_coords(rect):
            self.cells[cell].add(obj)

    def get_nearby(self, rect):
        nearby = set()
        for cell in self._get_cell_coords(rect):
            nearby.update(self.cells.get(cell, set()))
        return nearby
