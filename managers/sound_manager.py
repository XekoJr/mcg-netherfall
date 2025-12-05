import pygame

class SoundManager:
    """Manages all game sounds and music.""" # Not Being Used Yet
    
    def __init__(self):
        self.sounds = {}
        self.music = {}
        self.master_volume = 1.0
        self.music_volume = 1.0
        self.effects_volume = 1.0
    
    def load_sound(self, name, path):
        """Load a sound effect."""
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f" Failed to load {name}: {e}")
            return False
    
    def play(self, name, loops=0):
        """Play a sound by name."""
        if name in self.sounds:
            self.sounds[name].play(loops)
    
    def stop(self, name):
        """Stop a sound by name."""
        if name in self.sounds:
            self.sounds[name].stop()