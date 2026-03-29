# Exercise 3: Infinite Parallax Scrolling with Dynamic Layers
#
# This program demonstrates efficient infinite parallax scrolling with dynamic layer management and tile recycling.
# Comments explain the math and memory efficiency.

import pygame
import sys

SCREEN_W, SCREEN_H = 800, 600

class ParallaxLayer:
    def __init__(self, tile_img, speed, y, screen_width):
        self.tile_img = tile_img
        self.speed = speed
        self.y = y
        self.screen_width = screen_width
        self.tile_w = tile_img.get_width()
        # Calculate how many tiles needed to cover the screen (plus one for overlap)
        self.tiles = []
        n = (screen_width // self.tile_w) + 2
        for i in range(n):
            self.tiles.append(i * self.tile_w)

    def update(self, dt):
        for i in range(len(self.tiles)):
            self.tiles[i] -= self.speed * dt
        # Recycle tiles that have moved off the left
        for i in range(len(self.tiles)):
            if self.tiles[i] <= -self.tile_w:
                max_x = max(self.tiles)
                self.tiles[i] = max_x + self.tile_w

    def draw(self, screen, camera_x=0):
        for x in self.tiles:
            sx = x - camera_x
            if -self.tile_w < sx < self.screen_width:
                screen.blit(self.tile_img, (sx, self.y))

class ParallaxSystem:
    def __init__(self, screen_width):
        self.layers = []
        self.active = []
        self.screen_width = screen_width
    def add_layer(self, layer):
        self.layers.append(layer)
        self.active.append(True)
    def enable_layer(self, idx):
        if 0 <= idx < len(self.active):
            self.active[idx] = True
    def disable_layer(self, idx):
        if 0 <= idx < len(self.active):
            self.active[idx] = False
    def update(self, dt):
        for i, layer in enumerate(self.layers):
            if self.active[i]:
                layer.update(dt)
    def draw(self, screen, camera_x=0):
        for i, layer in enumerate(self.layers):
            if self.active[i]:
                layer.draw(screen, camera_x)

def make_tile(color, w, h):
    surf = pygame.Surface((w, h))
    surf.fill(color)
    pygame.draw.rect(surf, (0,0,0), (0,0,w,h), 2)
    return surf

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    # Create placeholder tiles
    ground_tile = make_tile((120, 80, 40), 160, 80)
    mountain_tile = make_tile((80, 120, 180), 200, 120)
    cloud_tile = make_tile((220, 220, 255), 120, 60)
    # Create layers
    ground = ParallaxLayer(ground_tile, speed=200, y=520, screen_width=SCREEN_W)
    mountains = ParallaxLayer(mountain_tile, speed=60, y=400, screen_width=SCREEN_W)
    clouds = ParallaxLayer(cloud_tile, speed=30, y=200, screen_width=SCREEN_W)
    system = ParallaxSystem(SCREEN_W)
    system.add_layer(mountains)
    system.add_layer(ground)
    cloud_added = False
    timer = 0
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        timer += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    if not cloud_added:
                        system.add_layer(clouds)
                        cloud_added = True
        # Add cloud layer after 5 seconds
        if not cloud_added and timer > 5.0:
            system.add_layer(clouds)
            cloud_added = True
        system.update(dt)
        screen.fill((120,180,255))
        system.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Math: Each tile's x position is decremented by speed*dt. When a tile moves off the left, it is moved to the right of the last tile.
# This ensures seamless, infinite scrolling with minimal memory use.
# Only visible tiles are drawn, and layers can be enabled/disabled at runtime.
# For vertical scrolling, use the same logic but manage y positions and tile columns.
