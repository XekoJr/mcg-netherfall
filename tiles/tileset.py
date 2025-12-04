class Tileset:
    def __init__(self, name, width, height, tile_grid=None, background_image=None, props=None, connections=None, boss_spawn=False, spawn_point=None):
        self.name = name
        self.width = width  # In tiles (e.g., 30)
        self.height = height
        self.tile_grid = tile_grid or []  # 2D array of tile types (can be empty if using background image)
        self.background_image = background_image  # Pre-rendered background image (300x300 pixels)
        self.props = props or []  # List of Prop objects to place on this tileset
        self.connections = connections or []  # List of (side, offset) tuples
        self.boss_spawn = boss_spawn  # Is this a boss spawn area?
        self.spawn_point = spawn_point  # (x, y) in tiles for boss spawn if boss_spawn=True
