import json
import pygame
from enemies import *
from abilities.__init__ import *
from assets import *
import random

class EnemyManager:
    """Manages all enemy-related logic."""
    def __init__(self):
        self.enemies = []

    def add_enemy(self, enemy):
        """Add a new enemy to the list."""
        self.enemies.append(enemy)

    def update_enemies(self, player_x, player_y, player, screen, camera_x, camera_y):
        """Update enemy positions and behaviors."""
        for enemy in self.enemies:
            if isinstance(enemy, Boss2Enemy):
                enemy.update(player_x, player_y, self, (0, 0, MAP_WIDTH, MAP_HEIGHT))
            else:
                enemy.move_toward_player(player_x, player_y)
                enemy.draw(screen, camera_x, camera_y, player)

    def draw_enemies(self, screen, camera_x, camera_y, player):
        """Draw all enemies."""
        for enemy in self.enemies:
            enemy.draw(screen, camera_x, camera_y, player)

    # Handle damage and collision logic
    def handle_projectile_collisions(self, projectiles, player, xp_drops, achievements, save_settings):
        """Check for collisions between projectiles and enemies."""
        for projectile in projectiles[:]:
            projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 10, 10)

            for enemy in self.enemies[:]:
                if projectile_rect.colliderect(enemy.get_rect()):
                    # Play the appropriate sound effect
                    if projectile['is_crit'] and crit_hit_sound:
                        crit_hit_sound.play()
                    elif normal_hit_sound:
                        normal_hit_sound.play()

                    # Apply burn or poison if abilities are active
                    for ability in player.abilities:
                        if isinstance(ability, BurningAbility) and ability.active:
                            ability.apply_burn(enemy)

                    for ability in player.abilities:
                        if isinstance(ability, PoisonAbility) and ability.active:
                            ability.apply_poison(enemy)

                    # Check if the enemy is dead
                    if enemy.take_damage(projectile['damage']):
                        # Pass `save_settings` to `handle_enemy_defeat`
                        self.handle_enemy_defeat(enemy, player, xp_drops, achievements, save_settings)
                    
                    # Remove the projectile after collision
                    projectiles.remove(projectile)
                    break

    def handle_player_collisions(self, player):
        """Check for collisions between the player and enemies."""
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        current_time = pygame.time.get_ticks()

        for enemy in self.enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                # Check if enough time has passed since the player was last damaged
                if current_time - player.last_damage_time >= player.invincibility_time * 1000:
                    
                    # Check for active ShieldAbility
                    for ability in player.abilities:
                        if isinstance(ability, ShieldAbility) and ability.block():
                            block_hit_sound.play()
                            return False  # Collision detected but damage was blocked

                    # Apply damage to the player
                    player.health -= enemy.damage
                    player.last_damage_time = current_time  # Update last damage time
                    hurt_sound.play()  # Play the hurt sound effect

                    if isinstance(enemy, BlobEnemy):
                        enemy.apply_poison(player)

                    # Check if the player's health has reached 0 or below
                    if player.health <= 0:
                        death_sound.play()
                        return True  # Player is dead

                return False  # Collision detected but no damage applied

        return False  # No collision

    def handle_enemy_defeat(self, enemy, player, xp_drops, achievements, save_settings):
        """Handle the logic when an enemy is defeated."""
        # Handle boss defeat logic
        if isinstance(enemy, Boss1Enemy):
            player.score += 100
            boss_death_sound.play()
            boss_music.stop()
            game_music.play(-1)

            # Mark the achievement for beating Pyraxis
            if not achievements.get("beat_Pyraxis", False):
                achievements["beat_Pyraxis"] = True
                print(f"[DEBUG] Updated achievements: {achievements}")

                # Save achievements via save_settings
                save_settings(achievements=achievements)

        elif isinstance(enemy, Boss2Enemy):
            player.score += 200
            boss_death_sound.play()
            boss_music.stop()
            game_music.play(-1)

            # Mark the achievement for beating Arcanos
            if not achievements.get("beat_Arcanos", False):
                achievements["beat_Arcanos"] = True
                print(f"[DEBUG] Updated achievements: {achievements}")

                # Save achievements via save_settings
                save_settings(achievements=achievements)

        # Handle other enemy-specific logic
        elif isinstance(enemy, BlobEnemy):
            player.score += 15
            blob_death_sound.play()
        elif isinstance(enemy, SkeletonEnemy):
            player.score += 10
            skeleton_death_sound.play()
        elif isinstance(enemy, BatEnemy):
            player.score += 5
            bat_death_sound.play()

        # Remove the enemy and drop XP
        self.enemies.remove(enemy)
        xp_drops.append({
            'x': enemy.x,
            'y': enemy.y,
            'value': enemy.xp_value
        })
