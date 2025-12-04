from .tileset import Tileset
from .prop import Prop
from assets import TILESET_BACKGROUNDS, PROP_IMAGES

"""
Tileset Definitions for MCG Netherfall

Each tileset is 30x30 tiles = 600x600 pixels (at 20 pixels per tile)
Background images are automatically scaled to 600x600 if needed
Props are placed at tile coordinates (0-29) within each tileset

Prop Sizes:
- 1x1: Small items (bushes, rocks, barrels, vases, tombstones) - 20x20 pixels
- 2x2: Large items (big rocks, well, spawner) - 40x40 pixels
- 1x3: Vertical tall items (pillars, statues, vertical benches, vertical coffins) - 20x60 pixels (blocks projectiles)
- 3x1: Horizontal wide items (horizontal coffins) - 60x20 pixels
"""

# Helper function to create props easily
def create_prop(prop_type, x, y, width=1, height=1, collidable=True, blocks_projectiles=False):
    """Create a Prop with the corresponding image"""
    image = PROP_IMAGES.get(prop_type)
    if image is None:
        print(f"  WARNING: Missing image for prop '{prop_type}'")
    return Prop(prop_type, x, y, width, height, image, collidable, blocks_projectiles)

# Boss Arena (30x30) - Stone arena with pillars and spawner
BOSS_ARENA_1 = Tileset(
    name="boss_arena_1",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-cross"),
    boss_spawn=True,
    spawn_point=(15, 15),  # Center of 30x30 grid
    props=[
        # Corner pillars (1x3 tiles each = 20x60 pixels) - block projectiles
        create_prop("pillar-1", 2, 2, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 25, 2, 1, 3, blocks_projectiles=True),
        create_prop("pillar-3", 2, 26, 1, 3, blocks_projectiles=True),
        create_prop("pillar-1", 25, 26, 1, 3, blocks_projectiles=True),
        
        # Spawner at center (2x2, non-collidable)
        create_prop("big-spawnner", 14, 14, 2, 2, collidable=False),
    ]
)

# Forest Clearing (30x30) - Trees, bushes, rocks
FOREST_CLEARING = Tileset(
    name="forest_clearing",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-1"),
    props=[
        # Big rocks scattered (2x2) - corners only
        create_prop("big-rock-1", 3, 3, 2, 2),
        create_prop("big-rock-2", 24, 4, 2, 2),
        create_prop("big-rock-1", 4, 24, 2, 2),
        create_prop("big-rock-2", 24, 24, 2, 2),
        
        # Small rocks (1x1) - edges
        create_prop("rock-1", 2, 12, 1, 1),
        create_prop("rock-2", 27, 15, 1, 1),
        create_prop("rock-3", 12, 2, 1, 1),
    ]
)

# Graveyard (30x30) - Coffins, tombstones, stone rips
GRAVEYARD = Tileset(
    name="graveyard",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-2"),
    props=[
        # Coffins standing upright (1x3) - tall thin (vertical orientation)
        create_prop("coffin-h", 4, 5, 1, 3),
        create_prop("coffin-h", 22, 6, 1, 3),
        
        # Coffins lying down (3x1) - wide thin (horizontal orientation)
        create_prop("coffin-v", 7, 20, 3, 1),
        create_prop("coffin-v", 20, 22, 3, 1),
        
        # Tombstones (1x1) - sparse
        create_prop("stone-rip-1", 10, 8, 1, 1),
        create_prop("stone-rip-2", 25, 18, 1, 1),
        create_prop("stone-text", 5, 25, 1, 1),
    ]
)

# Village Square (30x30) - Benches, barrels, boxes, well (horizontal path - avoid center Y)
VILLAGE_SQUARE = Tileset(
    name="village_square",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-path-horizontal"),
    props=[
        # Benches vertical (1x3) - block projectiles, avoid horizontal center
        create_prop("bench-v-1", 5, 6, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-2", 22, 6, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-1", 5, 23, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-2", 22, 23, 1, 3, blocks_projectiles=True),
        
        # Barrels at corners (1x1)
        create_prop("barrel-1", 3, 3, 1, 1),
        create_prop("box-1", 26, 3, 1, 1),
        create_prop("box-2", 3, 26, 1, 1),
        create_prop("barrel-1", 26, 26, 1, 1),
    ]
)

# Temple Ruins (30x30) - Pillars, statues, chests (vertical path - avoid center X)
TEMPLE_RUINS = Tileset(
    name="temple_ruins",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-path-vertical"),
    props=[
        # Statues (1x3) - block projectiles, avoid vertical center
        create_prop("statue", 6, 4, 1, 3, blocks_projectiles=True),
        create_prop("statue", 21, 4, 1, 3, blocks_projectiles=True),
        
        # Pillars (1x3) - block projectiles, spread out
        create_prop("pillar-1", 4, 18, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 23, 18, 1, 3, blocks_projectiles=True),
        
        # Chests at edges (1x1)
        create_prop("chest-close", 4, 25, 1, 1),
        create_prop("chest-open", 25, 25, 1, 1),
    ]
)

# Garden Path (30x30) - Bushes, vases, benches (cross paths - avoid center X and Y)
GARDEN_PATH = Tileset(
    name="garden_path",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-cross"),
    props=[
        # Benches in corners (1x3) - block projectiles, away from paths
        create_prop("bench-v-1", 6, 6, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-2", 21, 6, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-1", 6, 23, 1, 3, blocks_projectiles=True),
        create_prop("bench-v-2", 21, 23, 1, 3, blocks_projectiles=True),
        
        # Vases near corners (1x1)
        create_prop("vase-1", 4, 4, 1, 1),
        create_prop("vase-2", 25, 4, 1, 1),
        create_prop("vase-1", 4, 25, 1, 1),
        create_prop("vase-2", 25, 25, 1, 1),
    ]
)

# Rocky Terrain (30x30) - Rocks and big rocks (less cluttered)
ROCKY_TERRAIN = Tileset(
    name="rocky_terrain",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-1"),
    props=[
        # Big rocks (2x2) - strategic placement
        create_prop("big-rock-1", 4, 4, 2, 2),
        create_prop("big-rock-2", 24, 6, 2, 2),
        create_prop("big-rock-1", 8, 18, 2, 2),
        create_prop("big-rock-2", 22, 22, 2, 2),
        
        # Small rocks (1x1) - minimal
        create_prop("rock-1", 2, 14, 1, 1),
        create_prop("rock-2", 27, 14, 1, 1),
    ]
)

# List of all tilesets for easy access
TILESET_DEFINITIONS = [
    BOSS_ARENA_1,
    FOREST_CLEARING,
    GRAVEYARD,
    VILLAGE_SQUARE,
    TEMPLE_RUINS,
    GARDEN_PATH,
    ROCKY_TERRAIN,
]

# Regular tilesets (excluding boss arena)
REGULAR_TILESETS = [
    FOREST_CLEARING,
    GRAVEYARD,
    VILLAGE_SQUARE,
    TEMPLE_RUINS,
    GARDEN_PATH,
    ROCKY_TERRAIN,
]
