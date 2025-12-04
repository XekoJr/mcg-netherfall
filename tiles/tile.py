import pygame

class Tile:
    def __init__(self, tile_type, x, y, image=None):
        self.tile_type = tile_type  # "grass", "tree", "bush", "wall"
        self.x = x  # Grid position
        self.y = y
        self.image = image
        self.rect = pygame.Rect(x * 20, y * 20, 20, 20)
        
        # Collision properties
        self.blocks_player = False
        self.blocks_enemy = False
        self.blocks_projectile = False
        self.footstep_sound = None
        
        self.load_properties()
    
    def load_properties(self):
        # Set properties based on tile_type
        if self.tile_type in ["tree", "bush", "wall"]:
            self.blocks_player = True
            self.blocks_enemy = True
            self.blocks_projectile = True
        
        # Set footstep sounds
        if self.tile_type == "grass":
            self.footstep_sound = "grass_step"
        elif self.tile_type == "stone":
            self.footstep_sound = "stone_step"
