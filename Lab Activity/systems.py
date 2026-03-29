# systems.py
# ECS Systems and Entity class for Arcade Game

import pygame
from components import Transform, Velocity, Sprite, Collider, Health

class Entity:
    def __init__(self):
        self.components = {}
        self.alive = True
    def add_component(self, name, comp):
        self.components[name] = comp
    def get(self, name):
        return self.components.get(name)

class MovementSystem:
    def update(self, entities, dt):
        for e in entities:
            t = e.get('Transform')
            v = e.get('Velocity')
            if t and v:
                t.x += v.dx * dt
                t.y += v.dy * dt
                c = e.get('Collider')
                if c:
                    c.rect.x = int(t.x)
                    c.rect.y = int(t.y)

class RenderSystem:
    def draw(self, entities, screen):
        for e in entities:
            t = e.get('Transform')
            s = e.get('Sprite')
            if t and s:
                screen.blit(s.image, (t.x, t.y))

class BulletSystem:
    def update(self, entities, world_height):
        for e in entities:
            c = e.get('Collider')
            if c and c.type == 'bullet' and c.rect.y < -20:
                e.alive = False

class EnemySystem:
    def update(self, entities, world_height):
        for e in entities:
            c = e.get('Collider')
            if c and c.type == 'enemy' and c.rect.y > world_height:
                e.alive = False

class CollisionSystem:
    def __init__(self, grid):
        self.grid = grid
    def update(self, entities):
        self.grid.clear()
        for e in entities:
            c = e.get('Collider')
            if c:
                self.grid.insert(c.rect, e)
        # Bullet-enemy collisions
        for e in entities:
            c = e.get('Collider')
            if c and c.type == 'bullet':
                for other in self.grid.get_nearby(c.rect):
                    if other is not e and other.alive:
                        oc = other.get('Collider')
                        if oc and oc.type == 'enemy' and c.rect.colliderect(oc.rect):
                            e.alive = False
                            h = other.get('Health')
                            if h:
                                h.hp -= 1
                                if h.hp <= 0:
                                    other.alive = False
        # Player-enemy collisions
        for e in entities:
            c = e.get('Collider')
            if c and c.type == 'player':
                for other in self.grid.get_nearby(c.rect):
                    if other is not e and other.alive:
                        oc = other.get('Collider')
                        if oc and oc.type == 'enemy' and c.rect.colliderect(oc.rect):
                            return True  # Game over
        return False
