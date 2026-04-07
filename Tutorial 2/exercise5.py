# Exercise 5: Animation Blending and Cross-Fading
#
# This program demonstrates an AnimationController that supports cross-fading and parameter blending between idle and walk animations.
# Comments explain blending logic, performance, and challenges.

import pygame
import sys

SCREEN_W, SCREEN_H = 720, 480

class Animation:
    def __init__(self, frames, durations):
        self.frames = frames
        self.durations = durations
        self.current_frame = 0
        self.timer = 0
        self.playing = True
    def update(self, dt, speed=1.0):
        if not self.playing:
            return
        duration = self.durations[self.current_frame] / speed
        self.timer += dt
        if self.timer >= duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    def get_frame(self):
        return self.frames[self.current_frame]
    def reset(self):
        self.current_frame = 0
        self.timer = 0

class AnimationController:
    def __init__(self, animations):
        self.animations = animations  # dict: name -> Animation
        self.current = 'idle'
        self.target = None
        self.blend_time = 0
        self.blend_timer = 0
        self.blending = False
        self.flip = False
        self.speed_param = 0
    def play(self, name, blend_time=0):
        if name == self.current or blend_time == 0:
            self.current = name
            self.animations[self.current].reset()
            self.blending = False
        else:
            self.target = name
            self.blend_time = blend_time
            self.blend_timer = 0
            self.blending = True
    def set_flip(self, flip):
        self.flip = flip
    def set_speed_param(self, speed):
        self.speed_param = speed
    def update(self, dt):
        if self.blending:
            self.animations[self.current].update(dt, 1.0)
            self.animations[self.target].update(dt, 1.0)
            self.blend_timer += dt
            if self.blend_timer >= self.blend_time:
                self.current = self.target
                self.animations[self.current].reset()
                self.blending = False
        else:
            # Parameter blending: blend idle/walk based on speed_param
            if self.speed_param > 0:
                self.animations['walk'].update(dt, self.speed_param)
            else:
                self.animations['idle'].update(dt, 1.0)
    def get_frame(self):
        if self.blending:
            alpha = min(1.0, self.blend_timer / self.blend_time)
            src = self.animations[self.current].get_frame()
            tgt = self.animations[self.target].get_frame()
            # Alpha blend the two frames
            blended = pygame.Surface(src.get_size(), pygame.SRCALPHA)
            blended.blit(src, (0,0))
            tgt_alpha = int(255 * alpha)
            tgt_with_alpha = tgt.copy()
            tgt_with_alpha.set_alpha(tgt_alpha)
            blended.blit(tgt_with_alpha, (0,0))
            if self.flip:
                blended = pygame.transform.flip(blended, True, False)
            return blended
        else:
            frame = self.animations['walk'].get_frame() if self.speed_param > 0 else self.animations['idle'].get_frame()
            if self.flip:
                frame = pygame.transform.flip(frame, True, False)
            return frame

# --- Demo Program ---

# Utility to load and sort frames from a directory
import os
def load_animation_frames(folder):
    # List all PNGs and sort by number in filename
    frame_files = [f for f in os.listdir(folder) if f.endswith('.png')]
    # Sort by the number in 'playerN.png'
    frame_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    frames = []
    for fname in frame_files:
        path = os.path.join(folder, fname)
        img = pygame.image.load(path).convert_alpha()
        frames.append(img)
    return frames

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    # Load real animation frames
    # Use correct case and path for asset folders
    base_dir = os.path.dirname(os.path.abspath(__file__))
    idle_folder = os.path.join(base_dir, '..', 'Assets', 'idle')
    walk_folder = os.path.join(base_dir, '..', 'Assets', 'walking')
    idle_folder = os.path.normpath(idle_folder)
    walk_folder = os.path.normpath(walk_folder)
    idle_frames = load_animation_frames(idle_folder)
    walk_frames = load_animation_frames(walk_folder)
    # Use uniform durations for simplicity
    idle_durations = [0.1] * len(idle_frames)
    walk_durations = [0.08] * len(walk_frames)
    idle_anim = Animation(idle_frames, idle_durations)
    walk_anim = Animation(walk_frames, walk_durations)
    controller = AnimationController({'idle': idle_anim, 'walk': walk_anim})
    # Center player horizontally and vertically
    player_x = (SCREEN_W - 64) // 2  # 64 is the frame width
    player_y = (SCREEN_H - 96) // 2  # 96 is the frame height
    player_vx = 0
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        speed = 0
        if keys[pygame.K_LEFT]:
            player_vx = -200
            controller.set_flip(True)
            speed = 1
        elif keys[pygame.K_RIGHT]:
            player_vx = 200
            controller.set_flip(False)
            speed = 1
        else:
            player_vx = 0
        player_x += player_vx * dt
        player_x = max(0, min(SCREEN_W-64, player_x))
        controller.set_speed_param(speed)
        controller.update(dt)
        screen.fill((30,30,30))
        frame = controller.get_frame()
        # Draw player centered
        screen.blit(frame, (player_x, player_y))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Blending logic: During cross-fade, we alpha-blend the current and target animation frames.
# For parameter blending, we update the walk animation at a speed proportional to the speed parameter.
# Performance: Only two surfaces are blended per frame, and frame counts can differ. For real games, optimize by pre-blending or using shaders.
# Challenge: Blending works best with matching frame rates/lengths; otherwise, visual artifacts may occur.
# Reflection: Animation blending creates smooth transitions but requires careful timing and resource management in 2D games.
