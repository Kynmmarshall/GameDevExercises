# Exercise 7: Parallax Scrolling Background
#
# This program demonstrates a parallax scrolling system with multiple background layers, a camera that follows the player, and smoothing (lerp).
# Comments explain the math and infinite scrolling logic.

import pygame
import sys
import os

# --- ParallaxLayer ---
class ParallaxLayer:
    def __init__(self, image, scroll_factor, width):
        self.image = image
        self.scroll_factor = scroll_factor
        self.width = width  # width of the image (for tiling)
        self.offset = 0

    def update(self, camera_x):
        # The offset is a fraction of the camera position
        self.offset = (camera_x * self.scroll_factor) % self.width

    def draw(self, screen):
        # Draw enough tiles to fill the screen
        w, h = self.image.get_size()
        screen_w = screen.get_width()
        x = -self.offset
        while x < screen_w:
            screen.blit(self.image, (x, 0))
            x += self.width

# --- Camera ---
class Camera:
    def __init__(self, width, height, world_width):
        self.width = width
        self.height = height
        self.world_width = world_width
        self.x = 0
        self.target_x = 0
        self.smooth = 0.1  # Lerp factor

    def follow(self, target_x):
        self.target_x = max(self.width // 2, min(target_x, self.world_width - self.width // 2))

    def update(self):
        # Smoothly move camera towards target_x
        self.x += (self.target_x - self.x) * self.smooth
        # Clamp
        self.x = max(self.width // 2, min(self.x, self.world_width - self.width // 2))

    def apply(self, x, y):
        # Convert world to screen coordinates
        return x - self.x + self.width // 2, y

# --- Main Game ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()

    # Load or create background images (tileable)
    def make_bg(color, w, h):
        surf = pygame.Surface((w, h))
        surf.fill(color)
        for i in range(0, w, 40):
            pygame.draw.rect(surf, (color[0]//2, color[1]//2, color[2]//2), (i, h-30, 20, 30))
        return surf
    bg1 = make_bg((120, 180, 255), 800, 400)  # Far sky
    bg2 = make_bg((80, 200, 120), 600, 200)   # Near hills

    # Create layers
    layer1 = ParallaxLayer(bg1, 0.2, 800)
    layer2 = ParallaxLayer(bg2, 0.6, 600)
    layers = [layer1, layer2]

    # World and player
    world_width = 2400
    player = pygame.Rect(400, 320, 40, 60)
    player_speed = 300

    # Camera
    camera = Camera(800, 400, world_width)

    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= int(player_speed * dt)
        if keys[pygame.K_RIGHT]:
            player.x += int(player_speed * dt)
        player.x = max(0, min(player.x, world_width - player.width))

        # Camera follows player
        camera.follow(player.x + player.width // 2)
        camera.update()

        # Update parallax layers
        for layer in layers:
            layer.update(camera.x)

        # Draw
        screen.fill((0,0,0))
        for layer in layers:
            layer.draw(screen)
        px, py = camera.apply(player.x, player.y)
        pygame.draw.rect(screen, (255, 200, 0), (px, py, player.width, player.height))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Parallax math: Each layer's offset is camera_x * scroll_factor, so distant layers move less than close ones.
# Infinite scrolling: The background image is tiled horizontally. When the offset exceeds the image width, it wraps using modulo.
# Smoothing: The camera uses linear interpolation (lerp) to move smoothly towards the target position.
# This creates a cinematic, depth-rich scrolling effect.
