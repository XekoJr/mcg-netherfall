import pygame

class Prop:
    """Decorative prop/object that can be placed on tilesets"""
    
    def __init__(self, prop_type, x, y, width, height, image=None, collidable=True, blocks_projectiles=False):
        """Initialize a prop """
        self.prop_type = prop_type
        self.tile_x = x
        self.tile_y = y
        self.width_tiles = width
        self.height_tiles = height
        self.image = image
        self.collidable = collidable
        
        # Create rect in pixel coordinates (20 pixels per tile)
        # NOTE: This rect is just for the base definition - actual world rect is created in tile_manager
        self.rect = pygame.Rect(
            0,  # Placeholder - will be set by tile_manager during map generation
            0,
            width * 20,  # width_tiles * tile_size
            height * 20  # height_tiles * tile_size
        )
        
        # Collision properties
        self.blocks_player = collidable
        self.blocks_enemy = collidable
        self.blocks_projectile = blocks_projectiles
    
    def render(self, screen, camera_offset):
        """Render the prop with camera offset"""
        if self.image:
            render_x = self.rect.x - camera_offset[0]
            render_y = self.rect.y - camera_offset[1]
            screen.blit(self.image, (render_x, render_y))
