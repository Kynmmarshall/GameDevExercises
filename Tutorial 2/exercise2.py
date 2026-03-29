# Exercise 2: Tile-Based Level Editor and Scrolling Camera
#
# This program demonstrates a tile map loader, multi-layer rendering, a scrolling camera, and player collision with solid tiles.
# Comments explain the design and efficiency of tile culling.

import pygame
import sys
import os

TILE_SIZE = 32
SCREEN_W, SCREEN_H = 640, 480

# --- TileMap class ---
class TileMap:
    def __init__(self, filename, tile_images):
        self.tile_images = tile_images  # list of pygame.Surface
        self.layers = []  # list of 2D lists (layer[y][x] = tile_id)
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

# --- Camera class ---
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

# --- Player class ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
    def move(self, keys, dt, tilemap):
        speed = 180
        jump = -320
        gravity = 900
        if keys[pygame.K_LEFT]:
            self.vx = -speed
        elif keys[pygame.K_RIGHT]:
            self.vx = speed
        else:
            self.vx = 0
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = jump
        self.vy += gravity * dt
        # Horizontal
        self.rect.x += int(self.vx * dt)
        self.collide(tilemap, dx=True)
        # Vertical
        self.rect.y += int(self.vy * dt)
        self.on_ground = False
        self.collide(tilemap, dx=False)
    def collide(self, tilemap, dx):
        for i in range(4):
            px = self.rect.left + (self.rect.width-1 if i%2 else 0)
            py = self.rect.top + (self.rect.height-1 if i//2 else 0)
            tile = tilemap.get_tile(px, py, layer=0)
            if tile > 0:
                if dx:
                    if self.vx > 0:
                        self.rect.right = (px // TILE_SIZE) * TILE_SIZE
                    if self.vx < 0:
                        self.rect.left = (px // TILE_SIZE + 1) * TILE_SIZE
                    self.vx = 0
                else:
                    if self.vy > 0:
                        self.rect.bottom = (py // TILE_SIZE) * TILE_SIZE
                        self.on_ground = True
                    if self.vy < 0:
                        self.rect.top = (py // TILE_SIZE + 1) * TILE_SIZE
                    self.vy = 0
    def draw(self, screen, camera):
        sx, sy = camera.apply((self.rect.x, self.rect.y))
        pygame.draw.rect(screen, (255,200,0), (sx, sy, self.rect.width, self.rect.height))

# --- Main Program ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    # Placeholder tile images
    tile_images = [pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA) for _ in range(4)]
    tile_images[0].fill((0,0,0,0))
    tile_images[1].fill((100,200,100))
    tile_images[2].fill((200,100,100))
    tile_images[3].fill((180,180,255))
    # Load map
    level_path = os.path.join(os.path.dirname(__file__), 'level.txt')
    tilemap = TileMap(level_path, tile_images)
    camera = Camera(SCREEN_W, SCREEN_H, tilemap.width, tilemap.height)
    player = Player(64, 64)
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        player.move(keys, dt, tilemap)
        camera.follow(player.rect.centerx, player.rect.centery)
        screen.fill((60,60,80))
        tilemap.draw(screen, camera)
        player.draw(screen, camera)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Tile culling: Only tiles within the camera's view are drawn, making rendering efficient even for large maps.
# Sample level.txt format (first line: width height num_layers, then each layer):
# 10 8 2
# ...ground layer...
# ...decoration layer...
