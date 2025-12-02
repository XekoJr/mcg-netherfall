import pygame
import sys
from assets import *
from projectile import *
from xp import draw_xp_drops, xp_drops
from enemies import *
from abilities import *
from ui import HUD, Minimap, draw_debug_hitboxes
from characters import Gigachad, Ranger

class GameManager:
    def __init__(self, screen, menu):
        self.screen = screen
        self.menu = menu
        self.hud = HUD()
        self.minimap = Minimap(size=150, position="top-right")
        self.clock = pygame.time.Clock()
        self.frame_count = 0

    def handle_events(self, player, enemy_manager, achievements):
        """Handle pygame events including user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.menu.pause_menu(achievements):
                        return True
                if event.key == pygame.K_F3:
                    self.hud.toggle_debug()
                if event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self._toggle_fullscreen()
        return False

    def _toggle_fullscreen(self):
        """Toggle between windowed and fullscreen."""
        settings = self.menu.settings
        is_fullscreen = settings.get("fullscreen", False)
        
        if is_fullscreen:
            # Switch to windowed
            resolution = settings.get("resolution", (1366, 768))
            self.screen = pygame.display.set_mode(resolution)
            settings["fullscreen"] = False
            settings["borderless"] = False
        else:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            settings["fullscreen"] = True
            settings["borderless"] = True
            settings["resolution"] = self.screen.get_size()
        
        # Update menu screen reference
        self.menu.screen = self.screen
        self.menu.menu_background = self.menu.load_menu_background()
        self.menu.save_settings()

    def update_player(self, player, camera_x, camera_y):
        """Update player movement and combat."""
        player.move()
        
        # Handle different attack types
        if isinstance(player, Gigachad):
            player.update_attack_animation()
        
        player.attack(camera_x, camera_y)

    def spawn_enemies(self, enemy_manager, player_level):
        """Handle enemy spawning logic"""
        self.frame_count += 1
        if self.frame_count >= enemy_manager.spawn_interval:
            enemy_manager.spawn_enemy(player_level)
            self.frame_count = 0

    def update_abilities(self, player, enemy):
        """Update all active player abilities for a given enemy"""
        for ability in player.abilities:
            if ability.active:
                if isinstance(ability, ShieldAbility):
                    ability.update() 
                elif isinstance(ability, BurningAbility):
                    ability.update_burn(enemy)
                elif isinstance(ability, HealingAbility):
                    ability.heal(player)
                elif isinstance(ability, InvincibilityAbility):
                    ability.apply_invincibility(player)
                elif isinstance(ability, PoisonAbility):
                    ability.update_poison(enemy)

    def handle_boss_projectiles(self, player, achievements, reset_game):
        """Handle boss projectiles movement and collision with player"""
        for projectile in boss_projectiles[:]:
            projectile['x'] += projectile['dx'] * projectile['speed']
            projectile['y'] += projectile['dy'] * projectile['speed']

            projectile_rect = pygame.Rect(
                projectile['x'], 
                projectile['y'], 
                boss_projectile_frames[0].get_width(),
                boss_projectile_frames[0].get_height()
            )
            player_rect = pygame.Rect(player.x, player.y, player.size, player.size)

            # Check for collision with the player by boss projectiles
            if player_rect.colliderect(projectile_rect):
                if self._handle_projectile_collision(player, projectile, achievements, reset_game):
                    return True  # Player died, exit game loop

            # Remove the projectile if it goes out of bounds
            if (projectile['x'] < 0 or projectile['x'] > MAP_WIDTH or
                    projectile['y'] < 0 or projectile['y'] > MAP_HEIGHT):
                if projectile in boss_projectiles:
                    boss_projectiles.remove(projectile)
        
        return False

    def _handle_projectile_collision(self, player, projectile, achievements, reset_game):
        """Handle a single projectile collision with the player"""
        # Check for active ShieldAbility
        for ability in player.abilities:
            if isinstance(ability, ShieldAbility) and ability.block():
                block_hit_sound.play()
                boss_projectiles.remove(projectile)  # Remove the projectile since it was blocked
                return False  # Continue game

        # Check for invincibility
        current_time = pygame.time.get_ticks()
        if current_time - player.last_damage_time < player.invincibility_time * 1000:
            boss_projectiles.remove(projectile)  # Remove without applying damage
            return False  # Continue game

        # Apply damage to the player
        player.health -= projectile['damage']
        player.last_damage_time = current_time
        hurt_sound.play()

        # Apply burn status to the player
        player.apply_status("burn", 3, 0.5, 5, "Boss")

        # Check if the player's health has reached 0 or below
        if player.health <= 0:
            death_sound.play()
            new_player, new_enemy_manager, achievements = reset_game(achievements=achievements)
            self.menu.game_over_screen(player.score, achievements)  # Fixed: only pass score and achievements
            return True  # Player died, exit game loop

        # Remove the projectile
        if projectile in boss_projectiles:
            boss_projectiles.remove(projectile)
        
        return False

    def check_player_death(self, player, reset_game, achievements):
        """Check if player has died and handle game over if so"""
        if player.health <= 0:
            death_sound.play()
            new_player, new_enemy_manager, achievements = reset_game(achievements=achievements)
            self.menu.game_over_screen(player.score, achievements)  # Fixed: only pass score and achievements
            return True
        return False

    def draw_game(self, screen, player, camera_x, camera_y, enemy_manager):
        """Draw all game elements."""
        # Background
        background_x = -camera_x
        background_y = -camera_y

        # Draw the background
        screen.blit(background_image, (background_x, background_y))

        # Game entities
        player.draw_with_offset(screen, camera_x, camera_y)
        draw_projectiles(screen, camera_x, camera_y)
        enemy_manager.draw_enemies(screen, camera_x, camera_y, player)
        draw_boss_projectiles(screen, camera_x, camera_y)
        draw_xp_drops(screen, player, camera_x, camera_y)

        # HUD
        self.hud.draw_all(screen, player)
        
        # Minimap (draw after HUD so it's on top)
        self.minimap.draw(screen, player, enemy_manager.enemies, xp_drops, boss_projectiles)
        
        # Debug hitboxes (toggle with F3)
        if self.hud.show_debug:
            draw_debug_hitboxes(screen, player, enemy_manager.enemies, 
                              projectiles, boss_projectiles, camera_x, camera_y)

    def handle_Gigachad_attacks(self, player, enemy_manager):
        """Handle AOE damage from Gigachad attacks."""
        if isinstance(player, Gigachad) and player.attacking:
            for enemy in enemy_manager.enemies[:]:
                if player.is_enemy_in_range(enemy):
                    if enemy.take_damage(player.attack_damage):
                        # Enemy died
                        enemy_manager.handle_enemy_defeat(
                            enemy, player, xp_drops, 
                            self.achievements, self.menu.save_settings
                        )

    def run_game_loop(self, player, enemy_manager, achievements):
        """Main game loop."""
        self.frame_count = 0
        self.achievements = achievements
        boss_projectiles.clear()

        # Music management
        main_menu_music.stop()
        game_music.play(-1)

        running = True

        while running:
            camera_x, camera_y = self.get_camera_offset(player)

            # Handle events (check for pause or exit)
            return_to_menu = self.handle_events(player, enemy_manager, achievements)
            if return_to_menu:
                # Clean up and return to main menu
                game_music.stop()
                boss_music.stop()
                main_menu_music.play(-1)
                return

            # Update player
            self.update_player(player, camera_x, camera_y)

            # Handle Gigachad AOE attacks
            if isinstance(player, Gigachad):
                self.handle_Gigachad_attacks(player, enemy_manager)

            # Spawn and update enemies
            self.spawn_enemies(enemy_manager, player.level)
            enemy_manager.update_enemies(player.x, player.y, player, self.screen, camera_x, camera_y)

            # Update projectiles
            move_projectiles()
            move_boss_projectiles()

            # Handle enemy interactions and abilities
            for enemy in enemy_manager.enemies:
                self.update_abilities(player, enemy)
                
                # Boss-specific behavior
                if isinstance(enemy, Boss1Enemy):
                    enemy.shoot_at_player(player)

            # Handle boss projectiles
            if self.handle_boss_projectiles(player, achievements, self.menu.reset_game):
                return  # Player died, exit game loop

            # Handle collisions
            enemy_manager.handle_projectile_collisions(projectiles, player, xp_drops, achievements, self.menu.save_settings)
            for enemy in enemy_manager.enemies[:]:
                if enemy.is_dead():
                    enemy_manager.handle_enemy_defeat(enemy, player, xp_drops, achievements, self.menu.save_settings)

            # Handle player collisions with enemies
            if enemy_manager.handle_player_collisions(player):
                if self.check_player_death(player, self.menu.reset_game, achievements):
                    return  # Player died, exit game loop

            # Handle status effects and check for death
            player.update_status_effects()
            if self.check_player_death(player, self.menu.reset_game, achievements):
                return  # Player died, exit game loop
                
            player.update_abilities_effects()

            # Draw the game
            self.draw_game(self.screen, player, camera_x, camera_y, enemy_manager)

            # Handle level up if pending
            if player.level_up_pending:
                self.menu.level_up_menu(player, self.screen)
                player.level_up_pending = False
                continue

            pygame.display.flip()
            self.clock.tick(60)

    def get_camera_offset(self, player):
        """Calculate camera offset based on player position"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        offset_x = max(0, min(player.x - screen_width // 2, MAP_WIDTH - screen_width))
        offset_y = max(0, min(player.y - screen_height // 2, MAP_HEIGHT - screen_height))

        return offset_x, offset_y