# arcade_game.py
# Main game file integrating ECS, input, and spatial grid

import pygame
import random
from components import *
from entities import create_player, create_enemy, create_bullet
from systems import Entity, MovementSystem, RenderSystem, BulletSystem, EnemySystem, CollisionSystem
from input_manager import InputManager
from spatial_grid import SpatialGrid

WIDTH, HEIGHT = 800, 600

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Arcade Space Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.entities = []
        self.player_img = pygame.Surface((40, 40)); self.player_img.fill((0,200,255))
        self.enemy_img = pygame.Surface((40, 40)); self.enemy_img.fill((255,80,80))
        self.bullet_img = pygame.Surface((8, 16)); self.bullet_img.fill((255,255,0))
        self.player = create_player(self.player_img)
        self.entities.append(self.player)
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.input = InputManager()
        self.input.map_action('left', pygame.K_LEFT)
        self.input.map_action('right', pygame.K_RIGHT)
        self.input.map_action('shoot', pygame.K_SPACE)
        self.input.add_listener('shoot', self)
        self.shoot_cooldown = 0
        self.spawn_timer = 0
        self.grid = SpatialGrid(64)
        self.movement = MovementSystem()
        self.render = RenderSystem()
        self.bullets = BulletSystem()
        self.enemies = EnemySystem()
        self.collision = CollisionSystem(self.grid)
        self.game_over = False

    def on_action(self, action):
        if action == 'shoot' and not self.game_over and self.shoot_cooldown <= 0:
            t = self.player.get('Transform')
            b = create_bullet(self.bullet_img, t.x+16, t.y-16, 400)
            self.entities.append(b)
            self.shoot_cooldown = 0.25

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.input.update()

    def update(self, dt):
        if self.game_over:
            return
        # Player movement
        t = self.player.get('Transform')
        v = self.player.get('Velocity')
        v.dx = 0
        if self.input.is_action_pressed('left'):
            v.dx = -300
        if self.input.is_action_pressed('right'):
            v.dx = 300
        t.x = max(0, min(WIDTH-40, t.x + v.dx*dt))
        self.player.get('Collider').rect.x = int(t.x)
        # Spawn enemies
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            x = random.randint(0, WIDTH-40)
            e = create_enemy(self.enemy_img, x, -40, random.randint(80, 160))
            self.entities.append(e)
            self.spawn_timer = random.uniform(0.7, 1.3)
        # Update systems
        self.movement.update(self.entities, dt)
        self.bullets.update(self.entities, HEIGHT)
        self.enemies.update(self.entities, HEIGHT)
        # Remove dead entities
        self.entities = [e for e in self.entities if e.alive]
        # Collisions
        if self.collision.update(self.entities):
            self.game_over = True
        # Score
        for e in self.entities:
            if e.get('Collider') and e.get('Collider').type == 'enemy' and not e.alive:
                self.score += 10
        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def draw(self):
        self.screen.fill((20,20,40))
        self.render.draw(self.entities, self.screen)
        score_text = self.font.render(f"Score: {self.score}", True, (255,255,255))
        self.screen.blit(score_text, (10, 10))
        if self.game_over:
            over = self.font.render("GAME OVER! Press R to Restart", True, (255,80,80))
            self.screen.blit(over, (WIDTH//2-180, HEIGHT//2-20))
        pygame.display.flip()

    def restart(self):
        self.entities = [self.player]
        t = self.player.get('Transform')
        t.x, t.y = 380, 540
        self.player.get('Collider').rect.x, self.player.get('Collider').rect.y = 380, 540
        self.score = 0
        self.game_over = False

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1e3
            self.handle_events()
            if self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.restart()
            else:
                self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
