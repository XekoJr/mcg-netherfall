import json
import os
import pygame
import sys
import random
from assets import *
from ui.ui_elements import Button
from ui.utils import (
    IconButton, TextButton, Panel, RepeatingBackground, 
    Slider, Arrow, show_loading_screen
)

class Menu:
    """Handles all menu screens and UI navigation."""

    @staticmethod
    def initialize_display(save_manager):
        """Initialize display based on saved settings."""
        settings = save_manager.load()
        
        resolution = settings.get("resolution", (1366, 768))
        fullscreen = settings.get("fullscreen", False)
        borderless = settings.get("borderless", False)
        
        if borderless:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
            actual_resolution = screen.get_size()
            settings["resolution"] = actual_resolution
            save_manager.save(settings)
        elif fullscreen:
            screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(resolution)
        
        pygame.display.set_caption("MCG Netherfall")
        return screen

    def __init__(self, screen, font_title=None, font_button=None, font_credit=None, font_score=None):
        from managers import SaveManager
        
        self.screen = screen
        self.save_manager = SaveManager(save_file="save/save.dat")
        self.settings = self.save_manager.load()
        
        # Load translations
        self.translations = {}
        self.current_language = self.settings.get("language", "en")
        self._load_translations()
        
        # Apply saved volume settings to all audio
        self._apply_volume_settings()
        
        # Load main menu background
        self.menu_background = self.load_menu_background()
        
        # Initialize repeating pattern background for other screens
        self.pattern_background = RepeatingBackground(
            pattern_path="assets/images/background/background-pattern.png",
            fallback_color=BLACK
        )
        
        self.high_score = self.settings.get("high_score", 0)
        
        # Store font references
        self.font_title = font_title
        self.font_button = font_button 
        self.font_credit = font_credit
        self.font_score = font_score
        
        # Callbacks set by main.py
        self.reset_game = None
        self.game_loop = None

    def _load_translations(self):
        """Load translation file for current language."""
        lang_file = f"./translations/{self.current_language}.json"
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Translation file not found: {lang_file}, falling back to English")
            try:
                with open("./translations/en.json", 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except FileNotFoundError:
                print("ERROR: English translation file not found!")
                self.translations = {}

    def t(self, key_path, **kwargs):
        """
        Get translated text by key path.
        Supports variable substitution using kwargs.
        """
        keys = key_path.split('.')
        value = self.translations
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, key_path)
            else:
                return key_path
        
        # Replace variables if any
        if isinstance(value, str) and kwargs:
            return value.format(**kwargs)
        
        return value

    def _apply_volume_settings(self):
        """Apply volume settings to all sounds and music based on master volume."""
        min_volume = 0.01
        
        # Calculate volume multipliers
        master_volume = max(self.settings.get("master_volume", 100) / 100, min_volume)
        music_volume = max((self.settings.get("music_volume", 100) / 100) * master_volume, min_volume)
        effects_volume = max((self.settings.get("effects_volume", 100) / 100) * master_volume, min_volume)
        
        # Apply to music tracks
        music_tracks = {
            main_menu_music: 0.05,
            game_music: 0.1,
            boss_music: 0.1,
            skill_music: 0.05
        }
        
        for music, default_vol in music_tracks.items():
            if music:
                music.set_volume(max(default_vol * music_volume, min_volume))
        
        # Apply to sound effects
        sound_effects = {
            hover_sound: 0.3, click_sound: 0.3,
            normal_hit_sound: 0.5, crit_hit_sound: 0.6,
            block_hit_sound: 0.5, collect_xp_sound: 0.5,
            level_up_sound: 0.5, skill_bought_sound: 0.5,
            skill_failed_sound: 0.5, hurt_sound: 0.5,
            death_sound: 1.0, ability_obtained_sound: 0.5,
            ability_used_sound: 0.5, bat_death_sound: 0.05,
            boss_death_sound: 0.5, skeleton_death_sound: 0.6,
            blob_death_sound: 1.3, boss_spawn_sound: 0.5,
        }
        
        for sound, default_vol in sound_effects.items():
            if sound:
                sound.set_volume(max(default_vol * effects_volume, min_volume))

    def load_menu_background(self):
        """Load and scale the main menu background image."""
        try:
            bg = pygame.image.load("assets/images/background/netherfall-game-background.png")
            return pygame.transform.scale(bg, (self.screen.get_width(), self.screen.get_height()))
        except pygame.error as e:
            print(f"Error loading menu background: {e}")
            return None

    def load_settings(self):
        """Load settings from save file."""
        return self.save_manager.load()

    def save_settings(self, achievements=None):
        """Save settings to file, optionally including achievements."""
        if achievements:
            self.settings["achievements"] = achievements
        self.save_manager.save(self.settings)

    def convert_score_to_skill_points(self, score):
        """Convert final score to skill points (50 score = 1 SP)."""
        skill_points_earned = score // 50
        self.settings["skill_points"] += skill_points_earned
        self.save_settings()
        return skill_points_earned

    def save_high_score(self, score):
        """Update high score if current score is higher."""
        self.settings["high_score"] = score
        self.save_manager.save(self.settings)

    def main_menu(self, player, enemy_manager, achievements):
        """Main menu with centered action buttons and utility buttons in bottom-left."""
        main_menu_music.play(-1)
        running = True
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        margin = 20
        button_size = 60
        
        # Darker red color for utility buttons
        utility_button_color = (100, 0, 0)
        utility_button_hover = (70, 0, 0)
        
        # Calculate centered button positions
        center_button_width = 250
        center_button_height = 60
        center_button_spacing = 20
        total_center_height = (center_button_height * 3) + (center_button_spacing * 2)
        
        center_x = (screen_width - center_button_width) // 2
        start_y = (screen_height - total_center_height) // 2
        
        # Create main action buttons with translations
        play_button = Button(center_x, start_y, center_button_width, center_button_height, 
                            self.t('main_menu.play'), self.font_button)
        skill_button = Button(center_x, start_y + center_button_height + center_button_spacing, 
                             center_button_width, center_button_height, self.t('main_menu.skill_tree'), self.font_button)
        store_button = Button(center_x, start_y + (center_button_height + center_button_spacing) * 2,
                             center_button_width, center_button_height, self.t('main_menu.store'), self.font_button)
        
        # Create utility icon buttons
        lang_button = IconButton(
            margin,
            screen_height - (button_size * 3) - (margin * 3),
            button_size,
            'assets/images/icons/language.png',
            hover_color=utility_button_hover,
            normal_color=utility_button_color
        )
        
        settings_button = IconButton(
            margin,
            screen_height - (button_size * 2) - (margin * 2),
            button_size,
            'assets/images/icons/settings.png',
            hover_color=utility_button_hover,
            normal_color=utility_button_color
        )
        
        quit_button = IconButton(
            margin,
            screen_height - button_size - margin,
            button_size,
            'assets/images/icons/exit.png',
            hover_color=utility_button_hover,
            normal_color=utility_button_color
        )
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw main menu background
            if self.menu_background:
                self.screen.blit(self.menu_background, (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # Update and draw center buttons
            play_button.update(mouse_pos)
            skill_button.update(mouse_pos)
            store_button.update(mouse_pos)
            
            play_button.draw(self.screen)
            skill_button.draw(self.screen)
            store_button.draw(self.screen)
            
            # Update and draw utility icon buttons
            lang_button.update(mouse_pos)
            settings_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            lang_button.draw(self.screen)
            settings_button.draw(self.screen)
            quit_button.draw(self.screen)
            
            # Draw scoreboard panel in bottom-right
            scoreboard_width = 250
            scoreboard_height = 300
            scoreboard_x = screen_width - scoreboard_width - margin
            scoreboard_y = screen_height - scoreboard_height - margin
            
            Panel.draw(self.screen, scoreboard_x, scoreboard_y, scoreboard_width, scoreboard_height)
            
            scoreboard_title = self.font_button.render(self.t('main_menu.scoreboard'), True, WHITE)
            self.screen.blit(scoreboard_title, (
                scoreboard_x + (scoreboard_width - scoreboard_title.get_width()) // 2,
                scoreboard_y + 20
            ))
            
            if self.high_score > 0:
                high_score_text = self.font_score.render(
                    self.t('main_menu.me', score=self.high_score), True, WHITE
                )
                self.screen.blit(high_score_text, (
                    scoreboard_x + (scoreboard_width - high_score_text.get_width()) // 2,
                    scoreboard_y + 70
                ))
            
            # Handle user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings(achievements=achievements)
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Main action buttons
                    if play_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        if self.reset_game and self.game_loop:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.game_loop(player, enemy_manager, achievements)
                        # Reload background after returning from game
                        self.menu_background = self.load_menu_background()
                        
                    elif skill_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        self.skill_tree_menu(player, achievements)
                        self.menu_background = self.load_menu_background()
                        
                    elif store_button.rect.collidepoint(mouse_pos):
                        click_sound.play()
                        self.store_menu(player, achievements)
                    
                    # Utility buttons
                    elif quit_button.is_clicked(mouse_pos):
                        click_sound.play()
                        self.save_settings(achievements=achievements)
                        pygame.quit()
                        sys.exit()
                    
                    elif settings_button.is_clicked(mouse_pos):
                        click_sound.play()
                        self.settings_menu()
                        # Reload background and recreate all UI elements for new resolution
                        self.menu_background = self.load_menu_background()
                        screen_width = self.screen.get_width()
                        screen_height = self.screen.get_height()
                        
                        # Recreate main action buttons
                        center_x = (screen_width - center_button_width) // 2
                        start_y = (screen_height - total_center_height) // 2
                        play_button = Button(center_x, start_y, center_button_width, center_button_height, 
                                            self.t('main_menu.play'), self.font_button)
                        skill_button = Button(center_x, start_y + center_button_height + center_button_spacing, 
                                             center_button_width, center_button_height, self.t('main_menu.skill_tree'), self.font_button)
                        store_button = Button(center_x, start_y + (center_button_height + center_button_spacing) * 2,
                                             center_button_width, center_button_height, self.t('main_menu.store'), self.font_button)
                        
                        lang_button = IconButton(
                            margin,
                            screen_height - (button_size * 3) - (margin * 3),
                            button_size,
                            'assets/images/icons/language.png',
                            hover_color=utility_button_hover,
                            normal_color=utility_button_color
                        )
                        settings_button = IconButton(
                            margin,
                            screen_height - (button_size * 2) - (margin * 2),
                            button_size,
                            'assets/images/icons/settings.png',
                            hover_color=utility_button_hover,
                            normal_color=utility_button_color
                        )
                        quit_button = IconButton(
                            margin,
                            screen_height - button_size - margin,
                            button_size,
                            'assets/images/icons/exit.png',
                            hover_color=utility_button_hover,
                            normal_color=utility_button_color
                        )
                        
                    elif lang_button.is_clicked(mouse_pos):
                        click_sound.play()
                        self.language_menu()
                        # Reload translations after language change
                        self._load_translations()
                        # Recreate buttons with new translations
                        play_button = Button(center_x, start_y, center_button_width, center_button_height, 
                                            self.t('main_menu.play'), self.font_button)
                        skill_button = Button(center_x, start_y + center_button_height + center_button_spacing, 
                                             center_button_width, center_button_height, self.t('main_menu.skill_tree'), self.font_button)
                        store_button = Button(center_x, start_y + (center_button_height + center_button_spacing) * 2,
                                             center_button_width, center_button_height, self.t('main_menu.store'), self.font_button)
            
            pygame.display.flip()

    def pause_menu(self, achievements):
        """Pause menu shown during gameplay."""
        paused = True
        
        screen_width = self.screen.get_width()
        button_width, button_height = 200, 50
        button_x = (screen_width - button_width) // 2
        
        # Create pause menu buttons with translations
        continue_button = TextButton(button_x, 300, button_width, button_height, 
                                     self.t('pause_menu.continue'), self.font_button)
        menu_button = TextButton(button_x, 400, button_width, button_height, 
                                self.t('pause_menu.main_menu'), self.font_button)
        
        while paused:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw pattern background
            self.pattern_background.draw(self.screen)
            
            # Draw title
            title_text = self.font_title.render(self.t('pause_menu.title'), True, WHITE)
            self.screen.blit(title_text, ((screen_width - title_text.get_width()) // 2, 150))
            
            # Update and draw buttons
            continue_button.update(mouse_pos)
            menu_button.update(mouse_pos)
            
            continue_button.draw(self.screen)
            menu_button.draw(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                # ESC key to unpause
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    click_sound.play()
                    paused = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button.is_clicked(mouse_pos):
                        click_sound.play()
                        paused = False
                        
                    elif menu_button.is_clicked(mouse_pos):
                        click_sound.play()
                        game_music.stop()
                        boss_music.stop()
                        return True  # Signal to return to main menu
            
            pygame.display.flip()
        
        return False

    def game_over_screen(self, score, achievements):
        """Display game over screen with score and options."""
        game_music.stop()
        boss_music.stop()
        
        # Convert score to skill points
        new_skill_points = self.convert_score_to_skill_points(score)
        self.save_settings(achievements=achievements)
        
        # Update high score if necessary
        if score > self.high_score:
            self.high_score = score
            self.save_high_score(score)
        
        running = True
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        button_width, button_height = 200, 50
        button_x = (screen_width - button_width) // 2
        
        # Create game over buttons with translations
        restart_button = TextButton(button_x, screen_height // 2, button_width, button_height, 
                                    self.t('game_over.restart'), self.font_button)
        menu_button = TextButton(button_x, screen_height // 2 + 70, button_width, button_height, 
                                self.t('game_over.main_menu'), self.font_button)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw pattern background
            self.pattern_background.draw(self.screen)
            
            # Display game over text and stats
            game_over_text = self.font_title.render(self.t('game_over.title'), True, WHITE)
            score_text = self.font_score.render(self.t('game_over.final_score', score=score), True, WHITE)
            sp_text = self.font_score.render(self.t('game_over.new_skill_points', points=new_skill_points), True, WHITE)
            
            self.screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 4))
            self.screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 4 + 80))
            self.screen.blit(sp_text, (screen_width // 2 - sp_text.get_width() // 2, screen_height // 4 + 110))
            
            # Update and draw buttons
            restart_button.update(mouse_pos)
            menu_button.update(mouse_pos)
            
            restart_button.draw(self.screen)
            menu_button.draw(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_clicked(mouse_pos):
                        click_sound.play()
                        if self.reset_game and self.game_loop:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.game_loop(player, enemy_manager, achievements)
                        return
                        
                    elif menu_button.is_clicked(mouse_pos):
                        click_sound.play()
                        if self.reset_game:
                            player, enemy_manager, achievements = self.reset_game(achievements)
                            self.main_menu(player, enemy_manager, achievements)
                        return
            
            pygame.display.flip()

    def settings_menu(self):
        """Settings menu for audio, display, and graphics configuration."""
        running = True

        # Get native display resolution
        display_info = pygame.display.Info()
        native_width = display_info.current_w
        native_height = display_info.current_h

        # Available resolutions
        resolutions = sorted(list(set([
            (1024, 576),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (native_width, native_height)
        ])))

        # Display modes with translations
        display_modes = [
            {"name": self.t('settings.windowed'), "fullscreen": False},
            {"name": self.t('settings.windowed_fullscreen'), "fullscreen": True, "borderless": True},
            {"name": self.t('settings.fullscreen'), "fullscreen": True, "borderless": False}
        ]

        # Get current resolution
        stored_resolution = self.settings.get("resolution", (1366, 768))
        current_resolution = tuple(stored_resolution) if isinstance(stored_resolution, list) else stored_resolution
        
        if current_resolution not in resolutions:
            current_resolution_index = 2
        else:
            current_resolution_index = resolutions.index(current_resolution)

        # Determine current display mode
        current_fullscreen = self.settings.get("fullscreen", False)
        current_borderless = self.settings.get("borderless", False)
        
        if current_fullscreen and current_borderless:
            current_display_mode_index = 1
        elif current_fullscreen:
            current_display_mode_index = 2
        else:
            current_display_mode_index = 0

        # Create volume sliders
        sliders = {
            "master_volume": Slider(0, 0, 300, 20, 0, 100, self.settings.get("master_volume", 100)),
            "music_volume": Slider(0, 0, 300, 20, 0, 100, self.settings.get("music_volume", 100)),
            "effects_volume": Slider(0, 0, 300, 20, 0, 100, self.settings.get("effects_volume", 100)),
        }

        # Create buttons with translations
        back_button = TextButton(20, 0, 150, 50, self.t('settings.back'), self.font_button)
        reset_button = TextButton(0, 0, 150, 50, self.t('settings.reset'), self.font_button)

        while running:
            # Draw pattern background
            self.pattern_background.draw(self.screen)
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            back_button.rect.y = self.screen.get_height() - 70
            reset_button.rect.x = self.screen.get_width() - 170
            reset_button.rect.y = self.screen.get_height() - 70

            title_text = self.font_title.render(self.t('settings.title'), True, WHITE)
            self.screen.blit(title_text, ((self.screen.get_width() - title_text.get_width()) // 2, 30))

            # Volume sliders with translations
            slider_labels = [
                (self.t('settings.master_volume'), "master_volume"),
                (self.t('settings.music_volume'), "music_volume"),
                (self.t('settings.effects_volume'), "effects_volume"),
            ]

            for i, (label_text, key) in enumerate(slider_labels):
                slider = sliders[key]
                
                slider_x = (self.screen.get_width() - 300) // 2
                slider_y = 120 + i * 80
                slider.rect.x = slider_x
                slider.rect.y = slider_y
                
                # Update slider state
                slider.update(mouse_pos, mouse_pressed)
                
                # Draw slider label
                label = self.font_button.render(f"{label_text}: {slider.get_value()}%", True, WHITE)
                self.screen.blit(label, (slider_x, slider_y - 40))
                
                slider.draw(self.screen)
                
                # Apply volume changes in real-time
                if slider.get_value() != self.settings[key]:
                    self.settings[key] = slider.get_value()
                    self._apply_volume_settings()

            # Display mode selection
            mode_y = 380
            mode_label = self.font_button.render(self.t('settings.display_mode'), True, WHITE)
            self.screen.blit(mode_label, ((self.screen.get_width() - mode_label.get_width()) // 2, mode_y - 30))

            mode_text = self.font_button.render(display_modes[current_display_mode_index]["name"], True, WHITE)
            mode_text_x = (self.screen.get_width() - mode_text.get_width()) // 2
            self.screen.blit(mode_text, (mode_text_x, mode_y))

            # Draw navigation arrows for display mode
            left_mode_arrow_x = mode_text_x - 40
            left_mode_arrow_y = mode_y + 5
            if current_display_mode_index > 0:
                Arrow.draw_left(self.screen, left_mode_arrow_x, left_mode_arrow_y)

            right_mode_arrow_x = mode_text_x + mode_text.get_width() + 20
            right_mode_arrow_y = mode_y + 5
            if current_display_mode_index < len(display_modes) - 1:
                Arrow.draw_right(self.screen, right_mode_arrow_x, right_mode_arrow_y)

            # Resolution selection
            if current_display_mode_index != 1:
                res_y = 480
                res_label = self.font_button.render(self.t('settings.resolution'), True, WHITE)
                self.screen.blit(res_label, ((self.screen.get_width() - res_label.get_width()) // 2, res_y - 30))

                resolution_text = self.font_button.render(
                    f"{resolutions[current_resolution_index][0]}x{resolutions[current_resolution_index][1]}", 
                    True, WHITE
                )
                res_text_x = (self.screen.get_width() - resolution_text.get_width()) // 2
                self.screen.blit(resolution_text, (res_text_x, res_y))

                # Draw navigation arrows for resolution
                left_arrow_x = res_text_x - 40
                left_arrow_y = res_y + 5
                if current_resolution_index > 0:
                    Arrow.draw_left(self.screen, left_arrow_x, left_arrow_y)

                right_arrow_x = res_text_x + resolution_text.get_width() + 20
                right_arrow_y = res_y + 5
                if current_resolution_index < len(resolutions) - 1:
                    Arrow.draw_right(self.screen, right_arrow_x, right_arrow_y)

            # Update and draw buttons
            back_button.update(mouse_pos)
            reset_button.update(mouse_pos)

            back_button.draw(self.screen)
            reset_button.draw(self.screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings()
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked(mouse_pos):
                        click_sound.play()
                        self.save_settings()
                        running = False
                        
                    elif reset_button.is_clicked(mouse_pos):
                        click_sound.play()
                        self.settings = self.save_manager.reset()
                        self._apply_volume_settings()
                        current_resolution_index = 2
                        current_display_mode_index = 0
                        
                    # Display mode arrow clicks
                    elif (current_display_mode_index > 0 and 
                        Arrow.get_left_rect(left_mode_arrow_x, left_mode_arrow_y).collidepoint(mouse_pos)):
                        click_sound.play()
                        current_display_mode_index -= 1
                        self._apply_display_mode(resolutions[current_resolution_index], display_modes[current_display_mode_index])
                        
                    elif (current_display_mode_index < len(display_modes) - 1 and
                        Arrow.get_right_rect(right_mode_arrow_x, right_mode_arrow_y).collidepoint(mouse_pos)):
                        click_sound.play()
                        current_display_mode_index += 1
                        self._apply_display_mode(resolutions[current_resolution_index], display_modes[current_display_mode_index])
                        
                    # Resolution arrow clicks (only when not in borderless mode)
                    elif current_display_mode_index != 1:
                        if (current_resolution_index > 0 and
                            Arrow.get_left_rect(left_arrow_x, left_arrow_y).collidepoint(mouse_pos)):
                            click_sound.play()
                            current_resolution_index -= 1
                            self._apply_display_mode(resolutions[current_resolution_index], display_modes[current_display_mode_index])
                            
                        elif (current_resolution_index < len(resolutions) - 1 and
                            Arrow.get_right_rect(right_arrow_x, right_arrow_y).collidepoint(mouse_pos)):
                            click_sound.play()
                            current_resolution_index += 1
                            self._apply_display_mode(resolutions[current_resolution_index], display_modes[current_display_mode_index])

            pygame.display.flip()

    def _apply_display_mode(self, resolution, mode):
        """Apply display resolution and mode changes."""
        self.settings["resolution"] = resolution
        self.settings["fullscreen"] = mode["fullscreen"]
        self.settings["borderless"] = mode.get("borderless", False)
        
        # Set display mode
        if mode.get("borderless"):
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
        elif mode["fullscreen"]:
            self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(resolution)
        
        # Update resolution to actual screen size
        actual_size = self.screen.get_size()
        self.settings["resolution"] = actual_size
        self.menu_background = self.load_menu_background()
        
        pygame.display.flip()

    def language_menu(self):
        """Language selection menu."""
        running = True
        
        # Available languages
        languages = [
            {"name": self.t('language.english'), "code": "en"},
            {"name": self.t('language.portuguese'), "code": "pt"},
            {"name": self.t('language.spanish'), "code": "es"}
        ]
        
        current_language = self.settings.get("language", "en")
        
        # Language button dimensions
        button_width = 300
        button_height = 50
        button_x = (self.screen.get_width() - button_width) // 2
        start_y = 150
        spacing = 20
        
        # Create language buttons
        lang_buttons = []
        for i, lang in enumerate(languages):
            button_y = start_y + i * (button_height + spacing)
            is_selected = lang["code"] == current_language
            
            # Different colors for selected language
            color = GREEN if is_selected else GRAY
            hover_color = DARK_GREEN if not is_selected else GREEN
            
            button = TextButton(button_x, button_y, button_width, button_height, 
                              lang["name"], self.font_button, 
                              hover_color=hover_color, normal_color=color)
            lang_buttons.append((button, lang))
        
        back_button = TextButton(20, self.screen.get_height() - 70, 150, 50, 
                                self.t('language.back'), self.font_button)
        
        while running:
            self.pattern_background.draw(self.screen)
            
            mouse_pos = pygame.mouse.get_pos()
            
            title_text = self.font_title.render(self.t('language.title'), True, WHITE)
            self.screen.blit(title_text, ((self.screen.get_width() - title_text.get_width()) // 2, 50))
            
            # Update and draw language buttons
            for button, lang in lang_buttons:
                # Update button colors if language changed
                is_selected = lang["code"] == current_language
                button.normal_color = GREEN if is_selected else GRAY
                button.hover_color = DARK_GREEN if not is_selected else GREEN
                
                button.update(mouse_pos)
                button.draw(self.screen)
            
            # Update and draw back button
            back_button.update(mouse_pos)
            back_button.draw(self.screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked(mouse_pos):
                        click_sound.play()
                        running = False
                    
                    # Check language button clicks
                    for button, lang in lang_buttons:
                        if button.is_clicked(mouse_pos):
                            click_sound.play()
                            self.settings["language"] = lang["code"]
                            self.current_language = lang["code"]
                            self.save_settings()
                            current_language = lang["code"]
                            self._load_translations()
        
            pygame.display.flip()

    def level_up_menu(self, player, screen):
        """Display level-up menu with three random upgrade options."""
        running = True

        level_up_sound.play()

        # All possible upgrades
        all_upgrades = [
            {"text": self.t('level_up.fire_rate'), "upgrade": "fire_rate"},
            {"text": self.t('level_up.damage'), "upgrade": "damage"},
            {"text": self.t('level_up.health'), "upgrade": "health"},
            {"text": self.t('level_up.max_health'), "upgrade": "max_health"},
            {"text": self.t('level_up.speed'), "upgrade": "speed"},
            {"text": self.t('level_up.crit_chance'), "upgrade": "crit_chance"}
        ]

        # Randomly select 3 upgrades
        selected_upgrades = random.sample(all_upgrades, 3)

        hovered_button = None

        while running:
            self.pattern_background.draw(self.screen)

            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()

            title_text = self.font_title.render(self.t('level_up.title'), True, WHITE)
            screen.blit(title_text, (
                screen_width // 2 - title_text.get_width() // 2, 
                screen_height // 4 - 50
            ))

            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Draw upgrade option buttons
            button_rects = []
            for i, option in enumerate(selected_upgrades):
                button_width = 350
                button_height = 50
                button_x = screen_width // 2 - button_width // 2
                button_y = screen_height // 4 + 80 + i * 100

                # Check hover state
                is_hovered = button_x < mouse_x < button_x + button_width and button_y < mouse_y < button_y + button_height
                button_color = DARK_RED if is_hovered else RED

                # Draw button
                pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))

                # Draw button text
                option_text = self.font_button.render(option["text"], True, WHITE)
                screen.blit(option_text, (
                    button_x + (button_width - option_text.get_width()) // 2,
                    button_y + (button_height - option_text.get_height()) // 2
                ))

                # Play hover sound on state change
                if is_hovered and hovered_button != i:
                    if hover_sound:
                        hover_sound.play()
                    hovered_button = i
                elif not is_hovered and hovered_button == i:
                    hovered_button = None

                button_rects.append(pygame.Rect(button_x, button_y, button_width, button_height))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(mouse_x, mouse_y):
                            click_sound.play()
                            player.apply_upgrade(selected_upgrades[i]["upgrade"])
                            running = False

            pygame.display.flip()

        # Prevent immediate firing after menu closes
        player.last_shot_time = pygame.time.get_ticks()

    def skill_tree_menu(self, player, achievements):
        """Skill tree menu for upgrading character skills."""
        running = True
        selected_skill = None
        upgrade_button = None

        main_menu_music.stop()
        skill_music.play(-1)

        achievements = achievements or self.settings["achievements"]

        # Get screen dimensions for scaling
        screen_width, screen_height = self.settings["resolution"]
        scale_factor_x = screen_width / 1280
        scale_factor_y = screen_height / 720

        # Define skill node positions
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

        # Define connections between skills
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

        back_button = TextButton(20, self.screen.get_height() - 70, 150, 50, 
                                self.t('skill_tree.back'), self.font_button)
        
        def render_screen():
            """Render the complete skill tree screen."""
            # Draw pattern background
            self.pattern_background.draw(self.screen)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()

            sp_text = self.font_score.render(
                self.t('skill_tree.skill_points', points=self.settings['skill_points']), True, WHITE
            )
            self.screen.blit(sp_text, (20, 20))

            for start, end in connections:
                pygame.draw.line(
                    self.screen, WHITE, skill_positions[start], skill_positions[end], 2
                )

            # Draw skill nodes
            for skill_name, skill_data in self.settings["skills"].items():
                level = skill_data["level"]
                max_level = skill_data["max_level"]
                skill_type = skill_data.get("type", "abilities")
                x, y = skill_positions[skill_name]

                # Check if skill can be unlocked
                can_unlock = True
                requirements = skill_data.get("requires", [])
                for requirement in requirements:
                    required_skill, required_level = requirement
                    if self.settings["skills"].get(required_skill, {}).get("level", 0) < required_level:
                        can_unlock = False

                achievement = skill_data.get("achievement_required")
                if achievement and not achievements.get(achievement, False):
                    can_unlock = False

                # Determine icon and frame paths
                icon_path = (
                    f'assets/images/{skill_type}/{skill_name}.png'
                    if can_unlock or level > 0
                    else 'assets/images/locked.png'
                )
                frame_level = min(level + 1, 6 if skill_type == "stats" else 5)
                frame_path = (
                    f'assets/images/{skill_type}/{skill_type}-frame-{frame_level}.png'
                    if level > 0
                    else None
                )

                try:
                    # Highlight if hovered
                    highlight_color = RED if pygame.Rect(x - 40, y - 40, 80, 80).collidepoint(mouse_x, mouse_y) else None
                    if highlight_color:
                        pygame.draw.rect(self.screen, highlight_color, (x - 40, y - 40, 80, 80), 5)

                    # Draw frame if skill has levels
                    if frame_path:
                        frame = pygame.image.load(frame_path)
                        frame = pygame.transform.scale(frame, (80, 80))
                        self.screen.blit(frame, (x - 40, y - 40))

                    # Draw skill icon
                    icon = pygame.image.load(icon_path)
                    icon = pygame.transform.scale(icon, (60, 60))
                    self.screen.blit(icon, (x - 30, y - 30))
                except FileNotFoundError:
                    print(f"Missing image or frame for {skill_name}: {icon_path} or {frame_path}")

            # Draw selected skill details panel
            if selected_skill:
                nonlocal upgrade_button
                upgrade_button = render_selected_skill(selected_skill)

            # Draw back button
            back_button.rect.y = self.screen.get_height() - 70
            back_button.update((mouse_x, mouse_y))
            back_button.draw(self.screen)

        def render_selected_skill(skill_name):
            """Render the skill details panel for the selected skill."""
            skill_data = self.settings["skills"][skill_name]
            details_x = screen_width - int(300 * scale_factor_x)
            details_y = int(100 * scale_factor_y)

            # Check unlock requirements
            can_unlock = True
            unmet_requirements = []

            requirements = skill_data.get("requires", [])
            for prereq_skill, prereq_level in requirements:
                prereq_data = self.settings["skills"].get(prereq_skill)
                if not prereq_data or prereq_data["level"] < prereq_level:
                    translated_skill = self.t(f'skill_tree.{prereq_skill}')
                    unmet_requirements.append(f"{translated_skill} Lv {prereq_level}")
                    can_unlock = False

            achievement_required = skill_data.get("achievement_required")
            if achievement_required and not achievements.get(achievement_required, False):
                unmet_requirements.append(f"{achievement_required.replace('_', ' ').title()}")
                can_unlock = False

            # Show locked state if requirements not met
            if not can_unlock:
                try:
                    lock_icon = pygame.image.load('assets/images/locked.png')
                    lock_icon = pygame.transform.scale(lock_icon, (100, 100))
                    icon_center_x = details_x + 10 + (120 // 2)
                    self.screen.blit(lock_icon, (details_x + 20, details_y + 50))

                    name_text = self.font_button.render(self.t('skill_tree.locked'), True, WHITE)
                    self.screen.blit(name_text, (icon_center_x - name_text.get_width() // 2, details_y + 200))

                    for idx, req in enumerate(unmet_requirements):
                        req_text = self.font_button.render(req, True, RED)
                        self.screen.blit(req_text, (
                            icon_center_x - req_text.get_width() // 2,
                            details_y + 240 + idx * 40
                        ))
                except FileNotFoundError:
                    print(" Missing lock icon")
                return

            # Show skill details if unlockable
            level = skill_data["level"]
            max_level = skill_data["max_level"]
            skill_type = skill_data["type"]
            icon_path = f'assets/images/{skill_type}/{skill_name}.png'
            frame_level = min(level + 1, 6 if skill_type == "stats" else 5)
            frame_path = f'assets/images/{skill_type}/{skill_type}-frame-{frame_level}.png'

            try:
                icon = pygame.image.load(icon_path)
                icon = pygame.transform.scale(icon, (100, 100))
                self.screen.blit(icon, (details_x + 20, details_y + 50))

                if level > 0:
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (120, 120))
                    self.screen.blit(frame, (details_x + 10, details_y + 40))
            except FileNotFoundError as e:
                print(f"Missing frame or icon for {skill_name}: {e}")

            # Display skill information
            effect = skill_data["effect"]
            cost = skill_data["costs"][level] if level < max_level else self.t('skill_tree.maxed')

            translated_name = self.t(f'skill_tree.{skill_name}')
            name_text = self.font_button.render(
                f"{translated_name} {level}/{max_level}", True, WHITE
            )
            cost_text = self.font_button.render(
                self.t('skill_tree.cost', cost=cost) if level < max_level else cost, True, WHITE
            )
            effect_text = self.font_button.render(f"{effect}", True, WHITE)

            text_center_x = details_x + 10 + (120 // 2)

            self.screen.blit(name_text, (text_center_x - name_text.get_width() // 2, details_y + 200))
            self.screen.blit(cost_text, (text_center_x - cost_text.get_width() // 2, details_y + 240))
            self.screen.blit(effect_text, (text_center_x - effect_text.get_width() // 2, details_y + 280))

            # Draw upgrade button
            button_x = details_x - 27.5
            button_y = details_y + 380
            button_width, button_height = 200, 50

            button_text = self.t('skill_tree.upgrade') if level < max_level else self.t('skill_tree.maxed')

            pygame.draw.rect(self.screen, RED if level < max_level else GRAY, (button_x, button_y, button_width, button_height))

            text_surface = self.font_button.render(button_text, True, WHITE)
            self.screen.blit(
                text_surface, 
                (button_x + (button_width - text_surface.get_width()) // 2, button_y + (button_height - text_surface.get_height()) // 2)
            )

            return pygame.Rect(button_x, button_y, button_width, button_height)

        render_screen()
        pygame.display.flip()

        # Main skill tree loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check skill node clicks
                    for skill_name, (x, y) in skill_positions.items():
                        if pygame.Rect(x - 30, y - 30, 60, 60).collidepoint(mouse_x, mouse_y):
                            selected_skill = skill_name
                            render_screen()

                    # Check back button click
                    if back_button.is_clicked((mouse_x, mouse_y)):
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
                            render_screen()
                        else:
                            skill_failed_sound.play()

            pygame.display.flip()

    def store_menu(self, player, achievements):
        """Store menu for purchasing powerups."""
        running = True
        selected_powerup = None
        purchase_button = None

        # Get screen dimensions for scaling
        screen_width, screen_height = self.settings["resolution"]

        # Initialize powerups in settings if not present
        if "powerups" not in self.settings:
            self.settings["powerups"] = {
                'magnet': {'purchased': False, 'cost': 5},
                'bomb': {'purchased': False, 'cost': 10},
                'speed': {'purchased': False, 'cost': 7},
                'rage': {'purchased': False, 'cost': 7},
                'heal': {'purchased': False, 'cost': 5}
            }
            self.save_settings()

        # Powerup display information
        powerup_info = {
            'magnet': {
                'name': self.t('store.magnet_name'),
                'description': self.t('store.magnet_desc'),
                'icon': 'assets/images/powerups/magnet.png'
            },
            'heal': {
                'name': self.t('store.heal_name'),
                'description': self.t('store.heal_desc'),
                'icon': 'assets/images/powerups/heal.png'
            },
            'speed': {
                'name': self.t('store.speed_name'),
                'description': self.t('store.speed_desc'),
                'icon': 'assets/images/powerups/speed.png'
            },
            'rage': {
                'name': self.t('store.rage_name'),
                'description': self.t('store.rage_desc'),
                'icon': 'assets/images/powerups/rage.png'
            },
            'bomb': {
                'name': self.t('store.bomb_name'),
                'description': self.t('store.bomb_desc'),
                'icon': 'assets/images/powerups/bomb.png'
            }
        }

        # Powerup positions in grid layout
        powerup_positions = {
            'magnet': (150, 150),
            'heal': (350, 150),
            'speed': (150, 350),
            'rage': (350, 350),
            'bomb': (250, 550)
        }

        back_button = TextButton(20, screen_height - 70, 150, 50, 
                                self.t('store.back'), self.font_button)
        
        def render_screen():
            """Render the complete store screen."""
            nonlocal purchase_button
            
            # Draw pattern background
            self.pattern_background.draw(self.screen)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Display skill points
            sp_text = self.font_score.render(
                self.t('skill_tree.skill_points', points=self.settings['skill_points']), 
                True, WHITE
            )
            self.screen.blit(sp_text, (20, 20))

            # Store title
            title_text = self.font_title.render(self.t('store.title'), True, WHITE)
            self.screen.blit(title_text, ((screen_width - title_text.get_width()) // 2, 50))

            # Draw powerup nodes
            for powerup_id, (x, y) in powerup_positions.items():
                powerup_data = self.settings["powerups"][powerup_id]
                is_purchased = powerup_data['purchased']
                info = powerup_info[powerup_id]

                # Highlight if hovered
                node_rect = pygame.Rect(x - 40, y - 40, 80, 80)
                is_hovered = node_rect.collidepoint(mouse_x, mouse_y)
                
                if is_hovered:
                    pygame.draw.rect(self.screen, RED, node_rect, 5)

                # Draw frame
                if is_purchased:
                    try:
                        frame = pygame.image.load('assets/images/stats/stats-frame-1.png')
                        frame = pygame.transform.scale(frame, (80, 80))
                        self.screen.blit(frame, (x - 40, y - 40))
                    except FileNotFoundError:
                        pass

                # Draw icon
                try:
                    icon = pygame.image.load(info['icon'])
                    icon = pygame.transform.scale(icon, (60, 60))
                    self.screen.blit(icon, (x - 30, y - 30))
                    
                    # Draw "OWNED" badge if purchased
                    if is_purchased:
                        owned_text = self.font_credit.render("OWNED", True, GREEN)
                        self.screen.blit(owned_text, (
                            x - owned_text.get_width() // 2,
                            y + 50
                        ))
                except (pygame.error, FileNotFoundError):
                    # Draw placeholder
                    pygame.draw.rect(self.screen, GRAY, (x - 30, y - 30, 60, 60))

            # Draw selected powerup details
            if selected_powerup:
                purchase_button = render_selected_powerup(selected_powerup)

            back_button.rect.y = screen_height - 70
            back_button.update((mouse_x, mouse_y))
            back_button.draw(self.screen)

        def render_selected_powerup(powerup_id):
            """Render powerup details panel."""
            powerup_data = self.settings["powerups"][powerup_id]
            info = powerup_info[powerup_id]
            is_purchased = powerup_data['purchased']
            cost = powerup_data['cost']

            # Details panel position
            details_x = screen_width - 320
            details_y = 150

            # Draw powerup icon
            try:
                icon = pygame.image.load(info['icon'])
                icon = pygame.transform.scale(icon, (100, 100))
                self.screen.blit(icon, (details_x + 110, details_y + 20))
                
                if is_purchased:
                    frame = pygame.image.load('assets/images/stats/stats-frame-1.png')
                    frame = pygame.transform.scale(frame, (120, 120))
                    self.screen.blit(frame, (details_x + 100, details_y + 10))
            except (pygame.error, FileNotFoundError):
                # Draw placeholder
                pygame.draw.rect(self.screen, GRAY, (details_x + 110, details_y + 20, 100, 100))

            # Display powerup information
            text_center_x = details_x + 160

            name_text = self.font_button.render(info['name'], True, WHITE)
            self.screen.blit(name_text, (
                text_center_x - name_text.get_width() // 2,
                details_y + 140
            ))

            # Wrap description text
            desc_words = info['description'].split()
            lines = []
            current_line = []
            max_width = 280
            
            for word in desc_words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font_credit.render(test_line, True, WHITE)
                if test_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            desc_y = details_y + 180
            for line in lines:
                line_surface = self.font_credit.render(line, True, WHITE)
                self.screen.blit(line_surface, (
                    text_center_x - line_surface.get_width() // 2,
                    desc_y
                ))
                desc_y += 25

            # Cost display
            if not is_purchased:
                cost_text = self.font_button.render(
                    self.t('store.cost', cost=cost), True, YELLOW
                )
                self.screen.blit(cost_text, (
                    text_center_x - cost_text.get_width() // 2,
                    details_y + 300
                ))

            # Draw purchase/owned button
            button_x = details_x + 60
            button_y = details_y + 360
            button_width, button_height = 200, 50

            if is_purchased:
                button_color = GREEN
                button_text = self.t('store.owned')
            else:
                button_color = RED if self.settings['skill_points'] >= cost else GRAY
                button_text = self.t('store.purchase')

            pygame.draw.rect(self.screen, button_color, 
                           (button_x, button_y, button_width, button_height))

            text_surface = self.font_button.render(button_text, True, WHITE)
            self.screen.blit(text_surface, (
                button_x + (button_width - text_surface.get_width()) // 2,
                button_y + (button_height - text_surface.get_height()) // 2
            ))

            return pygame.Rect(button_x, button_y, button_width, button_height)

        render_screen()
        pygame.display.flip()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Check powerup node clicks
                    for powerup_id, (x, y) in powerup_positions.items():
                        if pygame.Rect(x - 40, y - 40, 80, 80).collidepoint(mouse_x, mouse_y):
                            click_sound.play()
                            selected_powerup = powerup_id
                            render_screen()
                            break

                    # Check back button
                    if back_button.is_clicked((mouse_x, mouse_y)):
                        click_sound.play()
                        running = False

                    # Check purchase button
                    if purchase_button and purchase_button.collidepoint(mouse_x, mouse_y):
                        powerup_data = self.settings["powerups"][selected_powerup]
                        
                        if not powerup_data['purchased']:
                            cost = powerup_data['cost']
                            
                            if self.settings['skill_points'] >= cost:
                                skill_bought_sound.play()
                                self.settings['skill_points'] -= cost
                                powerup_data['purchased'] = True
                                self.save_settings()
                                render_screen()
                            else:
                                skill_failed_sound.play()
                        else:
                            # Already owned
                            skill_failed_sound.play()

            pygame.display.flip()