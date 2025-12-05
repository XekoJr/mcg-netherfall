import pygame
import random
from .tile import Tile
from .tileset_definitions import BOSS_ARENA_1, REGULAR_TILESETS

class TileManager:
    """150x150 tile map (3000x3000px) using 5x5 tileset grid"""
    def __init__(self, width, height, tile_size=20):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.collision_grid = {}
        self.boss_spawn_position = None
        self.show_hitboxes = False
        self.placed_tilesets = []
        self.tileset_occupancy = [[False for _ in range(5)] for _ in range(5)]
        
    def generate_map(self):
        self._place_boss_arena()
        self._place_regular_tilesets()
        self.build_collision_hash()
        
    def _place_boss_arena(self):
        """Place the boss arena tileset at center of 5x5 grid"""
        boss_tileset = BOSS_ARENA_1
        tileset_slot_x = 2
        tileset_slot_y = 2
        start_x = tileset_slot_x * 30
        start_y = tileset_slot_y * 30
        
        self._place_tileset(boss_tileset, start_x, start_y)
        self.tileset_occupancy[tileset_slot_y][tileset_slot_x] = True
        
        spawn_tile_x = start_x + boss_tileset.spawn_point[0]
        spawn_tile_y = start_y + boss_tileset.spawn_point[1]
        self.boss_spawn_position = (spawn_tile_x * self.tile_size, spawn_tile_y * self.tile_size)
    
    def _place_regular_tilesets(self):
        """Place random regular tilesets in remaining 5x5 grid slots"""
        for slot_y in range(5):
            for slot_x in range(5):
                # Skip if already occupied (boss arena)
                if self.tileset_occupancy[slot_y][slot_x]:
                    continue
                
                if random.random() < 0.8:
                    tileset = random.choice(REGULAR_TILESETS)
                    start_x = slot_x * 30
                    start_y = slot_y * 30
                    self._place_tileset(tileset, start_x, start_y)
                    self.tileset_occupancy[slot_y][slot_x] = True
    
    def _place_tileset(self, tileset, start_x, start_y):
        """Place a tileset on the map at the given position"""
        self.placed_tilesets.append((tileset, start_x, start_y))
    
    def toggle_hitboxes(self):
        """Toggle debug hitbox rendering."""
        self.show_hitboxes = not self.show_hitboxes
        return self.show_hitboxes
    
    def build_collision_hash(self):
        """Collision detection"""
        self.collision_grid = {}
        cell_size = 100
        total_props = 0
        collidable_props = 0
        
        for tileset, start_x_tiles, start_y_tiles in self.placed_tilesets:
            for prop in tileset.props:
                total_props += 1
                if prop.collidable:
                    collidable_props += 1
                    prop_world_rect = pygame.Rect(
                        (start_x_tiles + prop.tile_x) * self.tile_size,
                        (start_y_tiles + prop.tile_y) * self.tile_size,
                        prop.width_tiles * self.tile_size,
                        prop.height_tiles * self.tile_size
                    )
                    
                    min_cell_x = prop_world_rect.left // cell_size
                    max_cell_x = prop_world_rect.right // cell_size
                    min_cell_y = prop_world_rect.top // cell_size
                    max_cell_y = prop_world_rect.bottom // cell_size
                    
                    cells_added = 0
                    for cell_x in range(min_cell_x, max_cell_x + 1):
                        for cell_y in range(min_cell_y, max_cell_y + 1):
                            key = (cell_x, cell_y)
                            if key not in self.collision_grid:
                                self.collision_grid[key] = []
                            self.collision_grid[key].append({
                                'rect': prop_world_rect,
                                'prop': prop
                            })
                            cells_added += 1
    
    def check_collision(self, rect, entity_type, debug=False):
        """Check if collides with props"""
        cell_size = 100
        min_cell_x = rect.left // cell_size
        max_cell_x = rect.right // cell_size
        min_cell_y = rect.top // cell_size
        max_cell_y = rect.bottom // cell_size

        
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                key = (cell_x, cell_y)
                if key in self.collision_grid:
                    if debug:
                        print(f" Cell {key} has {len(self.collision_grid[key])} props")
                    for prop_data in self.collision_grid[key]:
                        prop_rect = prop_data['rect']
                        prop_obj = prop_data['prop']
                        
                        should_block = False
                        if entity_type == "projectile":
                            should_block = prop_obj.blocks_projectile
                        elif entity_type == "player":
                            should_block = prop_obj.blocks_player
                        elif entity_type == "enemy":
                            should_block = prop_obj.blocks_enemy
                        
                        if should_block and rect.colliderect(prop_rect):
                            return True
        
        return False
    
    def render(self, screen, camera_offset):
        """Render visible tilesets (background images + props) with viewport culling"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        screen.fill((0, 0, 0))
        
        # Calculate visible tileset range
        tileset_pixel_size = 30 * self.tile_size  # 600 pixels
        
        if self.show_hitboxes and not hasattr(self, '_last_render_log'):
            self._last_render_log = 0
        
        import time
        current_time = time.time()
        if self.show_hitboxes and (current_time - self._last_render_log > 1.0):
            self._last_render_log = current_time
        
        rendered_count = 0
        culled_count = 0
        
        # Render each placed tileset
        for tileset, start_x_tiles, start_y_tiles in self.placed_tilesets:
            # Calculate tileset position in pixels
            tileset_x = start_x_tiles * self.tile_size
            tileset_y = start_y_tiles * self.tile_size
            
            margin = 50
            is_culled = (tileset_x + tileset_pixel_size < camera_offset[0] - margin or
                        tileset_x > camera_offset[0] + screen_width + margin or
                        tileset_y + tileset_pixel_size < camera_offset[1] - margin or
                        tileset_y > camera_offset[1] + screen_height + margin)
            
            if is_culled:
                culled_count += 1
                if self.show_hitboxes and hasattr(self, '_last_render_log'):
                    if current_time - self._last_render_log < 0.1:
                        reasons = []
                        if tileset_x + tileset_pixel_size < camera_offset[0] - margin:
                            reasons.append("LEFT")
                        if tileset_x > camera_offset[0] + screen_width + margin:
                            reasons.append("RIGHT")
                        if tileset_y + tileset_pixel_size < camera_offset[1] - margin:
                            reasons.append("TOP")
                        if tileset_y > camera_offset[1] + screen_height + margin:
                            reasons.append("BOTTOM")
                continue
            
            rendered_count += 1
            
            if tileset.background_image:
                screen_x = tileset_x - camera_offset[0]
                screen_y = tileset_y - camera_offset[1]
                screen.blit(tileset.background_image, (screen_x, screen_y))
            else:
                if not hasattr(self, '_logged_missing_bg'):
                    self._logged_missing_bg = set()
                if tileset.name not in self._logged_missing_bg:
                    self._logged_missing_bg.add(tileset.name)
            
            # Render props on this tileset
            for prop in tileset.props:
                prop_x = (start_x_tiles + prop.tile_x) * self.tile_size
                prop_y = (start_y_tiles + prop.tile_y) * self.tile_size
                
                # Check if prop is visible
                prop_width = prop.width_tiles * self.tile_size
                prop_height = prop.height_tiles * self.tile_size
                
                if (prop_x + prop_width < camera_offset[0] or
                    prop_x > camera_offset[0] + screen_width or
                    prop_y + prop_height < camera_offset[1] or
                    prop_y > camera_offset[1] + screen_height):
                    continue
                
                # Render prop
                if prop.image:
                    screen_x = prop_x - camera_offset[0]
                    screen_y = prop_y - camera_offset[1]
                    screen.blit(prop.image, (screen_x, screen_y))
                elif self.show_hitboxes:
                    if not hasattr(self, '_logged_missing_props'):
                        self._logged_missing_props = set()
                    if prop.prop_type not in self._logged_missing_props:
                        self._logged_missing_props.add(prop.prop_type)
                
                # Draw debug hitbox if enabled
                if hasattr(self, 'show_hitboxes') and self.show_hitboxes:
                    hitbox_rect = pygame.Rect(
                        prop_x - camera_offset[0],
                        prop_y - camera_offset[1],
                        prop_width,
                        prop_height
                    )
                    if prop.blocks_projectile:
                        color = (255, 0, 0, 128)  # Red - blocks projectiles
                    elif prop.collidable:
                        color = (0, 255, 0, 128)  # Green - blocks movement only
                    else:
                        color = (0, 0, 255, 128)  # Blue - non-collidable
                    pygame.draw.rect(screen, color, hitbox_rect, 2)
