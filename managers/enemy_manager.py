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
        self.spawn_timer = 0
        self.base_spawn_interval = 140  # Base spawn interval (frames)
        self.spawn_interval = self.base_spawn_interval
        self.boss_spawned = False
        self.level_enemy_map = {
            1: {"enemies": [(BatEnemy, 1)]},  # Only bats
            2: {"enemies": [(BatEnemy, 3), (SkeletonEnemy, 1)]},  # Bats are more common
            3: {"enemies": [(BatEnemy, 2), (SkeletonEnemy, 2), (BlobEnemy, 1)]},  # More variety
            4: {"enemies": [(BatEnemy, 3), (SkeletonEnemy, 3), (BlobEnemy, 2)]},  
            5: {"enemies": [(BatEnemy, 2), (SkeletonEnemy, 1)]},  # Eazy Boss
            6: {"enemies": [(BatEnemy, 1), (SkeletonEnemy, 2), (BlobEnemy, 1)]},  # Medium
            7: {"enemies": [(BatEnemy, 1), (SkeletonEnemy, 3)]}, # More skeletons
            8: {"enemies": [(BatEnemy, 2), (SkeletonEnemy, 3), (BlobEnemy, 2)]},
            9: {"enemies": [(BatEnemy, 3), (SkeletonEnemy, 3), (BlobEnemy, 3)]},
            10: {"enemies": [(BatEnemy, 1), (SkeletonEnemy, 3), (BlobEnemy, 1)]}, # Medium Boss
            11: {"enemies": [(BatEnemy, 2), (SkeletonEnemy, 3), (BlobEnemy, 2)]},
            12: {"enemies": [(SkeletonEnemy, 1), (BlobEnemy, 3)]}, # More blobs
            13: {"enemies": [(BlobEnemy, 3)]}, # Only blobs
            14: {"enemies": [(BatEnemy, 3), (SkeletonEnemy, 3), (BlobEnemy, 3)]},
            15: {"enemies": [(BatEnemy, 1), (SkeletonEnemy, 2), (BlobEnemy, 3)]}, # Hard Boss
            16: {"enemies": [(BatEnemy, 2), (SkeletonEnemy, 3), (BlobEnemy, 3)]},
        }

    def update_spawn_interval(self, player_level):
        """Update the spawn interval based on the player's level."""
        self.spawn_interval = max(30, self.base_spawn_interval - (player_level * 5))

    def add_enemy(self, enemy):
        """Add a new enemy to the list."""
        self.enemies.append(enemy)

    def spawn_enemy(self, player_level):
        """Spawn a new enemy or boss based on the player's level."""
        if player_level not in self.level_enemy_map:
            player_level = max(self.level_enemy_map.keys())  # Cap at highest level configuration

        # Ensure Boss1Enemy spawns at level 5
        if player_level == 5:
            if not any(isinstance(enemy, Boss1Enemy) for enemy in self.enemies):
                if not self.boss_spawned:
                # Spawn the boss in the center of the map
                    self.enemies.append(Boss1Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2))
                    self.boss_spawned = True
                    game_music.stop()
                    boss_spawn_sound.play()
                    boss_music.play(-1)

        # Ensure Boss2Enemy spawns at level 10
        if player_level == 10:
            if not any(isinstance(enemy, Boss2Enemy) for enemy in self.enemies):
                if not self.boss_spawned:
                    self.enemies.append(Boss2Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2))
                    self.boss_spawned = True
                    game_music.stop()
                    boss_spawn_sound.play()
                    boss_music.play(-1)

        if player_level in [5, 10]:
            self.spawn_interval = 170  # Set a defined spawn interval for boss levels
        elif player_level == 6:
            self.spawn_interval = 105  # Set a defined spawn interval for level 6
            self.boss_spawned = False
        elif player_level == 11:
            self.spawn_interval = 70
            self.boss_spawned = False
        elif player_level == 16:
            self.spawn_interval = 35
        else:
            self.update_spawn_interval(player_level)  # Update spawn interval based on level

        level_config = self.level_enemy_map[player_level]
        enemy_types = level_config["enemies"]

        # Weighted random choice based on spawn weights
        enemy_type = random.choices(
            [etype for etype, _ in enemy_types], 
            weights=[weight for _, weight in enemy_types],
            k=1
        )[0]
        
        # Apply health scaling based on player level
        health_multiplier = 1.0
        if player_level >= 16:
            health_multiplier = 1.6  # 60% extra health
        elif player_level >= 11:
            health_multiplier = 1.4  # 40% extra health
        elif player_level >= 6:
            health_multiplier = 1.2  # 20% extra health

        # Instantiate enemy and scale its health
        enemy_instance = enemy_type(x=0, y=0)  # Temporarily initialize
        enemy_instance.max_hp = int(enemy_instance.max_hp * health_multiplier)
        enemy_instance.hp = enemy_instance.max_hp  # Reset current HP to max HP

        # Randomly choose a side for spawning
        side = random.randint(0, 3)
        if side == 0:  # Top edge
            x, y = random.randint(0, MAP_WIDTH - enemy_instance.size[0]), -enemy_instance.size[1]
        elif side == 1:  # Bottom edge
            x, y = random.randint(0, MAP_WIDTH - enemy_instance.size[0]), MAP_HEIGHT
        elif side == 2:  # Left edge
            x, y = -enemy_instance.size[0], random.randint(0, MAP_HEIGHT - enemy_instance.size[1])
        else:  # Right edge
            x, y = MAP_WIDTH, random.randint(0, MAP_HEIGHT - enemy_instance.size[1])

        # Update the enemy's position
        enemy_instance.x = x
        enemy_instance.y = y

        # Spawn the chosen enemy
        self.enemies.append(enemy_instance)

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
