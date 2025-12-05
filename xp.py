import pygame
from assets import *

# XP properties
xp_width = 10
xp_height = 14
xp_drops = []  # List to store XP drops
player_xp = 0

# Load the XP image
try:
    xp_image = pygame.image.load('assets/images/xp/xp-drop.png')
    xp_image = pygame.transform.scale(xp_image, (xp_width, xp_height))  # Scale the image to the desired dimensions
except pygame.error as e:
    print(f"Error loading XP image: {e}")
    xp_image = None  # Fallback to None if loading fails

def draw_xp_drops(screen, player, camera_x, camera_y):
    """Draw and handle XP drops."""
    player_rect = pygame.Rect(player.x, player.y, player.size, player.size)

    for xp in xp_drops[:]:
        xp_rect = pygame.Rect(xp['x'], xp['y'], xp_width, xp_height)

        # Draw XP as an image relative to the camera
        if xp_image:
            screen.blit(xp_image, (xp['x'] - camera_x, xp['y'] - camera_y))
        else:
            # Fallback to a rectangle if the image fails to load
            pygame.draw.rect(screen, GREEN, (
                xp['x'] - camera_x,
                xp['y'] - camera_y,
                xp_width,
                xp_height
            ))

        # Check collision with player
        if player_rect.colliderect(xp_rect):
            player.gain_xp(xp['value'])  # Add XP based on the value of the drop
            xp_drops.remove(xp)
            if collect_xp_sound:
                collect_xp_sound.play()  # Play the XP collection sound
