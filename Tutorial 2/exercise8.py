"""
Exercise 8: UI System with Menus, Buttons, and Event Propagation (Difficult)
Implements a UI system with event propagation, menus, buttons, and a simple game state manager.
Event propagation is handled so that UI elements consume events and block them from reaching game logic when active.
"""
import pygame
import sys

SCREEN_W, SCREEN_H = 800, 600
FONT_NAME = None

# --- UI System ---
class UIElement:
    def __init__(self, x, y, w, h, visible=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = visible
    def handle_event(self, event):
        return False  # Return True if event is consumed
    def update(self, dt):
        pass
    def draw(self, screen):
        pass

class Button(UIElement):
    def __init__(self, x, y, w, h, text, callback, font, colors):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font = font
        self.colors = colors  # (normal, hover, pressed)
        self.state = 'normal'
        self.pressed = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if not self.pressed:
                    self.state = 'hover'
            else:
                self.state = 'normal'
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = 'pressed'
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                self.state = 'hover'
                self.callback()
                return True
            self.pressed = False
            self.state = 'normal'
        return False
    def draw(self, screen):
        color = self.colors[0]
        if self.state == 'hover':
            color = self.colors[1]
        elif self.state == 'pressed':
            color = self.colors[2]
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (40,40,40), self.rect, 2)
        text_surf = self.font.render(self.text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class UILabel(UIElement):
    def __init__(self, x, y, text, font, color=(255,255,255)):
        surf = font.render(text, True, color)
        super().__init__(x, y, surf.get_width(), surf.get_height())
        self.text = text
        self.font = font
        self.color = color
        self.surf = surf
    def set_text(self, text):
        self.text = text
        self.surf = self.font.render(self.text, True, self.color)
    def draw(self, screen):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

class UIPanel(UIElement):
    def __init__(self, x, y, w, h, color=(80,80,80,200)):
        super().__init__(x, y, w, h)
        self.color = color
    def draw(self, screen):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.color)
        screen.blit(s, (self.rect.x, self.rect.y))

class UIManager:
    def __init__(self):
        self.elements = []
    def add_element(self, element):
        self.elements.append(element)
    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)
    def handle_events(self, events):
        for event in events:
            for elem in reversed(self.elements):
                if elem.visible and elem.handle_event(event):
                    return True  # Event consumed, block propagation
        return False
    def update(self, dt):
        for elem in self.elements:
            if elem.visible:
                elem.update(dt)
    def draw(self, screen):
        for elem in self.elements:
            if elem.visible:
                elem.draw(screen)

# --- Game State Manager ---
MENU, GAME, PAUSE = 0, 1, 2

def main():
    pygame.init()
    global FONT_NAME
    FONT_NAME = pygame.font.get_default_font()
    font = pygame.font.Font(FONT_NAME, 32)
    small_font = pygame.font.Font(FONT_NAME, 24)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    state = MENU
    ui = UIManager()
    score = 0
    health = 100
    # --- UI Setup ---
    def start_game():
        nonlocal state
        state = GAME
        ui.elements.clear()
    def quit_game():
        pygame.quit()
        sys.exit()
    def resume_game():
        nonlocal state
        state = GAME
        ui.elements.clear()
    def main_menu():
        nonlocal state
        state = MENU
        ui.elements.clear()
        setup_menu()
    def setup_menu():
        ui.add_element(UIPanel(250, 150, 300, 300))
        ui.add_element(Button(300, 220, 200, 60, "Start Game", start_game, font, [(200,200,200),(220,220,100),(180,180,60)]))
        ui.add_element(Button(300, 320, 200, 60, "Quit", quit_game, font, [(200,200,200),(220,220,100),(180,180,60)]))
    def setup_pause():
        ui.add_element(UIPanel(250, 150, 300, 300))
        ui.add_element(Button(300, 220, 200, 60, "Resume", resume_game, font, [(200,200,200),(220,220,100),(180,180,60)]))
        ui.add_element(Button(300, 320, 200, 60, "Main Menu", main_menu, font, [(200,200,200),(220,220,100),(180,180,60)]))
    setup_menu()
    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(60) / 1e3
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        # --- State Handling ---
        if state == MENU:
            ui.handle_events(events)
            ui.update(dt)
            screen.fill((40,40,60))
            ui.draw(screen)
        elif state == GAME:
            # Game logic (simple demo)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                state = PAUSE
                ui.elements.clear()
                setup_pause()
            # Update score/health for demo
            score += 1 * dt
            health = max(0, health - 5 * dt)
            # Draw game
            screen.fill((60,120,60))
            # HUD
            score_lbl = UILabel(20, 20, f"Score: {int(score)}", small_font)
            health_lbl = UILabel(20, 60, f"Health: {int(health)}", small_font)
            score_lbl.draw(screen)
            health_lbl.draw(screen)
        elif state == PAUSE:
            if ui.handle_events(events):
                pass  # UI consumed event
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_p]:
                    state = GAME
                    ui.elements.clear()
            ui.update(dt)
            screen.fill((40,40,60))
            ui.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

# ---
# Event propagation: UIManager.handle_events returns True if any UI element consumes the event, blocking further handling.
# This prevents game logic from responding to input when menus are active, which is critical for robust UI systems.
# Buttons change color on hover/press, and menus are managed by game state.
