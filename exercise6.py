# Exercise 6: Sprite Animation System with State-Based Animations
#
# This implementation demonstrates a flexible animation system for a player character with multiple states (idle, walk left/right, jump, attack).
# Animations are managed separately from game logic, making the code modular and easy to extend.
# Placeholder colored rectangles are used for animation frames.

import pygame
import sys

# --- Animation class ---
class Animation:
    def __init__(self, images, frame_duration, loop=True):
        self.images = images  # list of pygame.Surface
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.timer = 0
        self.finished = False

    def update(self, dt):
        if self.finished:
            return
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.images):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.images) - 1
                    self.finished = True

    def get_image(self):
        return self.images[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.timer = 0
        self.finished = False

# --- AnimationSet class ---
class AnimationSet:
    def __init__(self, animations):
        self.animations = animations  # dict: state -> Animation
        self.current_state = None
        self.current_animation = None

    def play(self, state, reset_if_same=False):
        if self.current_state != state or reset_if_same:
            self.current_state = state
            self.current_animation = self.animations[state]
            self.current_animation.reset()

    def update(self, dt):
        if self.current_animation:
            self.current_animation.update(dt)

    def get_image(self):
        if self.current_animation:
            return self.current_animation.get_image()
        return None

    def is_finished(self):
        return self.current_animation.finished if self.current_animation else False

# --- Player class ---
class Player:
    def __init__(self, x, y, anim_set):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.current_state = "idle"
        self.anim_set = anim_set
        self.attack_queued = False
        self.override_animation = None
        self.prev_state = None

    def handle_input(self, keys, attack_pressed):
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -200
            self.current_state = "walk_left"
        elif keys[pygame.K_RIGHT]:
            self.vx = 200
            self.current_state = "walk_right"
        else:
            self.current_state = "idle"
        if not self.on_ground:
            self.current_state = "jump"
        if attack_pressed:
            if not self.on_ground:
                self.attack_queued = True

    def update(self, dt, attack_pressed):
        # Handle attack override
        if self.attack_queued and not self.override_animation:
            self.override_animation = self.anim_set.animations["air_attack"]
            self.override_animation.reset()
            self.prev_state = self.current_state
            self.attack_queued = False
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Gravity
        if not self.on_ground:
            self.vy += 800 * dt
        # Simulate ground
        if self.y >= 300:
            self.y = 300
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False
        # Jump
        if attack_pressed and self.on_ground:
            self.vy = -350
            self.on_ground = False
        # Animation logic
        if self.override_animation:
            self.override_animation.update(dt)
            if self.override_animation.finished:
                self.override_animation = None
                self.anim_set.play(self.prev_state)
        else:
            self.anim_set.play(self.current_state)
            self.anim_set.update(dt)

    def get_image(self):
        if self.override_animation:
            return self.override_animation.get_image()
        return self.anim_set.get_image()

    def draw(self, screen):
        img = self.get_image()
        if img:
            screen.blit(img, (self.x, self.y))

# --- Helper to create colored frames ---
def make_frames(color, count):
    frames = []
    for i in range(count):
        surf = pygame.Surface((50, 70))
        surf.fill(color)
        pygame.draw.rect(surf, (0,0,0), (0,0,50,70), 2)
        pygame.draw.circle(surf, (255,255,255), (25, 35), 10 + i*2, 2)
        frames.append(surf)
    return frames

# --- Main Program ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    # Create animations for each state
    anims = {
        "idle": Animation(make_frames((100,200,255), 4), 0.2, loop=True),
        "walk_left": Animation(make_frames((255,100,100), 6), 0.1, loop=True),
        "walk_right": Animation(make_frames((100,255,100), 6), 0.1, loop=True),
        "jump": Animation(make_frames((255,255,100), 2), 0.3, loop=True),
        "air_attack": Animation(make_frames((200,0,200), 5), 0.08, loop=False),
    }
    anim_set = AnimationSet(anims)
    player = Player(300, 300, anim_set)
    running = True
    attack_pressed = False
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    attack_pressed = True
        keys = pygame.key.get_pressed()
        player.handle_input(keys, attack_pressed)
        player.update(dt, attack_pressed)
        attack_pressed = False
        screen.fill((30,30,30))
        player.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# This system separates animation logic (Animation, AnimationSet) from game logic (Player state, movement).
# This makes it easy to add new animations or change animation behavior without touching gameplay code.
# It also allows for flexible animation overrides (e.g., air attack) and clean state-based animation switching.
