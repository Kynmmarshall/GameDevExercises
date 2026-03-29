# Exercise 1: Advanced Sprite Sheet Animation with Frame Events
#
# This program demonstrates an Animation class supporting per-frame durations, frame events, and on-complete callbacks.
# Comments explain the design and benefits.

import pygame
import sys

class Animation:
    def __init__(self, frames, durations):
        self.frames = frames  # list of pygame.Surface
        self.durations = durations if isinstance(durations, list) else [durations]
        self.current_frame = 0
        self.timer = 0
        self.playing = False
        self.loop = False
        self.frame_events = {}  # frame_index: callback
        self.on_complete = None

    def play(self, loop=False):
        self.current_frame = 0
        self.timer = 0
        self.playing = True
        self.loop = loop

    def add_frame_event(self, frame_index, callback):
        self.frame_events[frame_index] = callback

    def set_on_complete(self, callback):
        self.on_complete = callback

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def update(self, dt):
        if not self.playing:
            return
        # Use the correct duration for the current frame
        duration = self.durations[self.current_frame] if self.current_frame < len(self.durations) else self.durations[-1]
        self.timer += dt
        if self.timer >= duration:
            self.timer = 0
            self.current_frame += 1
            # Frame event callback
            if self.current_frame in self.frame_events:
                self.frame_events[self.current_frame]()
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
                    if self.on_complete:
                        self.on_complete()

# --- Demo Program ---

import os

# Helper to slice a sprite sheet into frames
def load_frames_from_sheet(path, frame_size, num_frames):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_size[0], 0, frame_size[0], frame_size[1])
        frame = sheet.subsurface(rect).copy()
        frames.append(frame)
    return frames

def main():
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    clock = pygame.time.Clock()
    # Load actual images from assets/animations
    base = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'Animations')
    idle_frames = load_frames_from_sheet(os.path.join(base, 'Ability_Use.png'), (128, 128), 10)
    punch_frames = load_frames_from_sheet(os.path.join(base, 'Punch_1.png'), (128, 128), 4)
    special_frames = load_frames_from_sheet(os.path.join(base, 'Explosive_Strike.png'), (128, 128), 9)

    # Idle animation: 6 frames, 0.1s each, looping
    idle_anim = Animation(idle_frames, [0.1]*6)
    idle_anim.play(loop=True)
    # Punch animation: 4 frames, [0.05, 0.1, 0.1, 0.2], non-looping
    punch_anim = Animation(punch_frames, [0.05, 0.1, 0.1, 0.2])
    punch_anim.add_frame_event(2, lambda: print("Punch lands!"))
    # Special attack animation: 9 frames, 0.08s each, non-looping
    special_anim = Animation(special_frames, [0.08]*9)
    special_anim.add_frame_event(4, lambda: print("Special attack effect!"))

    # On complete: return to idle
    def to_idle():
        idle_anim.play(loop=True)
        player['anim'] = idle_anim
    punch_anim.set_on_complete(to_idle)
    special_anim.set_on_complete(to_idle)

    # Player dict
    player = {'x': 96, 'y': 56, 'anim': idle_anim}
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    punch_anim.play(loop=False)
                    player['anim'] = punch_anim
                if event.key == pygame.K_s:
                    special_anim.play(loop=False)
                    player['anim'] = special_anim
        player['anim'].update(dt)
        screen.fill((30,30,30))
        screen.blit(player['anim'].get_current_frame(), (player['x'], player['y']))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Benefits: This design allows precise control over animation timing and game events (e.g., sounds, effects) at specific frames.
# Per-frame durations enable more expressive, realistic animations. Frame and completion callbacks make it easy to coordinate game logic with animation flow.
