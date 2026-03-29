Lab Activity - Arcade Game Project
==================================

Files:
------
arcade_game.py      - Main game file (run this to play)
components.py       - ECS component definitions
entities.py         - Entity creation helpers
systems.py          - ECS systems and Entity class
input_manager.py    - Input manager with observer pattern
grid.py             - Spatial grid for collision detection

How to Run:
-----------
- Requires Python 3 and pygame installed.
- Run the game with: python arcade_game.py

Game Controls:
--------------
- Left/Right arrows: Move player
- Space: Shoot
- R: Restart after game over

Features:
---------
- Player, enemies, and bullets are all entities with components.
- InputManager maps keys to actions and supports observers.
- SpatialGrid optimizes collision checks.
- Score and game over screen included.

See the report for UML, explanations, and screenshots.
