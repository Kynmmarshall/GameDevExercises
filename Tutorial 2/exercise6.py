"""
Exercise 6: Pathfinding with A* on a Tile-Based Map (Difficult)
Implements A* pathfinding for enemies on a tile map with variable movement costs and dynamic obstacles.
Comments explain A* steps and cost handling.
"""
import pygame
import sys
import os
import heapq

TILE_SIZE = 32
SCREEN_W, SCREEN_H = 640, 480

# --- TileMap class (from Exercise 2, with cost support) ---
class TileMap:
    def __init__(self, filename, tile_images, tile_costs):
        self.tile_images = tile_images
        self.tile_costs = tile_costs  # dict: tile_id -> cost
        self.layers = []
        self.width = 0
        self.height = 0
        self.load(filename)

    def load(self, filename):
        with open(filename) as f:
            header = f.readline().split()
            self.width, self.height, num_layers = map(int, header)
            for _ in range(num_layers):
                layer = []
                for _ in range(self.height):
                    row = list(map(int, f.readline().strip().split(',')))
                    layer.append(row)
                self.layers.append(layer)

    def draw(self, screen, camera):
        for layer in self.layers:
            for y in range(self.height):
                for x in range(self.width):
                    tile_id = layer[y][x]
                    if tile_id == 0:
                        continue
                    wx, wy = x * TILE_SIZE, y * TILE_SIZE
                    rect = pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)
                    if camera.is_visible(rect):
                        sx, sy = camera.apply((wx, wy))
                        screen.blit(self.tile_images[tile_id], (sx, sy))

    def get_tile(self, wx, wy, layer=0):
        x, y = wx // TILE_SIZE, wy // TILE_SIZE
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.layers[layer][y][x]
        return 0

    def is_solid(self, tile_id):
        # Example: 1=wall, 2=water, 3=mud, 0=empty
        return tile_id == 1

    def get_cost(self, tile_id):
        return self.tile_costs.get(tile_id, 1)

