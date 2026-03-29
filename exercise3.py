# Exercise 3: Input Manager with Observer Pattern
#
# This implementation demonstrates an InputManager that supports both polling and event-driven (observer) input handling.
# Listeners can subscribe to logical actions (e.g., "jump") and are notified when those actions occur.
#
# The observer pattern decouples input handling from game logic, making the code more modular and reusable.

import pygame

# --- InputManager with Observer Pattern ---
class InputManager:
	def __init__(self):
		self.action_key_map = {}  # action -> key
		self.listeners = {}       # action -> list of listeners
		self.current_keys = set()
		self.prev_keys = set()

	def map_action(self, action, key):
		self.action_key_map[action] = key

	def add_listener(self, action, listener):
		if action not in self.listeners:
			self.listeners[action] = []
		self.listeners[action].append(listener)

	def update(self):
		self.prev_keys = self.current_keys.copy()
		pressed = pygame.key.get_pressed()
		self.current_keys = set(
			key for action, key in self.action_key_map.items() if pressed[key]
		)
		# Notify listeners for edge events
		for action, key in self.action_key_map.items():
			just_pressed = (key not in self.prev_keys) and (key in self.current_keys)
			just_released = (key in self.prev_keys) and (key not in self.current_keys)
			if just_pressed or just_released:
				for listener in self.listeners.get(action, []):
					listener.on_action(action, 'pressed' if just_pressed else 'released')

	def is_action_pressed(self, action):
		key = self.action_key_map.get(action)
		return key in self.current_keys if key is not None else False

	def is_action_just_pressed(self, action):
		key = self.action_key_map.get(action)
		return (key not in self.prev_keys) and (key in self.current_keys) if key is not None else False

	def is_action_just_released(self, action):
		key = self.action_key_map.get(action)
		return (key in self.prev_keys) and (key not in self.current_keys) if key is not None else False

# --- Example Listeners ---
class Player:
	def __init__(self):
		self.jumping = False

	def on_action(self, action, state):
		if action == "jump" and state == "pressed":
			self.jumping = True
			print("Player: Jump!")

# Simulated AudioManager
class AudioManager:
	def on_action(self, action, state):
		if action == "jump" and state == "pressed":
			print("AudioManager: Play jump sound!")

# --- Main Game Loop ---
def main():
	pygame.init()
	screen = pygame.display.set_mode((400, 300))
	clock = pygame.time.Clock()
	running = True

	# Set up input manager and listeners
	input_manager = InputManager()
	input_manager.map_action("jump", pygame.K_SPACE)
	player = Player()
	audio = AudioManager()
	input_manager.add_listener("jump", player)
	input_manager.add_listener("jump", audio)

	rect_y = 200
	velocity = 0
	gravity = 1

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		input_manager.update()

		# Polling example (in addition to observer):
		if input_manager.is_action_just_pressed("jump") and not player.jumping:
			velocity = -15
			print("[Polling] Player jumps!")
		if player.jumping:
			player.jumping = False  # Reset after jump

		# Simple gravity and jump
		rect_y += velocity
		velocity += gravity
		if rect_y > 200:
			rect_y = 200
			velocity = 0

		screen.fill((30, 30, 30))
		pygame.draw.rect(screen, (0, 200, 0), (180, rect_y, 40, 40))
		pygame.display.flip()
		clock.tick(60)

	pygame.quit()

if __name__ == "__main__":
	main()

# ---
# Observer Pattern Explanation:
# The observer pattern allows objects (listeners) to subscribe to events (actions) in the InputManager.
# When an action occurs, all listeners are notified via their on_action method.
# This decouples input handling from game logic, making the code modular and easy to extend.

# Event-driven vs Polling Input Models:
# - Event-driven: Listeners are notified only when an event occurs (e.g., key pressed). Good for UI, menus, or when many systems need to react to the same input.
# - Polling: The game checks input state every frame. Good for continuous actions (e.g., holding a movement key).
#
# Scenarios:
# 1. Event-driven is better for triggering a sound or animation when a button is pressed (one-time events).
# 2. Polling is better for moving a character while a key is held down (continuous actions).
