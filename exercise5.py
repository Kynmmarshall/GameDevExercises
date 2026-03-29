# Exercise 5: Game State Machine with Stack
#
# This implementation uses a stack-based state machine for clean handling of nested game states (menu, play, pause, game over).
# Each state is an object that handles its own events, updates, and drawing.
# The stack allows for easy pausing/resuming and overlaying states (e.g., pause menu over gameplay).
#
# Reflection: Using a stack for game states allows you to pause the game, show overlays, and return to previous states without losing their data or logic. This is much cleaner than a single-state approach, especially for nested or modal states.

import pygame
import sys

# --- Base State ---
class GameState:
    def handle_events(self, events): pass
    def update(self, dt): pass
    def draw(self, screen): pass

# --- Game State Machine ---
class Game:
    def __init__(self):
        self.stack = []
    def push_state(self, state): self.stack.append(state)
    def pop_state(self): return self.stack.pop()
    def change_state(self, state): self.stack = [state]
    def current_state(self): return self.stack[-1] if self.stack else None

# --- Menu State ---
class MenuState(GameState):
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [("Start Game", (300, 200)), ("Quit", (300, 300))]
        self.button_rects = [pygame.Rect(x, y, 200, 60) for _, (x, y) in self.buttons]
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(event.pos):
                        if i == 0:
                            self.game.push_state(PlayState(self.game))
                        elif i == 1:
                            pygame.quit(); sys.exit()
    def update(self, dt): pass
    def draw(self, screen):
        screen.fill((40, 40, 80))
        for (text, (x, y)), rect in zip(self.buttons, self.button_rects):
            pygame.draw.rect(screen, (100, 100, 200), rect)
            label = self.font.render(text, True, (255, 255, 255))
            screen.blit(label, (x + 20, y + 10))

# --- Play State ---
class PlayState(GameState):
    def __init__(self, game):
        self.game = game
        self.player = pygame.Rect(390, 290, 40, 40)
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.game.push_state(PauseState(self.game))
    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 300 * dt
        if keys[pygame.K_LEFT]: self.player.x -= int(speed)
        if keys[pygame.K_RIGHT]: self.player.x += int(speed)
        if keys[pygame.K_UP]: self.player.y -= int(speed)
        if keys[pygame.K_DOWN]: self.player.y += int(speed)
        self.player.x = max(0, min(self.player.x, 760))
        self.player.y = max(0, min(self.player.y, 560))
        self.score += int(500 * dt)  # Simulate scoring over time
        # Simulate game over
        if self.score > 1000:
            self.game.push_state(GameOverState(self.game, self.score))
    def draw(self, screen):
        screen.fill((30, 120, 30))
        pygame.draw.rect(screen, (255, 200, 0), self.player)
        label = self.font.render(f"Score: {self.score}", True, (255,255,255))
        screen.blit(label, (10, 10))

# --- Pause State ---
class PauseState(GameState):
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 72)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.game.pop_state()  # Resume game
    def update(self, dt): pass
    def draw(self, screen):
        # Draw previous state (gameplay) behind pause overlay
        self.game.stack[-2].draw(screen)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        label = self.font.render("Paused", True, (255,255,255))
        screen.blit(label, (270, 220))

# --- Game Over State ---
class GameOverState(GameState):
    def __init__(self, game, score):
        self.game = game
        self.score = score
        self.font = pygame.font.SysFont(None, 60)
        self.button_rect = pygame.Rect(300, 350, 200, 60)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(event.pos):
                    self.game.change_state(MenuState(self.game))
    def update(self, dt): pass
    def draw(self, screen):
        screen.fill((80, 30, 30))
        label = self.font.render(f"Game Over! Score: {self.score}", True, (255,255,255))
        screen.blit(label, (120, 200))
        pygame.draw.rect(screen, (200, 100, 100), self.button_rect)
        btn_label = self.font.render("Main Menu", True, (255,255,255))
        screen.blit(btn_label, (self.button_rect.x + 10, self.button_rect.y + 10))

# --- Main Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    game = Game()
    game.push_state(MenuState(game))
    while game.current_state():
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        game.current_state().handle_events(events)
        game.current_state().update(dt)
        game.current_state().draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
