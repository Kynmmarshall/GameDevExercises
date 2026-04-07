"""
Exercise 7: Camera Effects – Shake, Zoom, and Smooth Follow (Difficult)
Demonstrates a Camera class with position, zoom, shake, and smooth follow with dead zone. Effects are stackable.
Press S to shake, Z to zoom in/out. Camera follows player smoothly.
"""
import pygame
import sys
import random
import math

SCREEN_W, SCREEN_H = 800, 600
WORLD_W, WORLD_H = 1600, 1200
PLAYER_SIZE = 40
OBSTACLE_RECT = pygame.Rect(600, 400, 120, 120)

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_duration = 0
        self.zoom_timer = 0
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.deadzone = pygame.Rect(
            width//2 - 100, height//2 - 60, 200, 120
        )  # Dead zone in screen coords
        self.smooth_speed = 8.0  # Higher = snappier

    def world_to_screen(self, pos):
        # Apply camera position, shake, and zoom
        sx = (pos[0] - self.x + self.shake_offset[0]) * self.zoom + self.width//2
        sy = (pos[1] - self.y + self.shake_offset[1]) * self.zoom + self.height//2
        return int(sx), int(sy)

    def apply_rect(self, rect):
        x, y = self.world_to_screen((rect.x, rect.y))
        w, h = int(rect.width * self.zoom), int(rect.height * self.zoom)
        return pygame.Rect(x, y, w, h)

    def update(self, target_pos, dt):
        # Smooth follow with dead zone
        tx, ty = target_pos
        # Dead zone in world coords
        dz_world = pygame.Rect(
            self.x - self.deadzone.width//2,
            self.y - self.deadzone.height//2,
            self.deadzone.width, self.deadzone.height
        )
        if not dz_world.collidepoint(tx, ty):
            # Move camera towards player
            dx = tx - self.x
            dy = ty - self.y
            self.x += dx * min(self.smooth_speed * dt, 1)
            self.y += dy * min(self.smooth_speed * dt, 1)
        # Clamp to world
        self.x = max(self.width//2/self.zoom, min(self.x, WORLD_W - self.width//2/self.zoom))
        self.y = max(self.height//2/self.zoom, min(self.y, WORLD_H - self.height//2/self.zoom))
        # Update shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            decay = self.shake_timer / self.shake_duration if self.shake_duration > 0 else 0
            intensity = self.shake_intensity * decay
            angle = random.uniform(0, 2*math.pi)
            self.shake_offset = (
                random.uniform(-1,1) * intensity,
                random.uniform(-1,1) * intensity
            )
        else:
            self.shake_offset = (0, 0)
        # Update zoom
        if self.zoom != self.target_zoom:
            if self.zoom_duration > 0:
                self.zoom_timer += dt
                t = min(self.zoom_timer / self.zoom_duration, 1)
                self.zoom = self.zoom + (self.target_zoom - self.zoom) * t
                if t >= 1:
                    self.zoom = self.target_zoom
                    self.zoom_duration = 0
            else:
                self.zoom = self.target_zoom

    def start_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration

    def start_zoom(self, target_zoom, duration):
        self.target_zoom = target_zoom
        self.zoom_duration = duration
        self.zoom_timer = 0

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 300
    def move(self, keys, dt):
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.x = max(0, min(self.x, WORLD_W))
        self.y = max(0, min(self.y, WORLD_H))
    def rect(self):
        return pygame.Rect(self.x-PLAYER_SIZE//2, self.y-PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    player = Player(WORLD_W//2, WORLD_H//2)
    camera = Camera(SCREEN_W, SCREEN_H)
    zooming_in = False
    zoom_cooldown = 0
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Fix: Use event.key == pygame.K_s (lowercase 's')
                if event.key == pygame.K_s:
                    camera.start_shake(30, 0.5)
                elif event.key == pygame.K_z and zoom_cooldown <= 0:
                    if not zooming_in:
                        camera.start_zoom(2.0, 0.5)
                        zooming_in = True
                        zoom_cooldown = 0.5
                    else:
                        camera.start_zoom(1.0, 0.5)
                        zooming_in = False
                        zoom_cooldown = 0.5
        if zoom_cooldown > 0:
            zoom_cooldown -= dt
        keys = pygame.key.get_pressed()
        player.move(keys, dt)
        camera.update((player.x, player.y), dt)
        # Draw world to a surface for zoom
        surf = pygame.Surface((WORLD_W, WORLD_H))
        surf.fill((60,60,80))
        # Draw obstacle
        pygame.draw.rect(surf, (180,60,60), OBSTACLE_RECT)
        # Draw player
        pygame.draw.rect(surf, (50,200,255), player.rect())
        # Blit world to screen with camera
        view_rect = pygame.Rect(
            int(camera.x - SCREEN_W//2/camera.zoom),
            int(camera.y - SCREEN_H//2/camera.zoom),
            int(SCREEN_W/camera.zoom),
            int(SCREEN_H/camera.zoom)
        )
        scaled = pygame.transform.smoothscale(surf.subsurface(view_rect), (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0,0))
        # Draw dead zone
        dz = camera.deadzone
        pygame.draw.rect(screen, (255,255,0), dz, 2)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Dead zone: A rectangle in screen/world space. Camera only moves if player leaves this zone.
# Smooth follow: Camera moves towards player with interpolation (lerp).
# Shake: Random offset decays over time.
# Zoom: Interpolates zoom factor, affects all drawing.
# Effects are stackable: shake and zoom can be active together.
