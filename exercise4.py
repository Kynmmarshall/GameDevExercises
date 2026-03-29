# Exercise 4: Collision Detection and Spatial Partitioning
#
# 1. AABB (Axis-Aligned Bounding Box) collision detection checks if two rectangles overlap by comparing their edges.
#    For rectangles A and B:
#    A and B overlap if:
#        A.left < B.right and A.right > B.left and A.top < B.bottom and A.bottom > B.top
#    Where:
#        left = x, right = x + width, top = y, bottom = y + height
#
# 2. rect_collide(rect1, rect2):
def rect_collide(rect1, rect2):
	return (
		rect1.x < rect2.x + rect2.width and
		rect1.x + rect1.width > rect2.x and
		rect1.y < rect2.y + rect2.height and
		rect1.y + rect1.height > rect2.y
	)

# 3. SpatialGrid class
from collections import defaultdict
import pygame

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

# 4. Benchmarking and demonstration
import random
import time

def benchmark(num_rects=200, cell_size=64, frames=1000, width=800, height=600, visualize=False):
	pygame.init()
	screen = pygame.display.set_mode((width, height)) if visualize else None
	rects = []
	velocities = []
	for _ in range(num_rects):
		w, h = random.randint(20, 40), random.randint(20, 40)
		x, y = random.randint(0, width - w), random.randint(0, height - h)
		rects.append(pygame.Rect(x, y, w, h))
		vx, vy = random.randint(-3, 3), random.randint(-3, 3)
		velocities.append([vx, vy])

	grid = SpatialGrid(cell_size)
	brute_checks_total = 0
	grid_checks_total = 0

	for frame in range(frames):
		# Move rectangles
		for i, rect in enumerate(rects):
			rect.x += velocities[i][0]
			rect.y += velocities[i][1]
			# Bounce off walls
			if rect.x < 0 or rect.x + rect.width > width:
				velocities[i][0] *= -1
			if rect.y < 0 or rect.y + rect.height > height:
				velocities[i][1] *= -1
			rect.x = max(0, min(rect.x, width - rect.width))
			rect.y = max(0, min(rect.y, height - rect.height))

		# Brute-force collision checks
		brute_checks = 0
		for i in range(num_rects):
			for j in range(i + 1, num_rects):
				brute_checks += 1
				_ = rect_collide(rects[i], rects[j])
		brute_checks_total += brute_checks

		# Grid-based collision checks
		grid.clear()
		for i, rect in enumerate(rects):
			grid.insert(rect, i)
		grid_checks = 0
		checked_pairs = set()
		for i, rect in enumerate(rects):
			for j in grid.get_nearby(rect):
				if i < j and (i, j) not in checked_pairs:
					grid_checks += 1
					_ = rect_collide(rects[i], rects[j])
					checked_pairs.add((i, j))
		grid_checks_total += grid_checks

		if visualize:
			screen.fill((30, 30, 30))
			for rect in rects:
				pygame.draw.rect(screen, (0, 200, 0), rect, 2)
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return

	print(f"Brute-force: avg checks/frame = {brute_checks_total // frames}")
	print(f"Grid-based: avg checks/frame = {grid_checks_total // frames}")
	if visualize:
		pygame.quit()

if __name__ == "__main__":
	benchmark(visualize=True)

# Analysis:
# Using a spatial grid reduces the number of collision checks per frame dramatically compared to brute-force O(N²) checking.
# The grid partitions space so that only nearby rectangles are checked for collisions, making the algorithm much more efficient for large numbers of entities.
