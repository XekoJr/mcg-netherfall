import pygame
import random
from .tile import Tile
from .tileset_definitions import BOSS_ARENA_1, REGULAR_TILESETS

class TileManager:
    """
    Manages the tile-based map system:
    - Map: 150x150 tiles (3000x3000 pixels at 20px/tile)
    - Grid: 5x5 tilesets
    - Each tileset: 30x30 tiles = 600x600 pixels
    - Background images: 600x600 pixels (scaled from 300x300)
    - Props: Various sizes (1x1 to 3x2 tiles)
    """
    def __init__(self, width, height, tile_size=20):
        self.width = width  # Number of tiles (e.g., 150 for 5x5 tilesets of 30x30 each)
        self.height = height
        self.tile_size = tile_size
        self.collision_grid = {}  # Spatial hash for collision detection
        self.boss_spawn_position = None  # (x, y) in pixels
        self.show_hitboxes = False  # Toggle for debug hitbox rendering
        
        # Track placed tilesets with their positions and data
        self.placed_tilesets = []  # List of (tileset, start_x, start_y) tuples
        
        # 2D occupancy array to track which tileset slots are occupied (5x5 grid)
        self.tileset_occupancy = [[False for _ in range(5)] for _ in range(5)]
        
    def generate_map(self):
        """Generate the map by placing boss arena first, then random tilesets"""
        print("\n=== MAP GENERATION START ===")
        # Step 1: Place boss spawn tileset at center (MUST be placed first)
        self._place_boss_arena()
        
        # Step 2: Place random regular tilesets (fill remaining 5x5 grid)
        self._place_regular_tilesets()
        
        print(f"Total tilesets placed: {len(self.placed_tilesets)}")
        
        # Step 3: Build spatial collision hash for performance (including props)
        self.build_collision_hash()
        print("=== MAP GENERATION COMPLETE ===\n")
        
    def _place_boss_arena(self):
        """Place the boss arena tileset at center of 5x5 grid"""
        boss_tileset = BOSS_ARENA_1
        
        # Place at center of 5x5 grid (position 2,2)
        tileset_slot_x = 2
        tileset_slot_y = 2
        
        # Convert to tile coordinates (each tileset is 30x30)
        start_x = tileset_slot_x * 30
        start_y = tileset_slot_y * 30
        
        # Store the tileset placement
        self._place_tileset(boss_tileset, start_x, start_y)
        self.tileset_occupancy[tileset_slot_y][tileset_slot_x] = True
        
        # Store boss spawn position in pixels
        spawn_tile_x = start_x + boss_tileset.spawn_point[0]
        spawn_tile_y = start_y + boss_tileset.spawn_point[1]
        self.boss_spawn_position = (spawn_tile_x * self.tile_size, spawn_tile_y * self.tile_size)
    
    def _place_regular_tilesets(self):
        """Place random regular tilesets in remaining 5x5 grid slots"""
        # Fill most of the remaining 24 slots (minus the center boss arena)
        for slot_y in range(5):
            for slot_x in range(5):
                # Skip if already occupied (boss arena)
                if self.tileset_occupancy[slot_y][slot_x]:
                    continue
                
                # 80% chance to place a tileset in each slot
                if random.random() < 0.8:
                    tileset = random.choice(REGULAR_TILESETS)
                    start_x = slot_x * 30
                    start_y = slot_y * 30
                    self._place_tileset(tileset, start_x, start_y)
                    self.tileset_occupancy[slot_y][slot_x] = True
    
    def _place_tileset(self, tileset, start_x, start_y):
        """Place a tileset on the map at the given position"""
        # Store tileset with position for rendering
        self.placed_tilesets.append((tileset, start_x, start_y))
        
        # Log tileset placement
        pixel_x = start_x * self.tile_size
        pixel_y = start_y * self.tile_size
        # Calculate grid position (each tileset is 30 tiles)
        grid_x = start_x // 30
        grid_y = start_y // 30
        print(f"  Placed '{tileset.name}' at grid({grid_x},{grid_y}) tiles({start_x},{start_y}) = pixels({pixel_x},{pixel_y})")
        print(f"    Background: {'LOADED' if tileset.background_image else 'MISSING'}")
        print(f"    Props: {len(tileset.props)}")
    
    def toggle_hitboxes(self):
        """Toggle debug hitbox rendering."""
        self.show_hitboxes = not self.show_hitboxes
        state = "ON" if self.show_hitboxes else "OFF"
        print(f"[DEBUG] Prop hitboxes: {state}")
        return self.show_hitboxes
    
    def build_collision_hash(self):
        """Build spatial hash for fast collision detection (props only)"""
        self.collision_grid = {}
        cell_size = 100  # pixels
        
        print("\n=== BUILDING COLLISION HASH ===")
        total_props = 0
        collidable_props = 0
        
        # Add all props from placed tilesets to collision hash
        for tileset, start_x_tiles, start_y_tiles in self.placed_tilesets:
            for prop in tileset.props:
                total_props += 1
                if prop.collidable:
                    collidable_props += 1
                    # Adjust prop position based on tileset placement
                    prop_world_rect = pygame.Rect(
                        (start_x_tiles + prop.tile_x) * self.tile_size,
                        (start_y_tiles + prop.tile_y) * self.tile_size,
                        prop.width_tiles * self.tile_size,
                        prop.height_tiles * self.tile_size
                    )
                    
                    # Add to ALL cells the prop overlaps
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
                            # Store both rect and prop object for entity-specific blocking
                            self.collision_grid[key].append({
                                'rect': prop_world_rect,
                                'prop': prop
                            })
                            cells_added += 1
                    
                    print(f"  Prop '{prop.prop_type}' at world({prop_world_rect.x},{prop_world_rect.y}) size({prop_world_rect.width}x{prop_world_rect.height}) -> {cells_added} cells")
        
        print(f"\nCollision Summary:")
        print(f"  Total props: {total_props}")
        print(f"  Collidable props: {collidable_props}")
        print(f"  Non-collidable props: {total_props - collidable_props}")
        print(f"  Collision cells with data: {len(self.collision_grid)}")
        print("=== COLLISION HASH COMPLETE ===\n")
    
    def check_collision(self, rect, entity_type, debug=False):
        """Check if rect collides with props (respects entity-specific blocking)"""
        cell_size = 100
        # Check which cells the rect overlaps
        min_cell_x = rect.left // cell_size
        max_cell_x = rect.right // cell_size
        min_cell_y = rect.top // cell_size
        max_cell_y = rect.bottom // cell_size
        
        if debug:
            print(f"\n[COLLISION CHECK] Entity: {entity_type}, Rect: ({rect.x},{rect.y}) size({rect.width}x{rect.height})")
            print(f"  Checking cells: x({min_cell_x}-{max_cell_x}) y({min_cell_y}-{max_cell_y})")
        
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                key = (cell_x, cell_y)
                if key in self.collision_grid:
                    if debug:
                        print(f"  Cell {key} has {len(self.collision_grid[key])} props")
                    for prop_data in self.collision_grid[key]:
                        prop_rect = prop_data['rect']
                        prop_obj = prop_data['prop']
                        
                        # Check if this prop blocks this entity type
                        should_block = False
                        if entity_type == "projectile":
                            should_block = prop_obj.blocks_projectile
                        elif entity_type == "player":
                            should_block = prop_obj.blocks_player
                        elif entity_type == "enemy":
                            should_block = prop_obj.blocks_enemy
                        
                        if should_block and rect.colliderect(prop_rect):
                            if debug:
                                print(f"  COLLISION! With prop at ({prop_rect.x},{prop_rect.y}) size({prop_rect.width}x{prop_rect.height})")
                            return True
        
        if debug:
            print("  No collision")
        return False
    
    def render(self, screen, camera_offset):
        """Render visible tilesets (background images + props) with viewport culling"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Fill screen with black to ensure no menu background shows through
        screen.fill((0, 0, 0))
        
        # Calculate visible tileset range (each tileset is 30x30 tiles = 600x600 pixels)
        tileset_pixel_size = 30 * self.tile_size  # 600 pixels
        
        # Debug logging (only once per second to avoid spam)
        if self.show_hitboxes and not hasattr(self, '_last_render_log'):
            self._last_render_log = 0
        
        import time
        current_time = time.time()
        if self.show_hitboxes and (current_time - self._last_render_log > 1.0):
            print(f"\n[RENDER DEBUG] Camera: ({int(camera_offset[0])},{int(camera_offset[1])}) Screen: {screen_width}x{screen_height}")
            self._last_render_log = current_time
        
        rendered_count = 0
        culled_count = 0
        
        # Render each placed tileset
        for tileset, start_x_tiles, start_y_tiles in self.placed_tilesets:
            # Calculate tileset position in pixels
            tileset_x = start_x_tiles * self.tile_size
            tileset_y = start_y_tiles * self.tile_size
            
            # Check if tileset is visible (with small margin to prevent edge flickering)
            margin = 50  # Extra pixels to render just off-screen
            is_culled = (tileset_x + tileset_pixel_size < camera_offset[0] - margin or
                        tileset_x > camera_offset[0] + screen_width + margin or
                        tileset_y + tileset_pixel_size < camera_offset[1] - margin or
                        tileset_y > camera_offset[1] + screen_height + margin)
            
            if is_culled:
                culled_count += 1
                # Debug: show why tilesets are culled
                if self.show_hitboxes and hasattr(self, '_last_render_log'):
                    if current_time - self._last_render_log < 0.1:
                        # Determine culling reason
                        reasons = []
                        if tileset_x + tileset_pixel_size < camera_offset[0] - margin:
                            reasons.append("LEFT")
                        if tileset_x > camera_offset[0] + screen_width + margin:
                            reasons.append("RIGHT")
                        if tileset_y + tileset_pixel_size < camera_offset[1] - margin:
                            reasons.append("TOP")
                        if tileset_y > camera_offset[1] + screen_height + margin:
                            reasons.append("BOTTOM")
                        print(f"  ✗ Culled '{tileset.name}' at world({tileset_x},{tileset_y}) - {'/'.join(reasons)}")
                continue
            
            rendered_count += 1
            
            # Render background image if available
            if tileset.background_image:
                screen_x = tileset_x - camera_offset[0]
                screen_y = tileset_y - camera_offset[1]
                screen.blit(tileset.background_image, (screen_x, screen_y))
                
                # Debug: Log rendering
                if self.show_hitboxes and hasattr(self, '_last_render_log'):
                    if current_time - self._last_render_log < 0.1:  # Only in same frame as main log
                        print(f"  ✓ Rendered '{tileset.name}' at screen({int(screen_x)},{int(screen_y)}) from world({tileset_x},{tileset_y})")
            else:
                # Debug: Log missing background
                if not hasattr(self, '_logged_missing_bg'):
                    self._logged_missing_bg = set()
                if tileset.name not in self._logged_missing_bg:
                    print(f"[RENDER WARNING] Tileset '{tileset.name}' has no background image at tiles({start_x_tiles},{start_y_tiles})")
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
                    # Debug: missing prop image
                    if not hasattr(self, '_logged_missing_props'):
                        self._logged_missing_props = set()
                    if prop.prop_type not in self._logged_missing_props:
                        print(f"[RENDER WARNING] Prop '{prop.prop_type}' has no image")
                        self._logged_missing_props.add(prop.prop_type)
                
                # Draw debug hitbox if enabled
                if hasattr(self, 'show_hitboxes') and self.show_hitboxes:
                    hitbox_rect = pygame.Rect(
                        prop_x - camera_offset[0],
                        prop_y - camera_offset[1],
                        prop_width,
                        prop_height
                    )
                    # Color code: Red for projectile-blocking, Green for normal collidable, Blue for non-collidable
                    if prop.blocks_projectile:
                        color = (255, 0, 0, 128)  # Red - blocks projectiles
                    elif prop.collidable:
                        color = (0, 255, 0, 128)  # Green - blocks movement only
                    else:
                        color = (0, 0, 255, 128)  # Blue - non-collidable
                    pygame.draw.rect(screen, color, hitbox_rect, 2)
        
        # Print render summary
        if self.show_hitboxes and hasattr(self, '_last_render_log'):
            if current_time - self._last_render_log < 0.1:  # Only in same frame as main log
                print(f"  Rendered: {rendered_count}/{len(self.placed_tilesets)} tilesets (culled: {culled_count})\n")
