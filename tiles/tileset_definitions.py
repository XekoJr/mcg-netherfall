from .tileset import Tileset
from .prop import Prop
from assets import TILESET_BACKGROUNDS, PROP_IMAGES

"""
Tilesets are 30x30 tiles (600x600 pixels @ 20px per tile)
Props use tile coords (0-29)
"""

# helper to make props easier
def create_prop(prop_type, x, y, width=1, height=1, collidable=True, blocks_projectiles=False):
    """Create a Prop with the corresponding image"""
    image = PROP_IMAGES.get(prop_type)
    if image is None:
        print(f"Missing image for prop '{prop_type}'")
    return Prop(prop_type, x, y, width, height, image, collidable, blocks_projectiles)

# Boss arena - pillars in corners
BOSS_ARENA_1 = Tileset(
    name="boss_arena_1",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-cross"),
    boss_spawn=True,
    spawn_point=(15, 15),  # center spawn
    props=[
        # pillars block projectiles
        create_prop("pillar-1", 2, 2, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 25, 2, 1, 3, blocks_projectiles=True),
        create_prop("pillar-3", 2, 26, 1, 3, blocks_projectiles=True),
        create_prop("pillar-1", 25, 26, 1, 3, blocks_projectiles=True),
        
        # Spawner at center (2x2, non-collidable)
        create_prop("big-spawnner", 14, 14, 2, 2, collidable=False),
    ]
)

# Forest area with rocks
FOREST_CLEARING = Tileset(
    name="forest_clearing",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-1"),
    props=[
        # big rocks in corners
        create_prop("big-rock-1", 3, 3, 2, 2),
        create_prop("big-rock-2", 24, 4, 2, 2),
        create_prop("big-rock-1", 4, 24, 2, 2),
        create_prop("big-rock-2", 24, 24, 2, 2),
        
        # some small ones on the sides
        create_prop("rock-1", 2, 12, 1, 1),
        create_prop("rock-2", 27, 15, 1, 1),
        create_prop("rock-3", 12, 2, 1, 1),
    ]
)

# graveyard with tombstones
GRAVEYARD = Tileset(
    name="graveyard",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-2"),
    props=[
        # Tall pillars
        create_prop("pillar-3", 4, 5, 1, 3, blocks_projectiles=True),
        create_prop("pillar-3", 22, 6, 1, 3, blocks_projectiles=True),
        
        # Coffins laying flat
        create_prop("coffin-v", 7, 20, 3, 1),
        create_prop("coffin-v", 20, 22, 3, 1),
        
        # Tombstones scattered around
        create_prop("stone-rip-1", 10, 8, 1, 1),
        create_prop("stone-rip-2", 25, 18, 1, 1),
        create_prop("stone-text", 5, 25, 1, 1),
    ]
)

# Village square - path goes horizontal so keep center clear
VILLAGE_SQUARE = Tileset(
    name="village_square",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-path-horizontal"),
    props=[
        # benches on the sides
        create_prop("pillar-1", 5, 6, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 22, 6, 1, 3, blocks_projectiles=True),
        create_prop("pillar-1", 5, 23, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 22, 23, 1, 3, blocks_projectiles=True),
        
        # barrels and boxes
        create_prop("barrel-1", 3, 3, 1, 1),
        create_prop("box-1", 26, 3, 1, 1),
        create_prop("box-2", 3, 26, 1, 1),
        create_prop("barrel-1", 26, 26, 1, 1),
    ]
)

# Temple ruins - vertical path so keep center X open
TEMPLE_RUINS = Tileset(
    name="temple_ruins",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-path-vertical"),
    props=[
        # statues at the top
        create_prop("statue", 6, 4, 1, 3, blocks_projectiles=True),
        create_prop("statue", 21, 4, 1, 3, blocks_projectiles=True),
        
        # pillars further down
        create_prop("pillar-1", 4, 18, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 23, 18, 1, 3, blocks_projectiles=True),
        
        # chests at bottom
        create_prop("chest-close", 4, 25, 1, 1),
        create_prop("chest-open", 25, 25, 1, 1),
    ]
)

# Garden with cross paths - gotta keep both center X and Y clear
GARDEN_PATH = Tileset(
    name="garden_path",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-cross"),
    props=[
        # benches in each corner
        create_prop("pillar-1", 6, 6, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 21, 6, 1, 3, blocks_projectiles=True),
        create_prop("pillar-1", 6, 23, 1, 3, blocks_projectiles=True),
        create_prop("pillar-2", 21, 23, 1, 3, blocks_projectiles=True),
        
        # vases for decoration
        create_prop("vase-1", 4, 4, 1, 1),
        create_prop("vase-2", 25, 4, 1, 1),
        create_prop("vase-1", 4, 25, 1, 1),
        create_prop("vase-2", 25, 25, 1, 1),
    ]
)

# Rocky terrain - not too crazy with the rocks
ROCKY_TERRAIN = Tileset(
    name="rocky_terrain",
    width=30,
    height=30,
    background_image=TILESET_BACKGROUNDS.get("bg-1"),
    props=[
        # bigger rocks spread out
        create_prop("big-rock-1", 4, 4, 2, 2),
        create_prop("big-rock-2", 24, 6, 2, 2),
        create_prop("big-rock-1", 8, 18, 2, 2),
        create_prop("big-rock-2", 22, 22, 2, 2),
        
        # couple small ones
        create_prop("rock-1", 2, 14, 1, 1),
        create_prop("rock-2", 27, 14, 1, 1),
    ]
)

# all the tilesets
TILESET_DEFINITIONS = [
    BOSS_ARENA_1,
    FOREST_CLEARING,
    GRAVEYARD,
    VILLAGE_SQUARE,
    TEMPLE_RUINS,
    GARDEN_PATH,
    ROCKY_TERRAIN,
]

# regular ones (no boss arena)
REGULAR_TILESETS = [
    FOREST_CLEARING,
    GRAVEYARD,
    VILLAGE_SQUARE,
    TEMPLE_RUINS,
    GARDEN_PATH,
    ROCKY_TERRAIN,
]
