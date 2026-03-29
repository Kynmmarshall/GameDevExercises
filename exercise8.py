# Exercise 8: Simple Particle System
#
# This program implements a generic, efficient particle system with pooling, supporting dust and explosion effects.
# Comments explain pooling and performance benefits.

import pygame
import sys
import random

# --- Particle class ---
class Particle:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.lifetime = 0
        self.size = 0
        self.init_size = 0
        self.color = (255,255,255)
        self.gravity = 0
        self.fade = 1.0

    def reset(self, x, y, vx, vy, lifetime, size, color, gravity, fade):
        self.active = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.init_size = size
        self.size = size
        self.color = color
        self.gravity = gravity
        self.fade = fade
        self.alpha = 255

    def update(self, dt):
        if not self.active:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        self.size = max(0, self.init_size * (self.lifetime / max(0.001, self.lifetime + dt)))
        self.alpha = int(255 * (self.lifetime / max(0.001, self.lifetime + dt)) * self.fade)
        if self.lifetime <= 0 or self.size <= 0 or self.alpha <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
        surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color + (self.alpha,), (int(self.size), int(self.size)), int(self.size))
        screen.blit(surf, (self.x - self.size, self.y - self.size))

# --- ParticleSystem with pooling ---
class ParticleSystem:
    def __init__(self, max_particles=300):
        self.particles = [Particle() for _ in range(max_particles)]

    def emit(self, template, count=1):
        # Find inactive particles to reuse (pooling)
        emitted = 0
        for p in self.particles:
            if not p.active:
                p.reset(**template)
                emitted += 1
                if emitted >= count:
                    break

    def update(self, dt):
        for p in self.particles:
            if p.active:
                p.update(dt)

    def draw(self, screen):
        for p in self.particles:
            if p.active:
                p.draw(screen)

# --- InputManager (observer pattern, simplified) ---
class InputManager:
    def __init__(self):
        self.listeners = []
    def add_listener(self, listener):
        self.listeners.append(listener)
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for l in self.listeners:
                    l.on_action('explode')
        return pygame.key.get_pressed()

# --- Player class ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.speed = 250
    def move(self, keys, dt):
        if keys[pygame.K_LEFT]:
            self.rect.x -= int(self.speed * dt)
        if keys[pygame.K_RIGHT]:
            self.rect.x += int(self.speed * dt)
        self.rect.x = max(0, min(self.rect.x, 760))
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 200, 0), self.rect)

# --- Demo Game ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()
    player = Player(380, 320)
    particles = ParticleSystem(400)
    input_manager = InputManager()

    # Observer: explosion effect
    class ExplosionListener:
        def on_action(self, action):
            if action == 'explode':
                for _ in range(40):
                    angle = random.uniform(0, 6.28)
                    speed = random.uniform(80, 220)
                    vx = speed * random.uniform(-1, 1)
                    vy = speed * random.uniform(-1, 1)
                    template = {
                        'x': player.rect.centerx,
                        'y': player.rect.centery,
                        'vx': vx,
                        'vy': vy,
                        'lifetime': random.uniform(0.5, 1.2),
                        'size': random.uniform(6, 12),
                        'color': (255, random.randint(100,200), 0),
                        'gravity': 200,
                        'fade': 1.0
                    }
                    particles.emit(template)
    input_manager.add_listener(ExplosionListener())

    running = True
    while running:
        dt = clock.tick(60) / 1e3
        keys = input_manager.update()
        player.move(keys, dt)
        # Dust effect when moving
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            template = {
                'x': player.rect.centerx,
                'y': player.rect.bottom,
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-10, 0),
                'lifetime': random.uniform(0.3, 0.5),
                'size': random.uniform(3, 7),
                'color': (180, 180, 180),
                'gravity': 100,
                'fade': 0.7
            }
            particles.emit(template, count=2)
        particles.update(dt)
        screen.fill((30,30,30))
        player.draw(screen)
        particles.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Particle pooling: Instead of creating/destroying particles, we reuse inactive ones. This avoids memory fragmentation and garbage collection spikes, improving performance for effects with many particles.
# Reflection: Pooling and generic templates make it easy to add new effects and keep the game smooth, even with hundreds of particles.
