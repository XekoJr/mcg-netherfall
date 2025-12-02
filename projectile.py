import random
import pygame
import math
from assets import *

# Projectile constants
PROJECTILE_SPEED = 7

pygame.mixer.init()

# List to store active projectiles
projectiles = []
boss_projectiles = []

# Load projectile animations
try:
    normal_projectile_frames = [
        pygame.image.load(f'./assets/images/projectile/normal/{i}.png') for i in range(6)  # Adjust number of frames
    ]
    crit_projectile_frames = [
        pygame.image.load(f'./assets/images/projectile/crit/{i}.png') for i in range(6)  # Adjust number of frames
    ]
    boss_projectile_frames = [
        pygame.image.load(f'./assets/images/projectile/boss/{i}.png') for i in range(11)  # Boss projectile frames
    ]

    # Optionally resize frames if needed
    normal_projectile_frames = [pygame.transform.scale(frame, (60, 25)) for frame in normal_projectile_frames]
    crit_projectile_frames = [pygame.transform.scale(frame, (60, 25)) for frame in crit_projectile_frames]
    boss_projectile_frames = [pygame.transform.scale(frame, (60, 25)) for frame in boss_projectile_frames]
except pygame.error as e:
    print(f"Error loading projectile frames: {e}")
    normal_projectile_frames, crit_projectile_frames, boss_projectile_frames = [], [], []

def fire_projectile(player, camera_x, camera_y):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x + camera_x - (player.x + player.size / 2)
    dy = mouse_y + camera_y - (player.y + player.size / 2)
    distance = math.sqrt(dx ** 2 + dy ** 2)
    if distance != 0:
        dx /= distance
        dy /= distance

    # Calculate the angle of rotation in degrees
    angle = math.degrees(math.atan2(-dy, dx))  # Negative dy because Pygame's y-axis is flipped

    is_crit = random.random() < (player.crit_chance / 100)
    damage = player.projectile_damage * player.crit_damage if is_crit else player.projectile_damage

    projectiles.append({
        'x': player.x + player.size / 2,
        'y': player.y + player.size / 2,
        'dx': dx,
        'dy': dy,
        'damage': damage,
        'is_crit': is_crit,
        'frames': crit_projectile_frames if is_crit else normal_projectile_frames,
        'frame_index': 0,  # Start at the first frame
        'last_frame_time': pygame.time.get_ticks(),  # Time to control animation speed
        'angle': angle  # Store the angle for rotation
    })

def move_projectiles():
    """Update the position of all projectiles."""
    for projectile in projectiles[:]:
        projectile['x'] += projectile['dx'] * PROJECTILE_SPEED
        projectile['y'] += projectile['dy'] * PROJECTILE_SPEED  # Move y

        # Remove projectiles that go out of map boundaries
        if (projectile['x'] < 0 or projectile['x'] > MAP_WIDTH or
                projectile['y'] < 0 or projectile['y'] > MAP_HEIGHT):
            projectiles.remove(projectile)

def draw_projectiles(screen, camera_x, camera_y):
    """Draw all projectiles with animation and rotation."""
    current_time = pygame.time.get_ticks()
    for projectile in projectiles:
        frames = projectile['frames']
        frame_index = projectile['frame_index']

        # Get the current frame
        if frames:
            frame = frames[frame_index]

            # Rotate the frame based on the angle
            rotated_frame = pygame.transform.rotate(frame, projectile['angle'])

            # Get the rect of the rotated image for proper centering
            frame_rect = rotated_frame.get_rect(center=(
                projectile['x'] - camera_x,
                projectile['y'] - camera_y
            ))

            # Draw the rotated frame
            screen.blit(rotated_frame, frame_rect.topleft)
        else:
            # Fallback if frames are missing
            pygame.draw.rect(screen, YELLOW if not projectile['is_crit'] else RED, (
                projectile['x'] - camera_x,
                projectile['y'] - camera_y,
                10, 10
            ))

        # Update animation frame
        if current_time - projectile['last_frame_time'] > 100:  # 100ms per frame
            projectile['frame_index'] = (frame_index + 1) % len(frames)
            projectile['last_frame_time'] = current_time

# Boss projectile functions

def move_boss_projectiles():
    """Move all boss projectiles."""
    for projectile in boss_projectiles[:]:
        projectile['x'] += projectile['dx'] * projectile['speed']
        projectile['y'] += projectile['dy'] * projectile['speed']

        # Remove projectiles that go out of bounds
        if (projectile['x'] < 0 or projectile['x'] > MAP_WIDTH or
                projectile['y'] < 0 or projectile['y'] > MAP_HEIGHT):
            boss_projectiles.remove(projectile)

def draw_boss_projectiles(screen, camera_x, camera_y):
    """Draw boss projectiles with animation."""
    current_time = pygame.time.get_ticks()
    for projectile in boss_projectiles:
        frames = projectile['frames']
        frame_index = projectile['frame_index']
        frame = frames[frame_index]

        # Rotate the frame based on angle
        rotated_frame = pygame.transform.rotate(frame, projectile['angle'])
        frame_rect = rotated_frame.get_rect(center=(
            projectile['x'] - camera_x,
            projectile['y'] - camera_y
        ))

        # Draw the projectile
        screen.blit(rotated_frame, frame_rect.topleft)

        # Update animation frame
        if current_time - projectile['last_frame_time'] > 100:  # Adjust frame time as needed
            projectile['frame_index'] = (frame_index + 1) % len(frames)
            projectile['last_frame_time'] = current_time
