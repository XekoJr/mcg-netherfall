import json
import os
import pygame
import sys
import random
from assets import *
from ui.ui_elements import Button

class Menu:
    """Handles all menu screens."""
    
    def __init__(self, screen, font_title=None, font_button=None, font_credit=None, font_score=None):
        self.screen = screen
        self.settings_file = "./utils.json"
        self.settings = self.load_settings()
        self.menu_background = self.load_menu_background()
        self.high_score = self.settings.get("high_score", 0)
        self.resolutions = [(1366, 768), (1280, 720), (1024, 576)]
        
        # Fonts
        self.font_title = font_title
        self.font_button = font_button 
        self.font_credit = font_credit
        self.font_score = font_score
        
        # Game state callbacks (set by main)
        self.reset_game = None
        self.game_loop = None

    def load_menu_background(self):
        """Load and scale menu background."""
        try:
            bg = pygame.image.load("./assets/images/background/gameart-cover.jpg")
            return pygame.transform.scale(bg, (self.screen.get_width(), self.screen.get_height()))
        except pygame.error as e:
            print(f"Error loading menu background: {e}")
            return None

    def load_settings(self):
        """Load settings from file."""
        default_settings = {
            "master_volume": 100,
            "music_volume": 100,
            "effects_volume": 100,
            "resolution": (1280, 720),
            "high_score": 0,
            "skill_points": 0,
            "skills": {
                "max_health": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [1, 2, 3, 6, 8, 10],
                    "effect": "+20 HP per level"
                },
                "speed": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [1, 2, 3, 6, 7, 8],
                    "effect": "+5% Speed per level"
                },
                "heal": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [5, 6, 7, 8, 9],
                    "effect": "+2 HP/sec per level",
                    "requires": 
                        [
                            ["max_health", 3],
                            ["speed", 3]
                        ]
                },
                "damage": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [2, 3, 4, 5, 6, 7],
                    "effect": "+10% Damage per level",
                    "requires": [["heal", 2]]
                },
                "fire_rate": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [3, 4, 5, 6, 7, 8],
                    "effect": "+10% Fire Rate per level",
                    "requires": [["damage", 1]]
                },
                "crit_damage": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [4, 5, 6, 7, 8, 9],
                    "effect": "+30% Crit damage per level",
                    "requires": [["heal", 2]]
                },
                "crit_chance": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [4, 5, 6, 7, 8, 9],
                    "effect": "+5% Crit Rate per level",
                    "requires": [["crit_damage", 1]]
                },
                "shield": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [3, 4, 5, 6, 7],
                    "effect": "-1s Cooldown per level",
                    "requires":
                        [
                            ["crit_chance", 3],
                            ["fire_rate", 3]
                        ]
                },
                "burn_damage": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [4, 5, 6, 7, 8],
                    "effect": "+0.5 Fire Damage per level",
                    "achievement_required": "beat_Pyraxis"
                },
                "burn_duration": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [4, 5, 6, 7, 8],
                    "effect": "+1s Fire Duration per level",
                    "requires": [["burn_damage", 3]],
                    "achievement_required": "beat_Pyraxis"
                },
                "invincibility": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [6, 7, 8, 9, 10],
                    "effect": "+0.5s Invincibility per level",
                    "requires": [["burn_duration", 1]],
                    "achievement_required": "beat_Arcanos"
                }
            },
            "achievements": {
                "beat_Pyraxis": False,
                "beat_Arcanos": False,
                "beat_Nyxblade": False,
            },
        }
        try:
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
                # Ensure all default keys are present
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
        except (FileNotFoundError, json.JSONDecodeError):
            settings = default_settings  # Use default settings if file is missing or corrupted
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=4)

        # Apply resolution on load
        pygame.display.set_mode(settings["resolution"])

        # Define default volumes for all sounds
        default_volumes = {
            "main_menu_music": 0.05,
            "game_music": 0.1,
            "boss_music": 0.1,
            "skill_music": 0.05,
            "hover_sound": 0.2,
            "click_sound": 0.3,
            "normal_hit_sound": 0.5,
            "crit_hit_sound": 0.6,
            "block_hit_sound": 0.5,
            "collect_xp_sound": 0.5,
            "level_up_sound": 0.5,
            "skill_bought_sound": 0.2,
            "skill_failed_sound": 0.2,
            "hurt_sound": 0.5,
            "death_sound": 1.0,
            "ability_obtained_sound": 0.5,
            "ability_used_sound": 0.5,
            "bat_death_sound": 0.05,
            "boss_death_sound": 0.5,
            "skeleton_death_sound": 0.6,
            "blob_death_sound": 1.3,
            "boss_spawn_sound": 0.5,
        }

        # Minimum volume threshold
        min_volume = 0.01  # 1% volume minimum

        # Apply volume settings
        master_volume = max(settings["master_volume"] / 100, min_volume)
        music_volume = max((settings["music_volume"] / 100) * master_volume, min_volume)
        effects_volume = max((settings["effects_volume"] / 100) * master_volume, min_volume)

        # Scale and apply volumes for music
        if main_menu_music: main_menu_music.set_volume(max(default_volumes["main_menu_music"] * music_volume, min_volume))
        if game_music: game_music.set_volume(max(default_volumes["game_music"] * music_volume, min_volume))
        if boss_music: boss_music.set_volume(max(default_volumes["boss_music"] * music_volume, min_volume))
        if skill_music: skill_music.set_volume(max(default_volumes["skill_music"] * music_volume, min_volume))

        # Scale and apply volumes for effects
        for sound_key, sound_obj in {
            "hover_sound": hover_sound,
            "click_sound": click_sound,
            "normal_hit_sound": normal_hit_sound,
            "crit_hit_sound": crit_hit_sound,
            "block_hit_sound": block_hit_sound,
            "collect_xp_sound": collect_xp_sound,
            "level_up_sound": level_up_sound,
            "skill_bought_sound": skill_bought_sound,
            "skill_failed_sound": skill_failed_sound,
            "hurt_sound": hurt_sound,
            "death_sound": death_sound,
            "ability_obtained_sound": ability_obtained_sound,
            "ability_used_sound": ability_used_sound,
            "bat_death_sound": bat_death_sound,
            "boss_death_sound": boss_death_sound,
            "skeleton_death_sound": skeleton_death_sound,
            "blob_death_sound": blob_death_sound,
            "boss_spawn_sound": boss_spawn_sound,
        }.items():
            if sound_obj:
                sound_obj.set_volume(max(default_volumes[sound_key] * effects_volume, min_volume))

        return settings

    def save_settings(self, achievements=None):
        """Save settings to file."""
        try:
            with open(self.settings_file, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
                # Update settings
                data.update(self.settings)
                data["resolution"] = self.settings.get("resolution", (1366, 768))
                data["high_score"] = max(data.get("high_score", 0), self.high_score)  # Keep the highest score
                
                # Update achievements if provided
                if achievements:
                    data["achievements"] = achievements
                
                # Write updated data back to the file
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            self.menu_background = self.load_menu_background()  # Reload the background image
        except FileNotFoundError:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
                
    def convert_score_to_skill_points(self, score):
        """Convert score to skill points."""
        skill_points_earned = score // 100
        self.settings["skill_points"] += skill_points_earned
        self.save_settings()

        return skill_points_earned

    def save_high_score(self, score):
        """Save high score."""
        try:
            with open(self.settings_file, "r+") as f:
                data = json.load(f)
                data["high_score"] = score
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except FileNotFoundError:
            with open(self.settings_file, "w") as f:
                json.dump({"high_score": score}, f, indent=4)

    def main_menu(self, player, enemy_manager, achievements):
        """Main menu screen."""
        main_menu_music.play(-1)
        running = True
        
        # Create buttons
        margin = 20
        button_width, button_height = 200, 50
        button_x = margin
        button_y = self.screen.get_height() - (button_height * 4) - (margin * 4)
        
        start_button = Button(button_x, button_y, button_width, button_height, 
                             "Start Game", self.font_button)
        skill_button = Button(button_x, button_y + button_height + margin, button_width, button_height,
                             "Skill Tree", self.font_button)
        settings_button = Button(button_x, button_y + (button_height + margin) * 2, button_width, button_height,
                               "Settings", self.font_button)
        quit_button = Button(button_x, button_y + (button_height + margin) * 3, button_width, button_height,
                           "Quit", self.font_button)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw background
            if self.menu_background:
                self.screen.blit(self.menu_background, (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # Draw high score
            if self.high_score > 0:
                high_score_text = self.font_score.render(f"High Score: {self.high_score}", True, WHITE)
                self.screen.blit(high_score_text, (margin, margin))
            
            # Update and draw buttons
            start_button.update(mouse_pos)
            skill_button.update(mouse_pos)
            settings_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            start_button.draw(self.screen)
            skill_button.draw(self.screen)
            settings_button.draw(self.screen)
            quit_button.draw(self.screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings(achievements=achievements)
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        running = False
                        # Call game loop through callback
                        if self.reset_game and self.game_loop:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.game_loop(player, enemy_manager, achievements)
                            
                    elif skill_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        self.skill_tree_menu(player, achievements)
                        
                    elif settings_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        self.settings_menu()
                        
                    elif quit_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        self.save_settings(achievements=achievements)
                        pygame.quit()
                        sys.exit()
            
            pygame.display.flip()

    def pause_menu(self, achievements):
        """Pause menu screen."""
        paused = True
        
        # Create buttons
        screen_width = self.screen.get_width()
        button_width, button_height = 200, 50
        button_x = (screen_width - button_width) // 2
        
        continue_button = Button(button_x, 300, button_width, button_height,
                                "Continue", self.font_button)
        menu_button = Button(button_x, 400, button_width, button_height,
                           "Main Menu", self.font_button)
        
        while paused:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill(BLACK)
            
            # Title
            title_text = self.font_title.render("Paused", True, WHITE)
            self.screen.blit(title_text, (
                (screen_width - title_text.get_width()) // 2, 150
            ))
            
            # Update and draw buttons
            continue_button.update(mouse_pos)
            menu_button.update(mouse_pos)
            
            continue_button.draw(self.screen)
            menu_button.draw(self.screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    paused = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        paused = False
                        
                    elif menu_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        game_music.stop()
                        boss_music.stop()
                        return True  # Signal to return to main menu
            
            pygame.display.flip()
        
        return False

    def game_over_screen(self, score, achievements):
        """Game over screen."""
        game_music.stop()
        boss_music.stop()
        
        # Convert score to skill points
        new_skill_points = self.convert_score_to_skill_points(score)
        self.save_settings(achievements=achievements)
        
        # Update high score
        if score > self.high_score:
            self.high_score = score
            self.save_high_score(score)
        
        running = True
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Create buttons
        button_width, button_height = 200, 50
        button_x = (screen_width - button_width) // 2
        
        restart_button = Button(button_x, screen_height // 2, button_width, button_height,
                               "Restart", self.font_button)
        menu_button = Button(button_x, screen_height // 2 + 70, button_width, button_height,
                           "Main Menu", self.font_button)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill(BLACK)
            
            # Display texts
            game_over_text = self.font_title.render("Game Over", True, WHITE)
            score_text = self.font_score.render(f"Final Score: {score}", True, WHITE)
            sp_text = self.font_score.render(f"New Skill Points: {new_skill_points}", True, WHITE)
            
            self.screen.blit(game_over_text, 
                           (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 4))
            self.screen.blit(score_text,
                           (screen_width // 2 - score_text.get_width() // 2, screen_height // 4 + 80))
            self.screen.blit(sp_text,
                           (screen_width // 2 - sp_text.get_width() // 2, screen_height // 4 + 110))
            
            # Update and draw buttons
            restart_button.update(mouse_pos)
            menu_button.update(mouse_pos)
            
            restart_button.draw(self.screen)
            menu_button.draw(self.screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        if self.reset_game and self.game_loop:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.game_loop(player, enemy_manager, achievements)
                        return
                        
                    elif menu_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        if self.reset_game:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.main_menu(player, enemy_manager, achievements)
                        return
            
            pygame.display.flip()

    def settings_menu(self):
        """Settings menu - keep existing code."""
        running = True

        # Define available resolutions
        resolutions = [(1024, 576), (1280, 720), (1366, 768)]

        # Get the stored resolution, ensuring it is a tuple
        stored_resolution = self.settings.get("resolution", (1366, 768))
        current_resolution = tuple(stored_resolution) if isinstance(stored_resolution, list) else stored_resolution

        # Find the current resolution index, defaulting to (1366, 768) if not found
        if current_resolution not in resolutions:
            current_resolution_index = resolutions.index((1366, 768))
        else:
            current_resolution_index = resolutions.index(current_resolution)

        hovered_button = None

        # Minimum volume threshold (ensures sound is always audible)
        min_volume = 0.01  # 1% volume minimum

        while running:
            self.screen.fill(BLACK)

            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Define volume settings
            options = [
                {"label": "Master Volume", "key": "master_volume"},
                {"label": "Music Volume", "key": "music_volume"},
                {"label": "Effects Volume", "key": "effects_volume"},
            ]

            # Draw sliders for volume settings
            for i, option in enumerate(options):
                label = self.font_button.render(f"{option['label']}: {self.settings.get(option['key'], 100)}%", True, WHITE)
                slider_x = (self.screen.get_width() - 300) // 2
                slider_y = 150 + i * 100
                slider_width = 300
                slider_height = 20

                pygame.draw.rect(self.screen, GRAY, (slider_x, slider_y, slider_width, slider_height))
                slider_fill_width = int((self.settings[option['key']] / 100) * slider_width)
                pygame.draw.rect(self.screen, GREEN, (slider_x, slider_y, slider_fill_width, slider_height))
                self.screen.blit(label, (slider_x, slider_y - 40))

                # Handle slider interaction
                if pygame.mouse.get_pressed()[0] and slider_x <= mouse_x <= slider_x + slider_width and \
                        slider_y <= mouse_y <= slider_y + slider_height:
                    new_value = int(((mouse_x - slider_x) / slider_width) * 100)
                    self.settings[option['key']] = max(0, min(100, new_value))

                    # Apply volume changes dynamically
                    master_volume = max(self.settings["master_volume"] / 100, min_volume)
                    music_volume = max((self.settings["music_volume"] / 100) * master_volume, min_volume)
                    effects_volume = max((self.settings["effects_volume"] / 100) * master_volume, min_volume)

                    # Adjust music volumes
                    for music, default_vol in {
                        main_menu_music: 0.05,
                        game_music: 0.1,
                        boss_music: 0.1,
                        skill_music: 0.05
                    }.items():
                        if music:
                            music.set_volume(max(default_vol * music_volume, min_volume))

                    # Adjust effects volumes
                    for sound, default_vol in {
                        hover_sound: 0.3,
                        click_sound: 0.3,
                        normal_hit_sound: 0.5,
                        crit_hit_sound: 0.6,
                        block_hit_sound: 0.5,
                        collect_xp_sound: 0.5,
                        level_up_sound: 0.5,
                        skill_bought_sound: 0.5,
                        skill_failed_sound: 0.5,
                        hurt_sound: 0.5,
                        death_sound: 1.0,
                        ability_obtained_sound: 0.5,
                        ability_used_sound: 0.5,
                        bat_death_sound: 0.05,
                        boss_death_sound: 0.5,
                        skeleton_death_sound: 0.6,
                        blob_death_sound: 1.3,
                        boss_spawn_sound: 0.5,
                    }.items():
                        if sound:
                            sound.set_volume(max(default_vol * effects_volume, min_volume))

            # Resolution Setting with Arrows
            resolution_text = self.font_button.render(f"{resolutions[current_resolution_index][0]}x{resolutions[current_resolution_index][1]}", True, WHITE)
            res_text_x = (self.screen.get_width() - resolution_text.get_width()) // 2
            res_text_y = 450
            self.screen.blit(resolution_text, (res_text_x, res_text_y))

            # Draw Left Arrow
            if current_resolution_index > 0:
                left_arrow_x = res_text_x - 40
                left_arrow_y = res_text_y + 10
                pygame.draw.polygon(self.screen, WHITE, [
                    (left_arrow_x + 20, left_arrow_y),  # Pointy tip
                    (left_arrow_x, left_arrow_y + 10),  # Bottom
                    (left_arrow_x + 20, left_arrow_y + 20)  # Top
                ])
                if pygame.mouse.get_pressed()[0] and left_arrow_x <= mouse_x <= left_arrow_x + 20 and \
                        left_arrow_y <= mouse_y <= left_arrow_y + 20:
                    current_resolution_index -= 1
                    self.settings["resolution"] = resolutions[current_resolution_index]
                    pygame.display.set_mode(resolutions[current_resolution_index])

            # Draw Right Arrow
            if current_resolution_index < len(resolutions) - 1:
                right_arrow_x = res_text_x + resolution_text.get_width() + 40  # Adjusted spacing
                right_arrow_y = res_text_y + 10
                pygame.draw.polygon(self.screen, WHITE, [
                    (right_arrow_x - 20, right_arrow_y),  # Pointy tip
                    (right_arrow_x, right_arrow_y + 10),  # Bottom
                    (right_arrow_x - 20, right_arrow_y + 20)  # Top
                ])
                if pygame.mouse.get_pressed()[0] and right_arrow_x - 20 <= mouse_x <= right_arrow_x and \
                        right_arrow_y <= mouse_y <= right_arrow_y + 20:
                    current_resolution_index += 1
                    self.settings["resolution"] = resolutions[current_resolution_index]
                    pygame.display.set_mode(resolutions[current_resolution_index])

            # Back Button (Save and Return to Main Menu)
            back_button_x = 20
            back_button_y = self.screen.get_height() - 70
            back_button_width, back_button_height = 150, 50
            back_hovered = back_button_x < mouse_x < back_button_x + back_button_width and \
                        back_button_y < mouse_y < back_button_y + back_button_height
            back_button_color = DARK_RED if back_hovered else RED
            pygame.draw.rect(self.screen, back_button_color, (back_button_x, back_button_y, back_button_width, back_button_height))
            back_text = self.font_button.render("Back", True, WHITE)
            self.screen.blit(back_text, (
                back_button_x + (back_button_width - back_text.get_width()) // 2,
                back_button_y + (back_button_height - back_text.get_height()) // 2
            ))

            # Reset Button
            reset_button_width, reset_button_height = 150, 50
            reset_button_x = self.screen.get_width() - reset_button_width - 20
            reset_button_y = self.screen.get_height() - reset_button_height - 20
            reset_hovered = reset_button_x < mouse_x < reset_button_x + reset_button_width and \
                            reset_button_y < mouse_y < reset_button_y + reset_button_height
            reset_button_color = DARK_RED if reset_hovered else RED
            pygame.draw.rect(self.screen, reset_button_color, (reset_button_x, reset_button_y, reset_button_width, reset_button_height))
            reset_text = self.font_button.render("Reset", True, WHITE)
            self.screen.blit(reset_text, (
                reset_button_x + (reset_button_width - reset_text.get_width()) // 2,
                reset_button_y + (reset_button_height - reset_text.get_height()) // 2
            ))

            # Play hover sound for the Back button
            if back_hovered and hovered_button != "back":
                hover_sound.play()
                hovered_button = "back"
            elif not back_hovered and hovered_button == "back":
                hovered_button = None

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_hovered:
                        click_sound.play()  # Play click sound
                        self.save_settings()
                        running = False
                    elif reset_hovered:
                        click_sound.play()
                        try:
                            os.remove("utils.json")
                            print("[DEBUG] utils.json file deleted successfully.")
                        except FileNotFoundError:
                            print("[DEBUG] utils.json file not found.")
                        self.settings = self.load_settings()

            pygame.display.flip()

    def skill_tree_menu(self, player, achievements):
        """Skill tree menu - keep existing code."""
        running = True
        selected_skill = None  # Currently selected skill for the right panel
        upgrade_button = None  # Track the upgrade button rect

        main_menu_music.stop()  # Stop the main menu music
        skill_music.play(-1)  # Loop the skill tree music indefinitely

        achievements = achievements or self.settings["achievements"]

        # Define skill tree layout (coordinates and connections)
        screen_width, screen_height = self.settings["resolution"]
        scale_factor_x = screen_width / 1280  # Based on default width
        scale_factor_y = screen_height / 720  # Based on default height

        skill_positions = {
            "max_health": (int(300 * scale_factor_x), int(50 * scale_factor_y)),
            "speed": (int(500 * scale_factor_x), int(50 * scale_factor_y)),
            "heal": (int(400 * scale_factor_x), int(200 * scale_factor_y)),
            "damage": (int(300 * scale_factor_x), int(350 * scale_factor_y)),
            "fire_rate": (int(300 * scale_factor_x), int(500 * scale_factor_y)),
            "crit_damage": (int(500 * scale_factor_x), int(350 * scale_factor_y)),
            "crit_chance": (int(500 * scale_factor_x), int(500 * scale_factor_y)),
            "shield": (int(400 * scale_factor_x), int(650 * scale_factor_y)),
            "burn_damage": (int(700 * scale_factor_x), int(200 * scale_factor_y)),
            "burn_duration": (int(700 * scale_factor_x), int(350 * scale_factor_y)),
            "invincibility": (int(700 * scale_factor_x), int(500 * scale_factor_y)),
        }

        connections = [
            ("max_health", "heal"),
            ("speed", "heal"),
            ("heal", "damage"),
            ("damage", "fire_rate"),
            ("fire_rate", "shield"),
            ("heal", "crit_damage"),
            ("crit_damage", "crit_chance"),
            ("crit_chance", "shield"),
            ("burn_damage", "burn_duration"),
            ("burn_duration", "invincibility"),
        ]

        def render_screen():
            """Render the entire skill tree screen."""
            self.screen.fill(BLACK)  # Background color
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Display available skill points
            sp_text = self.font_score.render(f"SP: {self.settings['skill_points']}", True, WHITE)
            self.screen.blit(sp_text, (20, 20))

            # Draw connections
            for start, end in connections:
                pygame.draw.line(
                    self.screen, WHITE, skill_positions[start], skill_positions[end], 2
                )

            # Draw skills
            for skill_name, skill_data in self.settings["skills"].items():
                level = skill_data["level"]
                max_level = skill_data["max_level"]
                skill_type = skill_data.get("type", "abilities")
                x, y = skill_positions[skill_name]

                # Validate requirements
                can_unlock = True
                requirements = skill_data.get("requires", [])
                for requirement in requirements:
                    required_skill, required_level = requirement
                    if self.settings["skills"].get(required_skill, {}).get("level", 0) < required_level:
                        can_unlock = False

                achievement = skill_data.get("achievement_required")
                if achievement and not achievements.get(achievement, False):
                    can_unlock = False

                # Load skill icon and frame or locked icon
                icon_path = (
                    f'./assets/images/{skill_type}/{skill_name}.png'
                    if can_unlock or level > 0
                    else './assets/images/locked.png'
                )
                frame_level = min(level + 1, 6 if skill_type == "stats" else 5)
                frame_path = (
                    f'./assets/images/{skill_type}/{skill_type}-frame-{frame_level}.png'
                    if level > 0
                    else None
                )

                try:
                    # Highlight skill if hovered or selected
                    highlight_color = RED if pygame.Rect(x - 40, y - 40, 80, 80).collidepoint(mouse_x, mouse_y) else None
                    if highlight_color:
                        pygame.draw.rect(self.screen, highlight_color, (x - 40, y - 40, 80, 80), 5)  # Larger margin for highlight

                    # Load and display the frame if the skill has a level
                    if frame_path:
                        frame = pygame.image.load(frame_path)
                        frame = pygame.transform.scale(frame, (80, 80))  # Slightly larger frame for visibility
                        self.screen.blit(frame, (x - 40, y - 40))

                    # Load and display the icon
                    icon = pygame.image.load(icon_path)
                    icon = pygame.transform.scale(icon, (60, 60))
                    self.screen.blit(icon, (x - 30, y - 30))  # Center the icon
                except FileNotFoundError:
                    print(f"[DEBUG] Missing image or frame for {skill_name}: {icon_path} or {frame_path}")

            # Draw the right panel for selected skill
            if selected_skill:
                nonlocal upgrade_button
                upgrade_button = render_selected_skill(selected_skill)

            # Back Button (Save and Return to Main Menu)
            back_button_x = 20
            back_button_y = self.screen.get_height() - 70
            back_button_width, back_button_height = 150, 50
            back_hovered = back_button_x < mouse_x < back_button_x + back_button_width and \
                        back_button_y < mouse_y < back_button_y + back_button_height
            back_button_color = DARK_RED if back_hovered else RED
            pygame.draw.rect(self.screen, back_button_color, (back_button_x, back_button_y, back_button_width, back_button_height))
            back_text = self.font_button.render("Back", True, WHITE)
            self.screen.blit(back_text, (
                back_button_x + (back_button_width - back_text.get_width()) // 2,
                back_button_y + (back_button_height - back_text.get_height()) // 2
            ))

        def render_selected_skill(skill_name):
            """Render the right panel for the selected skill."""
            skill_data = self.settings["skills"][skill_name]
            details_x = screen_width - int(300 * scale_factor_x)
            details_y = int(100 * scale_factor_y)

            # Check if the skill can be upgraded
            can_unlock = True
            unmet_requirements = []

            # Check prerequisites
            requirements = skill_data.get("requires", [])
            for prereq_skill, prereq_level in requirements:
                prereq_data = self.settings["skills"].get(prereq_skill)
                if not prereq_data or prereq_data["level"] < prereq_level:
                    unmet_requirements.append(f"{prereq_skill.replace('_', ' ').title()} Lv {prereq_level}")
                    can_unlock = False

            # Check achievement requirements
            achievement_required = skill_data.get("achievement_required")
            if achievement_required and not achievements.get(achievement_required, False):
                unmet_requirements.append(f"{achievement_required.replace('_', ' ').title()}")
                can_unlock = False

            # Display locked state if requirements are not met
            if not can_unlock:
                try:
                    # Load and display the lock icon
                    lock_icon = pygame.image.load('./assets/images/locked.png')
                    lock_icon = pygame.transform.scale(lock_icon, (100, 100))
                    icon_center_x = details_x + 10 + (120 // 2)  # Center of the image frame (image width = 120)
                    self.screen.blit(lock_icon, (details_x + 20, details_y + 50))  # Draw the lock icon

                    # Center and display the "Locked" text
                    name_text = self.font_button.render("Locked", True, WHITE)
                    self.screen.blit(name_text, (icon_center_x - name_text.get_width() // 2, details_y + 200))

                    # Display and center unmet requirements below the "Locked" text
                    for idx, req in enumerate(unmet_requirements):
                        req_text = self.font_button.render(req, True, RED)
                        self.screen.blit(req_text, (
                            icon_center_x - req_text.get_width() // 2,  # Center horizontally
                            details_y + 240 + idx * 40                 # Space out requirements vertically
                        ))
                except FileNotFoundError:
                    print("[DEBUG] Missing lock icon")
                return

            # If requirements are met, show the skill icon, frame, and details
            level = skill_data["level"]
            max_level = skill_data["max_level"]
            skill_type = skill_data["type"]
            icon_path = f'./assets/images/{skill_type}/{skill_name}.png'
            frame_level = min(level + 1, 6 if skill_type == "stats" else 5)
            frame_path = f'./assets/images/{skill_type}/{skill_type}-frame-{frame_level}.png'

            try:
                # Load and display the icon
                icon = pygame.image.load(icon_path)
                icon = pygame.transform.scale(icon, (100, 100))
                self.screen.blit(icon, (details_x + 20, details_y + 50))

                if level > 0:
                    # Load and display the frame
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (120, 120))
                    self.screen.blit(frame, (details_x + 10, details_y + 40))
            except FileNotFoundError as e:
                print(f"[DEBUG] Missing frame or icon for {skill_name}: {e}")

            # Display skill details
            effect = skill_data["effect"]
            cost = skill_data["costs"][level] if level < max_level else "MAX"

            # Render texts
            name_text = self.font_button.render(skill_name.replace("_", " ").title() + f" {level}/{max_level}", True, WHITE)
            cost_text = self.font_button.render(f"SP: {cost}", True, WHITE)
            effect_text = self.font_button.render(f"{effect}", True, WHITE)

            # Calculate horizontal center based on the skill image position
            text_center_x = details_x + 10 + (120 // 2)  # Center of the image frame (image width = 120)

            # Display centered text
            self.screen.blit(name_text, (text_center_x - name_text.get_width() // 2, details_y + 200))
            self.screen.blit(cost_text, (text_center_x - cost_text.get_width() // 2, details_y + 240))
            self.screen.blit(effect_text, (text_center_x - effect_text.get_width() // 2, details_y + 280))

            # Return the upgrade button rect
            button_x = details_x - 27.5
            button_y = details_y + 380
            button_width, button_height = 200, 50

            # Determine button text
            button_text = "Upgrade" if level < max_level else "MAXED"

            # Draw the button
            pygame.draw.rect(self.screen, RED if level < max_level else GRAY, (button_x, button_y, button_width, button_height))

            # Render the text and display it on the button
            text_surface = self.font_button.render(button_text, True, WHITE)
            self.screen.blit(
                text_surface, 
                (button_x + (button_width - text_surface.get_width()) // 2, button_y + (button_height - text_surface.get_height()) // 2)
            )

            # Return the button rect
            return pygame.Rect(button_x, button_y, button_width, button_height)


        # Initial render
        render_screen()
        pygame.display.flip()

        # Main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check for skill node clicks
                    for skill_name, (x, y) in skill_positions.items():
                        if pygame.Rect(x - 30, y - 30, 60, 60).collidepoint(mouse_x, mouse_y):
                            selected_skill = skill_name
                            render_screen()  # Refresh the screen with the selected skill

                    # Check for back button click
                    button_x = 20
                    button_y = screen_height - 70
                    button_width, button_height = 200, 50
                    if pygame.Rect(button_x, button_y, button_width, button_height).collidepoint(mouse_x, mouse_y):
                        click_sound.play()
                        skill_music.stop()
                        main_menu_music.play(-1)
                        player.apply_skill_upgrades(self.settings["skills"])
                        player.apply_stat_upgrades(self.settings["skills"])
                        player.abilities = []
                        player.initialize_abilities(self.settings["skills"])
                        running = False

                    # Handle upgrade button click
                    if upgrade_button and upgrade_button.collidepoint(mouse_x, mouse_y):
                        skill_data = self.settings["skills"][selected_skill]
                        level = skill_data["level"]
                        max_level = skill_data["max_level"]
                        cost = skill_data["costs"][level] if level < max_level else None

                        if level < max_level and self.settings["skill_points"] >= cost:
                            skill_bought_sound.play()
                            self.settings["skill_points"] -= cost
                            skill_data["level"] += 1
                            self.save_settings()
                            render_screen()  # Refresh screen
                        else:
                            skill_failed_sound.play()

            pygame.display.flip()

    def level_up_menu(self, player, screen):
        """Displays the level-up menu and lets the player choose an upgrade."""
        running = True

        # Play the level-up sound
        level_up_sound.play()

        # Define all possible upgrades
        all_upgrades = [
            {"text": "Increase Fire Rate by 20%", "upgrade": "fire_rate"},
            {"text": "Increase Damage by 30%", "upgrade": "damage"},
            {"text": "Restore 40 HP", "upgrade": "health"},
            {"text": "Increase Max Health by 20", "upgrade": "max_health"},
            {"text": "Increase Speed by 13%", "upgrade": "speed"},
            {"text": "Increase Crit Chance by 5%", "upgrade": "crit_chance"}
        ]

        # Randomly select 3 upgrades
        selected_upgrades = random.sample(all_upgrades, 3)

        hovered_button = None  # To track which button is hovered

        while running:
            self.screen.fill(BLACK)

            # Get dynamic screen dimensions
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            # Render the title text
            title_text = self.font_title.render("Level Up!", True, WHITE)
            screen.blit(title_text, (
                screen_width // 2 - title_text.get_width() // 2, 
                screen_height // 4 - 50
            ))

            # Mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Draw buttons and check hover
            button_rects = []  # Store button rects for later click detection
            for i, option in enumerate(selected_upgrades):
                # Button dimensions
                button_width = 350
                button_height = 50
                button_x = screen_width // 2 - button_width // 2
                button_y = screen_height // 4 + 80 + i * 100

                # Detect hover
                is_hovered = button_x < mouse_x < button_x + button_width and button_y < mouse_y < button_y + button_height
                button_color = DARK_RED if is_hovered else RED

                # Draw the button
                pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))

                # Render button text
                option_text = self.font_button.render(option["text"], True, WHITE)
                screen.blit(option_text, (
                    button_x + (button_width - option_text.get_width()) // 2,
                    button_y + (button_height - option_text.get_height()) // 2
                ))

                # Play hover sound
                if is_hovered and hovered_button != i:
                    hover_sound.play()
                    hovered_button = i
                elif not is_hovered and hovered_button == i:
                    hovered_button = None

                # Add button rect for click detection
                button_rects.append(pygame.Rect(button_x, button_y, button_width, button_height))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(mouse_x, mouse_y):  # Check if click is inside button rect
                            click_sound.play()  # Play click sound
                            player.apply_upgrade(selected_upgrades[i]["upgrade"])
                            running = False  # Exit menu

            pygame.display.flip()

        # Update last_shot_time to avoid firing immediately after exiting the menu
        player.last_shot_time = pygame.time.get_ticks()