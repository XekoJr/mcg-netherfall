import pygame
from assets import *
import math

class Enemy:
    """Base class for all enemies."""
    def __init__(self, x, y, hp, speed, xp_value, damage, size, images, tile_manager=None):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp  # Store the maximum HP for the health ratio
        self.speed = speed
        self.xp_value = xp_value  # XP value when the enemy dies
        self.damage =  damage
        self.size = size
        self.images = [pygame.transform.scale(img, self.size) for img in images]
        self.current_image_index = 0
        self.animation_counter = 0
        self.animation_speed = 10
        self.tile_manager = tile_manager

    def move_toward_player(self, player_x, player_y):
        """Move the enemy toward the player."""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Calculate new position
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Check collision with props if tile_manager available (with sliding)
        if self.tile_manager:
            # Try moving to new position
            new_rect = pygame.Rect(new_x, new_y, self.size[0], self.size[1])
            if not self.tile_manager.check_collision(new_rect, "enemy"):
                # No collision, apply full movement
                self.x = new_x
                self.y = new_y
            else:
                # Collision detected, try sliding along X axis only
                x_only_rect = pygame.Rect(new_x, self.y, self.size[0], self.size[1])
                if not self.tile_manager.check_collision(x_only_rect, "enemy"):
                    self.x = new_x
                else:
                    # Try sliding along Y axis only
                    y_only_rect = pygame.Rect(self.x, new_y, self.size[0], self.size[1])
                    if not self.tile_manager.check_collision(y_only_rect, "enemy"):
                        self.y = new_y
                    # else: fully blocked, don't move
        else:
            # No tile manager, just apply movement
            self.x = new_x
            self.y = new_y

    def take_damage(self, damage):
        """Reduce health and return True if the enemy dies."""
        self.hp -= damage
        return self.hp <= 0
    
    def is_dead(self):
        return self.hp <= 0

    def draw(self, screen, camera_x, camera_y, player):
        """Draw the enemy and its HP bar."""
        # Update animation frame
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_image_index = (self.current_image_index + 1) % len(self.images)

        # Determine if the enemy is to the right of the player
        flip_image = self.x > player.x

        # Flip the image if necessary
        image_to_draw = pygame.transform.flip(self.images[self.current_image_index], flip_image, False)

        # Draw the enemy sprite
        screen.blit(image_to_draw, (
            self.x - camera_x,
            self.y - camera_y
        ))

        # Draw the HP bar above the enemy
        health_ratio = max(0, self.hp / self.max_hp)  # Ensure ratio is never below 0
        pygame.draw.rect(screen, BLACK, (
            self.x - camera_x,
            self.y - camera_y - 10,  # Position above the enemy
            self.size[0], 5  # Match enemy width
        ))
        pygame.draw.rect(screen, GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED, (
            self.x - camera_x,
            self.y - camera_y - 10,
            self.size[0] * health_ratio, 5  # Scale width based on health ratio
        ))

    def get_rect(self):
        """Get the enemy's collision rectangle."""
        return pygame.Rect(self.x, self.y, self.size[0], self.size[1])
