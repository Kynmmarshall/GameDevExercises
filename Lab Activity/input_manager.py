# input_manager.py
# InputManager with action mapping and observer pattern

import pygame

class InputManager:
    def __init__(self):
        self.action_key_map = {}
        self.listeners = {}
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
            if just_pressed:
                for listener in self.listeners.get(action, []):
                    listener.on_action(action)

    def is_action_pressed(self, action):
        key = self.action_key_map.get(action)
        return key in self.current_keys if key is not None else False

    def is_action_just_pressed(self, action):
        key = self.action_key_map.get(action)
        return (key not in self.prev_keys) and (key in self.current_keys) if key is not None else False
