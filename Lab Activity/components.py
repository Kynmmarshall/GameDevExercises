# components.py
# ECS Components for Arcade Game

class Transform:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, dx=0, dy=0):
        self.dx = dx
        self.dy = dy

class Sprite:
    def __init__(self, image):
        self.image = image

class Collider:
    def __init__(self, rect, type_):
        self.rect = rect
        self.type = type_  # 'player', 'enemy', 'bullet'

class Health:
    def __init__(self, hp):
        self.hp = hp

class Score:
    def __init__(self):
        self.value = 0
