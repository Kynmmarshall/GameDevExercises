"""
Exercise 1: Game Loop Analysis and Delta Time

1. Problems in the original code:
- Movement is frame-rate dependent because the player moves a fixed number of pixels per frame (speed = 5), so higher FPS means faster movement.
- The window can freeze on quit because sys.exit() is called inside the event loop, which can interrupt Pygame's cleanup.
- No structure: all logic is in the global scope, making it hard to maintain or extend.
- No FPS counter for debugging performance.

Delta time solves frame-rate dependence by scaling movement by the time elapsed since the last frame, ensuring consistent speed regardless of FPS.
"""

import pygame
import sys

class Game:
	def __init__(self):
		"""Initializes Pygame, window, clock, player, and variables."""
		pygame.init()
		self.screen = pygame.display.set_mode((800, 600))
		pygame.display.set_caption("Delta Time Game")
		self.clock = pygame.time.Clock()
		self.player = pygame.Rect(400, 300, 50, 50)
		self.speed = 300  # pixels per second
		self.running = True

	def handle_events(self):
		"""Processes QUIT and other events."""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

	def update(self, dt):
		"""Moves the player using delta time (dt in seconds)."""
		keys = pygame.key.get_pressed()
		# Move left/right with frame-rate independent speed
		if keys[pygame.K_LEFT]:
			self.player.x -= int(self.speed * dt)
		if keys[pygame.K_RIGHT]:
			self.player.x += int(self.speed * dt)

	def draw(self):
		"""Draws the player rectangle."""
		self.screen.fill((0, 0, 0))
		pygame.draw.rect(self.screen, (0, 255, 0), self.player)
		pygame.display.flip()

	def run(self):
		"""Main loop: handles events, updates, draws, and manages FPS/delta time."""
		while self.running:
			self.handle_events()
			# clock.tick returns milliseconds since last call; convert to seconds for dt
			dt = self.clock.tick(60) / 1000.0
			self.update(dt)
			self.draw()
			# Show FPS in window title
			fps = self.clock.get_fps()
			pygame.display.set_caption(f"Delta Time Game - FPS: {fps:.2f}")
		pygame.quit()
		sys.exit()

if __name__ == "__main__":
	game = Game()
	game.run()


#Reflection:

# Delta time is crucial in game development to ensure consistent movement and gameplay
# across different hardware and frame rates. Without delta time, objects move faster on
# high-FPS systems and slower on low-FPS ones, leading to unfair or broken gameplay.

# By multiplying movement and animations by the time elapsed since the last frame,
# delta time decouples game logic from rendering speed, resulting in smooth and
# predictable behavior regardless of performance.

# This makes games more robust, fair, and enjoyable for all players, regardless of their hardware capabilities.