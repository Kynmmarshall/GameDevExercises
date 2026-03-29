# entities.py
# Entity creation helpers for Arcade Game

import pygame
from components import Transform, Velocity, Sprite, Collider, Health

def create_player(image):
    from systems import Entity
    e = Entity()
    e.add_component('Transform', Transform(380, 540))
    e.add_component('Velocity', Velocity())
    e.add_component('Sprite', Sprite(image))
    e.add_component('Collider', Collider(pygame.Rect(380, 540, 40, 40), 'player'))
    return e

def create_enemy(image, x, y, speed):
    from systems import Entity
    e = Entity()
    e.add_component('Transform', Transform(x, y))
    e.add_component('Velocity', Velocity(0, speed))
    e.add_component('Sprite', Sprite(image))
    e.add_component('Collider', Collider(pygame.Rect(x, y, 40, 40), 'enemy'))
    e.add_component('Health', Health(1))
    return e

def create_bullet(image, x, y, speed):
    from systems import Entity
    e = Entity()
    e.add_component('Transform', Transform(x, y))
    e.add_component('Velocity', Velocity(0, -speed))
    e.add_component('Sprite', Sprite(image))
    e.add_component('Collider', Collider(pygame.Rect(x, y, 8, 16), 'bullet'))
    return e