# --- Camera class (from Exercise 2) ---
class Camera:
    def __init__(self, width, height, map_w, map_h):
        self.width = width
        self.height = height
        self.map_w = map_w
        self.map_h = map_h
        self.x = 0
        self.y = 0
    def follow(self, target_x, target_y):
        self.x = max(0, min(target_x - self.width // 2, self.map_w * TILE_SIZE - self.width))
        self.y = max(0, min(target_y - self.height // 2, self.map_h * TILE_SIZE - self.height))
    def apply(self, pos):
        return pos[0] - self.x, pos[1] - self.y
    def is_visible(self, rect):
        cam_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return cam_rect.colliderect(rect)

# --- A* Pathfinding ---
def astar(tilemap, start, goal, layer=0, dynamic_blocked=None):
    # Each node: (f, g, h, (x, y), parent)
    open_set = []
    heapq.heappush(open_set, (0, 0, 0, start, None))
    closed = set()
    node_map = {}
    while open_set:
        f, g, h, pos, parent = heapq.heappop(open_set)
        if pos in closed:
            continue
        closed.add(pos)
        node_map[pos] = (g, h, parent)
        if pos == goal:
            # Reconstruct path
            path = []
            while pos:
                path.append(pos)
                _, _, parent = node_map[pos]
                pos = parent
            path.reverse()
            return path
        x, y = pos
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if not (0 <= nx < tilemap.width and 0 <= ny < tilemap.height):
                continue
            tile_id = tilemap.layers[layer][ny][nx]
            if tilemap.is_solid(tile_id):
                continue
            if dynamic_blocked and (nx, ny) in dynamic_blocked:
                continue
            cost = tilemap.get_cost(tile_id)
            ng = g + cost
            nh = abs(goal[0]-nx) + abs(goal[1]-ny)  # Manhattan
            nf = ng + nh
            if (nx, ny) in closed:
                continue
            heapq.heappush(open_set, (nf, ng, nh, (nx, ny), pos))
    return None  # No path

# --- Enemy class ---
class Enemy:
    def __init__(self, x, y, tilemap):
        self.x = x
        self.y = y
        self.tilemap = tilemap
        self.path = []
        self.path_idx = 0
        self.repath_timer = 0
        self.speed = 80  # pixels/sec
        self.blocked = set()
    def update(self, dt, player_pos, dynamic_blocked=None):
        self.repath_timer += dt
        tx, ty = int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)
        px, py = int(player_pos[0] // TILE_SIZE), int(player_pos[1] // TILE_SIZE)
        # Recalculate path every 0.5s or if blocked
        if self.repath_timer > 0.5 or not self.path or (self.path and (tx, ty) != self.path[self.path_idx]):
            self.path = astar(self.tilemap, (tx, ty), (px, py), dynamic_blocked=dynamic_blocked)
            self.path_idx = 0
            self.repath_timer = 0
        # Move along path
        if self.path and self.path_idx < len(self.path):
            next_tile = self.path[self.path_idx]
            nx, ny = next_tile
            wx, wy = nx * TILE_SIZE + TILE_SIZE//2, ny * TILE_SIZE + TILE_SIZE//2
            dx, dy = wx - self.x, wy - self.y
            dist = (dx**2 + dy**2)**0.5
            if dist < 2:
                self.path_idx += 1
            else:
                move_dist = min(self.speed * dt, dist)
                if dist > 0:
                    self.x += dx / dist * move_dist
                    self.y += dy / dist * move_dist
    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x-12, self.y-12))
        pygame.draw.circle(screen, (200,50,50), (int(sx)+12, int(sy)+12), 12)
        # Draw path
        if self.path:
            for idx, (tx, ty) in enumerate(self.path):
                color = (255,255,0) if idx == self.path_idx else (100,255,100)
                wx, wy = tx*TILE_SIZE+TILE_SIZE//2, ty*TILE_SIZE+TILE_SIZE//2
                px, py = camera.apply((wx, wy))
                pygame.draw.circle(screen, color, (int(px), int(py)), 6, 1)

# --- Player class (arrow keys) ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 28, 28)
    def move(self, keys, dt, tilemap):
        speed = 180
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        nx = self.x + dx * speed * dt
        ny = self.y + dy * speed * dt
        # Collision
        tx, ty = int(nx // TILE_SIZE), int(ny // TILE_SIZE)
        if not tilemap.is_solid(tilemap.layers[0][ty][tx]):
            self.x, self.y = nx, ny
        self.rect.x, self.rect.y = int(self.x), int(self.y)
    def draw(self, screen, camera):
        sx, sy = camera.apply((self.rect.x, self.rect.y))
        pygame.draw.rect(screen, (50,200,255), (sx, sy, self.rect.width, self.rect.height))

# --- Main Program ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    # Tile images and costs
    tile_images = [pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) for _ in range(4)]
    tile_images[0].fill((0,0,0,0))      # empty
    tile_images[1].fill((100,200,100))  # wall
    tile_images[2].fill((80,80,255))    # water
    tile_images[3].fill((180,140,80))   # mud
    tile_costs = {0:1, 1:999, 2:5, 3:2}  # wall=impassable, water=5, mud=2
    level_path = os.path.join(os.path.dirname(__file__), 'level.txt')
    tilemap = TileMap(level_path, tile_images, tile_costs)
    camera = Camera(SCREEN_W, SCREEN_H, tilemap.width, tilemap.height)
    player = Player(64, 64)
    enemy = Enemy(320, 320, tilemap)
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        player.move(keys, dt, tilemap)
        camera.follow(player.x, player.y)
        # Dynamic obstacles: block tiles occupied by player
        dynamic_blocked = {(int(player.x//TILE_SIZE), int(player.y//TILE_SIZE))}
        enemy.update(dt, (player.x, player.y), dynamic_blocked=dynamic_blocked)
        screen.fill((60,60,80))
        tilemap.draw(screen, camera)
        player.draw(screen, camera)
        enemy.draw(screen, camera)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# A* steps: open set (priority queue), closed set, g/h/f costs, parent pointers for path reconstruction.
# Variable costs: tilemap.get_cost(tile_id) used for g cost. Walls are impassable (cost=999).
# Dynamic obstacles: pass set of blocked tiles to astar().
# Path is visualized as circles along the route.
