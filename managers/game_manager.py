import pygame
import sys
from assets import *
from projectile import *
from xp import draw_xp_drops, xp_drops
from enemies import *
from abilities import *
from ui import HUD, Minimap, draw_debug_hitboxes
from characters import Gigachad, Ranger
from managers.powerup_manager import PowerupManager

class GameManager:
    # ===== CONFIGURATION SETTINGS =====
    # Set TESTING_MODE to switch between testing and production
    TESTING_MODE = False  # Change to True for testing
    
    # Performance settings
    TARGET_FPS = 60
    
    # Testing configuration (fast gameplay for debugging)
    if TESTING_MODE:
        ROUND_DURATION = 10  # 10 seconds per round
        WAVE_1_THRESHOLD = 0.45  # 45% of round (4.5 seconds)
        WAVE_2_THRESHOLD = 0.10  # 10% of round (1 second)
        BASE_SPAWN_INTERVAL = 60  # Faster spawning
        MIN_SPAWN_INTERVAL = 20
        XP_TO_LEVEL = 25  # Less XP needed
        XP_SCALING = 2.10  # 110% scaling
        SHOW_DEBUG_INFO = True
    else:
        # Production configuration (balanced gameplay)
        ROUND_DURATION = 600  # 10 minutes per round
        WAVE_1_THRESHOLD = 0.45  # 45% of round (4.5 minutes)
        WAVE_2_THRESHOLD = 0.10  # 10% of round (1 minute)
        BASE_SPAWN_INTERVAL = 140  # Normal spawning
        MIN_SPAWN_INTERVAL = 40
        XP_TO_LEVEL = 30  # Standard XP requirement
        XP_SCALING = 1.15  # 15% scaling
        SHOW_DEBUG_INFO = False
    
    # Time multiplier settings
    TIME_MULTIPLIER_RATE = 1.0 / 60  # +1x per minute
    
    # Endless mode scaling
    ENDLESS_HEALTH_SCALING = 0.3  # +30% per round after round 2
    ENDLESS_SPAWN_SCALING = 0.3  # +30% spawn rate per round
    ENDLESS_WAVE_SCALING = 0.5  # +50% wave size per round
    BOSS_HEALTH_SCALING = 0.5  # +50% boss health per round
    
    # Animation settings
    ANIMATION_FRAME_DELAY = 100  # Milliseconds between frames
    # ===== END CONFIGURATION =====

    def __init__(self, screen, menu):
        self.screen = screen
        self.menu = menu
        self.hud = HUD(screen, Fonts.score, menu.t)
        self.minimap = Minimap(screen, menu.t, size=150, position="top-right")
        
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        
        # Timer system - Uses config values
        self.round_duration = self.ROUND_DURATION
        self.round_start_time = 0
        self.current_round = 1
        self.boss_spawned = False
        self.wave_1_spawned = False
        self.wave_2_spawned = False
        
        # Difficulty scaling - Uses config values
        self.base_spawn_interval = self.BASE_SPAWN_INTERVAL
        self.current_spawn_interval = self.base_spawn_interval
        
        # Score tracking
        self.kills = 0
        self.time_multiplier = 1.0
        
        # Debug info
        self.show_debug_info = self.SHOW_DEBUG_INFO

        # Powerup manager
        self.powerup_manager = PowerupManager()

    def get_elapsed_time(self):
        """Get elapsed time in seconds since round start."""
        return (pygame.time.get_ticks() - self.round_start_time) / 1000

    def get_remaining_time(self):
        """Get remaining time in seconds until boss spawns."""
        elapsed = self.get_elapsed_time()
        return max(0, self.round_duration - elapsed)

    def format_time(self, seconds):
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def should_spawn_wave_1(self):
        """Check if first wave should spawn."""
        remaining = self.get_remaining_time()
        threshold = self.round_duration * self.WAVE_1_THRESHOLD
        return remaining <= threshold and not self.wave_1_spawned

    def should_spawn_wave_2(self):
        """Check if second wave should spawn."""
        remaining = self.get_remaining_time()
        threshold = self.round_duration * self.WAVE_2_THRESHOLD
        return remaining <= threshold and not self.wave_2_spawned

    def should_spawn_boss(self):
        """Check if boss should spawn (timer reached 0)."""
        remaining = self.get_remaining_time()
        return remaining <= 0 and not self.boss_spawned

    def update_spawn_rate(self):
        """Gradually increase spawn rate over time."""
        elapsed = self.get_elapsed_time()
        
        # Base spawn rate reduction
        progress = elapsed / self.round_duration
        interval_reduction = (self.base_spawn_interval - self.MIN_SPAWN_INTERVAL) * progress
        
        # Additional reduction for endless mode (round 3+)
        if self.current_round >= 3:
            endless_multiplier = 1 + (self.current_round - 2) * self.ENDLESS_SPAWN_SCALING
            interval_reduction *= endless_multiplier
        
        self.current_spawn_interval = int(self.base_spawn_interval - interval_reduction)
        self.current_spawn_interval = max(self.MIN_SPAWN_INTERVAL, self.current_spawn_interval)
        
        # Update time multiplier for score calculation
        total_game_time = (self.current_round - 1) * self.round_duration + elapsed
        self.time_multiplier = 1.0 + (total_game_time * self.TIME_MULTIPLIER_RATE)

    def calculate_score(self, base_score):
        """Calculate score with time multiplier."""
        return int(base_score * self.time_multiplier)

    def add_kill(self, base_points):
        """Add a kill to the counter and update score."""
        self.kills += 1
        score_gained = self.calculate_score(base_points)
        return score_gained

    def spawn_wave(self, enemy_manager, wave_number):
        """Spawn a wave of enemies."""
        wave_sizes = {
            1: 15,  # First wave spawns 15 enemies
            2: 25   # Second wave spawns 25 enemies
        }
        
        # Scale wave size for endless mode
        if self.current_round >= 3:
            base_size = wave_sizes.get(wave_number, 10)
            wave_sizes[wave_number] = int(base_size * (1 + (self.current_round - 2) * self.ENDLESS_WAVE_SCALING))
        
        num_enemies = wave_sizes.get(wave_number, 10)
        
        for _ in range(num_enemies):
            # Spawn mix of enemies based on current round
            if self.current_round == 1:
                enemy_types = [BatEnemy, SkeletonEnemy, BlobEnemy]
                weights = [3, 2, 1]  # More bats, fewer blobs
            elif self.current_round == 2:
                enemy_types = [BatEnemy, SkeletonEnemy, BlobEnemy]
                weights = [2, 3, 2]  # More balanced, tougher enemies
            else:  # Endless mode (round 3+)
                enemy_types = [BatEnemy, SkeletonEnemy, BlobEnemy]
                weights = [2, 2, 3]  # More blobs (harder enemies)
            
            enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
            
            # Spawn at random edge
            side = random.randint(0, 3)
            if side == 0:  # Top
                x, y = random.randint(0, MAP_WIDTH - 60), -60
            elif side == 1:  # Bottom
                x, y = random.randint(0, MAP_WIDTH - 60), MAP_HEIGHT
            elif side == 2:  # Left
                x, y = -60, random.randint(0, MAP_HEIGHT - 60)
            else:  # Right
                x, y = MAP_WIDTH, random.randint(0, MAP_HEIGHT - 60)
            
            enemy = enemy_type(x, y)
            
            # Scale health based on round
            health_multiplier = 1.0
            if self.current_round == 2:
                health_multiplier = 1.5
            elif self.current_round >= 3:
                health_multiplier = 1.5 + (self.current_round - 2) * self.ENDLESS_HEALTH_SCALING
            
            enemy.max_hp = int(enemy.max_hp * health_multiplier)
            enemy.hp = enemy.max_hp
            
            enemy_manager.add_enemy(enemy)

    def spawn_boss(self, enemy_manager):
        """Spawn the appropriate boss for the current round."""
        if self.current_round == 1:
            boss = Boss1Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        elif self.current_round == 2:
            boss = Boss2Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        else:
            # Endless mode: Alternate between bosses with scaling health
            if self.current_round % 2 == 1:
                boss = Boss1Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2)
            else:
                boss = Boss2Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2)
            
            # Scale boss health for endless mode
            health_multiplier = 1.0 + (self.current_round - 2) * self.BOSS_HEALTH_SCALING
            boss.max_hp = int(boss.max_hp * health_multiplier)
            boss.hp = boss.max_hp
        
        enemy_manager.add_enemy(boss)
        self.boss_spawned = True
        game_music.stop()
        boss_spawn_sound.play()
        boss_music.play(-1)

    def check_boss_defeated(self, enemy_manager):
        """Check if boss is defeated and advance to next round."""
        has_boss = any(isinstance(e, (Boss1Enemy, Boss2Enemy)) for e in enemy_manager.enemies)
        
        if self.boss_spawned and not has_boss:
            # Boss defeated! Start next round
            self.current_round += 1
            self.boss_spawned = False
            self.wave_1_spawned = False
            self.wave_2_spawned = False
            self.round_start_time = pygame.time.get_ticks()
            
            boss_music.stop()
            game_music.play(-1)
            
            return True
        return False

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
                    self._toggle_fullscreen()
        return False

    def _toggle_fullscreen(self):
        """Toggle between windowed and fullscreen."""
        settings = self.menu.settings
        is_fullscreen = settings.get("fullscreen", False)
        
        if is_fullscreen:
            resolution = settings.get("resolution", (1366, 768))
            self.screen = pygame.display.set_mode(resolution)
            settings["fullscreen"] = False
            settings["borderless"] = False
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            settings["fullscreen"] = True
            settings["borderless"] = True
            settings["resolution"] = self.screen.get_size()
        
        self.menu.screen = self.screen
        self.menu.menu_background = self.menu.load_menu_background()
        self.menu.save_settings()
        
        self.hud.screen = self.screen
        self.minimap.screen = self.screen

    def update_player(self, player, camera_x, camera_y):
        """Update player movement and combat."""
        player.move()
        
        if isinstance(player, Gigachad):
            player.update_attack_animation()
        
        player.attack(camera_x, camera_y)

    def spawn_enemies(self, enemy_manager):
        """Handle regular enemy spawning based on timer."""
        # Don't spawn if boss is active
        if self.boss_spawned:
            return
        
        self.frame_count += 1
        if self.frame_count >= self.current_spawn_interval:
            # Spawn regular enemy
            enemy_types = [BatEnemy, SkeletonEnemy, BlobEnemy]
            
            if self.current_round == 1:
                weights = [3, 2, 1]
            elif self.current_round == 2:
                weights = [2, 3, 2]
            else:  # Endless mode
                weights = [2, 2, 3]
            
            enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
            
            # Random edge spawn
            side = random.randint(0, 3)
            if side == 0:
                x, y = random.randint(0, MAP_WIDTH - 60), -60
            elif side == 1:
                x, y = random.randint(0, MAP_WIDTH - 60), MAP_HEIGHT
            elif side == 2:
                x, y = -60, random.randint(0, MAP_HEIGHT - 60)
            else:
                x, y = MAP_WIDTH, random.randint(0, MAP_HEIGHT - 60)
            
            enemy = enemy_type(x, y)
            
            # Scale health based on round
            health_multiplier = 1.0
            if self.current_round == 2:
                health_multiplier = 1.5
            elif self.current_round >= 3:
                health_multiplier = 1.5 + (self.current_round - 2) * self.ENDLESS_HEALTH_SCALING
            
            enemy.max_hp = int(enemy.max_hp * health_multiplier)
            enemy.hp = enemy.max_hp
            
            enemy_manager.add_enemy(enemy)
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

            if player_rect.colliderect(projectile_rect):
                if self._handle_projectile_collision(player, projectile, achievements, reset_game):
                    return True

            if (projectile['x'] < 0 or projectile['x'] > MAP_WIDTH or
                    projectile['y'] < 0 or projectile['y'] > MAP_HEIGHT):
                if projectile in boss_projectiles:
                    boss_projectiles.remove(projectile)
        
        return False

    def _handle_projectile_collision(self, player, projectile, achievements, reset_game):
        """Handle a single projectile collision with the player"""
        for ability in player.abilities:
            if isinstance(ability, ShieldAbility) and ability.block():
                block_hit_sound.play()
                boss_projectiles.remove(projectile)
                return False

        current_time = pygame.time.get_ticks()
        if current_time - player.last_damage_time < player.invincibility_time * 1000:
            boss_projectiles.remove(projectile)
            return False

        player.health -= projectile['damage']
        player.last_damage_time = current_time
        hurt_sound.play()

        player.apply_status("burn", 3, 0.5, 5, "Boss")

        if player.health <= 0:
            death_sound.play()
            new_player, new_enemy_manager, achievements = reset_game(achievements=achievements)
            self.menu.game_over_screen(player.score, achievements)
            return True

        if projectile in boss_projectiles:
            boss_projectiles.remove(projectile)
        
        return False

    def check_player_death(self, player, reset_game, achievements):
        """Check if player has died and handle game over if so"""
        if player.health <= 0:
            death_sound.play()
            new_player, new_enemy_manager, achievements = reset_game(achievements=achievements)
            self.menu.game_over_screen(player.score, achievements)
            return True
        return False

    def draw_game(self, screen, player, camera_x, camera_y, enemy_manager):
        """Draw all game elements."""
        background_x = -camera_x
        background_y = -camera_y

        screen.blit(background_image, (background_x, background_y))

        player.draw_with_offset(screen, camera_x, camera_y)
        draw_projectiles(screen, camera_x, camera_y)
        enemy_manager.draw_enemies(screen, camera_x, camera_y, player)
        draw_boss_projectiles(screen, camera_x, camera_y)
        draw_xp_drops(screen, player, camera_x, camera_y)
        
        # Draw powerup drops and effects
        self.powerup_manager.draw_drops(screen, camera_x, camera_y)
        self.powerup_manager.draw_effects(screen, camera_x, camera_y, player)

        # Draw HUD elements (health, XP, abilities)
        self.hud.draw_all(screen, player)
        
        # Draw timer and score at top-left
        self.draw_timer_and_score(screen)
        
        # Draw active powerup UI
        self.powerup_manager.draw_active_powerups_ui(screen)
        
        self.minimap.draw(screen, player, enemy_manager.enemies, xp_drops, boss_projectiles)
        
        if self.hud.show_debug:
            draw_debug_hitboxes(screen, player, enemy_manager.enemies, 
                              projectiles, boss_projectiles, camera_x, camera_y)

    def draw_timer_and_score(self, screen):
        """Draw the countdown timer and score at top-left."""
        remaining = self.get_remaining_time()
        time_str = self.format_time(remaining)
        
        # Choose color based on time remaining
        if remaining <= self.round_duration * self.WAVE_2_THRESHOLD:
            color = RED
        elif remaining <= self.round_duration * self.WAVE_1_THRESHOLD:
            color = YELLOW
        else:
            color = WHITE
        
        font = Fonts.score
        
        # Timer text
        mode_indicator = " [TESTING]" if self.TESTING_MODE else ""
        timer_text = font.render(f"Round {self.current_round} - {time_str}{mode_indicator}", True, color)
        screen.blit(timer_text, (20, 20))
        
        # Score text (kills with multiplier)
        multiplier_text = f" x{self.time_multiplier:.1f}" if self.time_multiplier > 1.0 else ""
        score_text = font.render(f"Kills: {self.kills}{multiplier_text}", True, WHITE)
        screen.blit(score_text, (20, 50))
        
        # Debug info (only in testing mode)
        if self.show_debug_info:
            fps = int(self.clock.get_fps())
            spawn_interval = self.current_spawn_interval
            debug_text = font.render(f"FPS: {fps} | Spawn: {spawn_interval}", True, YELLOW)
            screen.blit(debug_text, (20, 80))

    def handle_Gigachad_attacks(self, player, enemy_manager):
        """Handle AOE damage from Gigachad attacks."""
        if isinstance(player, Gigachad) and player.attacking:
            for enemy in enemy_manager.enemies[:]:
                if player.is_enemy_in_range(enemy):
                    if enemy.take_damage(player.attack_damage):
                        score_gained = self.handle_enemy_defeat_score(enemy)
                        player.score += score_gained
                        enemy_manager.handle_enemy_defeat(
                            enemy, player, xp_drops, 
                            self.achievements, self.menu.save_settings
                        )

    def handle_enemy_defeat_score(self, enemy):
        """Calculate score for defeating an enemy and try to drop powerup."""
        if isinstance(enemy, Boss1Enemy):
            base_score = 100
        elif isinstance(enemy, Boss2Enemy):
            base_score = 200
        elif isinstance(enemy, BlobEnemy):
            base_score = 15
        elif isinstance(enemy, SkeletonEnemy):
            base_score = 10
        elif isinstance(enemy, BatEnemy):
            base_score = 5
        else:
            base_score = 5
        
        # Try to drop powerup at enemy position
        purchased_powerups = {
            k: v['purchased'] 
            for k, v in self.menu.settings.get('powerups', {}).items()
        }
        self.powerup_manager.try_drop_powerup(enemy.x, enemy.y, purchased_powerups)
        
        return self.add_kill(base_score)

    def run_game_loop(self, player, enemy_manager, achievements):
        """Main game loop."""
        self.frame_count = 0
        self.achievements = achievements
        boss_projectiles.clear()
        
        # Initialize timer and scoring
        self.round_start_time = pygame.time.get_ticks()
        self.current_round = 1
        self.boss_spawned = False
        self.wave_1_spawned = False
        self.wave_2_spawned = False
        self.kills = 0
        self.time_multiplier = 1.0
        
        # Clear powerups
        self.powerup_manager.powerup_drops.clear()
        self.powerup_manager.active_powerups.clear()

        main_menu_music.stop()
        game_music.play(-1)

        running = True

        while running:
            self.clock.tick(self.TARGET_FPS)
            
            camera_x, camera_y = self.get_camera_offset(player)

            return_to_menu = self.handle_events(player, enemy_manager, achievements)
            if return_to_menu:
                game_music.stop()
                boss_music.stop()
                main_menu_music.play(-1)
                return

            self.update_player(player, camera_x, camera_y)

            if isinstance(player, Gigachad):
                self.handle_Gigachad_attacks(player, enemy_manager)

            # Update spawn rate and time multiplier
            self.update_spawn_rate()

            # Check for wave spawns
            if self.should_spawn_wave_1():
                self.spawn_wave(enemy_manager, 1)
                self.wave_1_spawned = True
            
            if self.should_spawn_wave_2():
                self.spawn_wave(enemy_manager, 2)
                self.wave_2_spawned = True
            
            # Check for boss spawn
            if self.should_spawn_boss():
                self.spawn_boss(enemy_manager)

            # Regular enemy spawning
            self.spawn_enemies(enemy_manager)
            
            enemy_manager.update_enemies(player.x, player.y, player, self.screen, camera_x, camera_y)

            move_projectiles()
            move_boss_projectiles()

            for enemy in enemy_manager.enemies:
                self.update_abilities(player, enemy)
                
                if isinstance(enemy, Boss1Enemy):
                    enemy.shoot_at_player(player)

            if self.handle_boss_projectiles(player, achievements, self.menu.reset_game):
                return

            # Update powerups
            self.powerup_manager.update(player, enemy_manager.enemies, xp_drops)

            enemy_manager.handle_projectile_collisions(projectiles, player, xp_drops, achievements, self.menu.save_settings)
            for enemy in enemy_manager.enemies[:]:
                if enemy.is_dead():
                    score_gained = self.handle_enemy_defeat_score(enemy)
                    player.score += score_gained
                    enemy_manager.handle_enemy_defeat(enemy, player, xp_drops, achievements, self.menu.save_settings)

            # Check if boss was defeated
            if self.check_boss_defeated(enemy_manager):
                # Boss defeated - round advanced
                pass

            if enemy_manager.handle_player_collisions(player):
                if self.check_player_death(player, self.menu.reset_game, achievements):
                    return

            player.update_status_effects()
            if self.check_player_death(player, self.menu.reset_game, achievements):
                return
                
            player.update_abilities_effects()

            self.draw_game(self.screen, player, camera_x, camera_y, enemy_manager)

            if player.level_up_pending:
                self.menu.level_up_menu(player, self.screen)
                player.level_up_pending = False
                continue

            pygame.display.flip()

    def get_camera_offset(self, player):
        """Calculate camera offset based on player position"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        offset_x = max(0, min(player.x - screen_width // 2, MAP_WIDTH - screen_width))
        offset_y = max(0, min(player.y - screen_height // 2, MAP_HEIGHT - screen_height))

        return offset_x, offset_y