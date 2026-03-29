# Exercise 4: Advanced Particle System with Emitters and Object Pooling
#
# This program demonstrates a high-performance particle system using object pooling and multiple emitters.
# Comments explain pooling, performance, and emitter design.

import pygame
import sys
import random

SCREEN_W, SCREEN_H = 800, 600

class Particle:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.lifetime = 0
        self.color = (255,255,255)
        self.size = 1
        self.alpha = 255
        self.fade = 1.0
    def reinit(self, x, y, vx, vy, lifetime, color, size, fade=1.0):
        self.active = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.color = color
        self.size = size
        self.alpha = 255
        self.fade = fade
    def update(self, dt):
        if not self.active:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.size = max(0, self.size * (self.lifetime / max(0.001, self.lifetime + dt)))
        self.alpha = int(255 * (self.lifetime / max(0.001, self.lifetime + dt)) * self.fade)
        if self.lifetime <= 0 or self.size <= 0 or self.alpha <= 0:
            self.active = False
    def draw(self, screen):
        if not self.active:
            return
        surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color + (self.alpha,), (int(self.size), int(self.size)), int(self.size))
        screen.blit(surf, (self.x - self.size, self.y - self.size))

class ParticlePool:
    def __init__(self, max_particles=500):
        self.particles = [Particle() for _ in range(max_particles)]
    def spawn(self, **kwargs):
        for p in self.particles:
            if not p.active:
                p.reinit(**kwargs)
                return p
        return None  # Pool exhausted
    def update(self, dt):
        for p in self.particles:
            if p.active:
                p.update(dt)
    def draw(self, screen):
        for p in self.particles:
            if p.active:
                p.draw(screen)

class Emitter:
    def __init__(self, pool, x, y, particle_template, continuous=False, rate=0, burst=0):
        self.pool = pool
        self.x = x
        self.y = y
        self.template = particle_template
        self.continuous = continuous
        self.rate = rate
        self.burst = burst
        self.timer = 0
    def emit(self):
        for _ in range(self.burst):
            self.spawn_particle()
    def update(self, dt):
        if self.continuous:
            self.timer += dt
            while self.timer > 1.0/self.rate:
                self.spawn_particle()
                self.timer -= 1.0/self.rate
    def spawn_particle(self):
        # Customize properties per emitter
        t = self.template
        vx = random.uniform(*t['vx']) if isinstance(t['vx'], tuple) else t['vx']
        vy = random.uniform(*t['vy']) if isinstance(t['vy'], tuple) else t['vy']
        lifetime = random.uniform(*t['lifetime']) if isinstance(t['lifetime'], tuple) else t['lifetime']
        size = random.uniform(*t['size']) if isinstance(t['size'], tuple) else t['size']
        color = t['color'] if isinstance(t['color'], tuple) else (255,255,255)
        fade = t.get('fade', 1.0)
        self.pool.spawn(x=self.x, y=self.y, vx=vx, vy=vy, lifetime=lifetime, color=color, size=size, fade=fade)

# --- Demo Game ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    pool = ParticlePool(600)
    # Player
    player = pygame.Rect(400, 500, 40, 40)
    player_speed = 260
    # Emitters
    explosion_template = {
        'vx': (-200, 200), 'vy': (-200, 200), 'lifetime': (0.5, 1.0), 'color': (255,180,0), 'size': (6, 12), 'fade': 1.0
    }
    smoke_template = {
        'vx': (-20, 20), 'vy': (-60, -20), 'lifetime': (0.7, 1.2), 'color': (120,120,120), 'size': (4, 8), 'fade': 0.7
    }
    smoke_emitter = Emitter(pool, player.centerx, player.bottom, smoke_template, continuous=True, rate=20)
    explosion_emitter = Emitter(pool, player.centerx, player.centery, explosion_template, burst=40)
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                explosion_emitter.x, explosion_emitter.y = player.centerx, player.centery
                explosion_emitter.emit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= int(player_speed * dt)
        if keys[pygame.K_RIGHT]:
            player.x += int(player_speed * dt)
        player.x = max(0, min(player.x, SCREEN_W - player.width))
        # Smoke follows player
        smoke_emitter.x, smoke_emitter.y = player.centerx, player.bottom
        smoke_emitter.update(dt)
        pool.update(dt)
        screen.fill((30,30,30))
        pygame.draw.rect(screen, (0,200,255), player)
        pool.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Object pooling: Instead of creating/destroying particles, we reuse inactive ones, reducing memory allocation and garbage collection.
# Without pooling, hundreds of objects would be created/destroyed per second, causing performance drops.
# With pooling, all particles are pre-allocated and simply reinitialized, keeping the system smooth even with many particles.
# Performance: Try increasing the pool size or emission rates to see how pooling keeps the game responsive.
