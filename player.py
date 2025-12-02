import math
import pygame
import time
from abilities.__init__ import *
from assets import *

class Player:
    def __init__(self, fonts=None):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 60
        self.speed = 2  
        self.health = 40
        self.max_health = 40
        self.xp = 0  # Total XP collected
        self.level = 1  # Starting level
        self.current_xp = 0  # XP toward the next level
        self.xp_to_next_level = 75  # Initial XP required to level up
        self.last_shot_time = 0
        self.score = 0
        self.level_up_pending = False
        self.fire_rate = 1200
        self.projectile_damage = 6  # Base projectile damage
        self.crit_chance = 0  # Critical hit chance (percentage)
        self.crit_damage = 1.5  # Multiplier for critical hit damage
        self.fonts = fonts or {}
        self.font_credit = self.fonts.get('credit')
        self.font_score = self.fonts.get('score')
        self.font_health = self.fonts.get('health')

        # Base player stats
        self.base_speed = 2
        self.base_health = 40
        self.base_projectile_damage = 6
        self.base_fire_rate = 1200
        self.base_crit_chance = 0
        self.base_crit_damage = 1.5

        self.base_invincibility_time = 0.35  # Default invincibility duration in seconds
        self.stat_upgrades = {}  # Track stat upgrades

        # Hitbox configuration
        self.hitbox_offset = (10, 10)  # Offset from the sprite's top-left corner
        self.hitbox_size = (40, 40)  # Width and height of the hitbox

        # Player animation
        self.player_images = {
            'down': [pygame.image.load(f'./assets/images/player/down/{i}.png') for i in range(4)],
            'up': [pygame.image.load(f'./assets/images/player/up/{i}.png') for i in range(4)],
            'left': [pygame.image.load(f'./assets/images/player/left/{i}.png') for i in range(4)],
            'right': [pygame.image.load(f'./assets/images/player/right/{i}.png') for i in range(4)],
        }

        # Resize images to the desired size
        self.player_images = {direction: [pygame.transform.scale(image, (self.size, self.size)) for image in images]
                              for direction, images in self.player_images.items()}

        # Animation control variables
        self.animation_index = 0
        self.animation_timer = 0  # Timer to control image switching
        # Initialize player direction (default "down")
        self.direction = 'down'
        self.current_image = self.player_images[self.direction][self.animation_index]  # Initial image
        self.last_move_time = time.time()  # Time tracking for animations

        # Control animation speed in seconds
        self.animation_speed = 0.2  # Swap image every 0.2 seconds
        self.last_animation_time = time.time()  # Last animation time

        # Status effects
        self.status_effects = {}

        # Abilities
        self.abilities = []  # List of active abilities
        self.invincibility_time = 0.35  # Default invincibility duration in seconds
        self.last_damage_time = 0

    def get_hitbox(self):
        """Returns the player's hitbox as a pygame.Rect."""
        return pygame.Rect(
            self.x + self.hitbox_offset[0],
            self.y + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1]
        )

    def move(self):
        """Update player movement while respecting map boundaries."""
        keys = pygame.key.get_pressed()
        moving = False  # Check if the player is moving

        # Initialize movement deltas
        dx, dy = 0, 0

        # Check for movement in each direction
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
            self.direction = 'up'
            moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
            self.direction = 'down'
            moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
            self.direction = 'left'
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            self.direction = 'right'
            moving = True

        # Normalize movement for diagonal movement
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        if magnitude > 0:  # Avoid division by zero
            dx = (dx / magnitude) * self.speed
            dy = (dy / magnitude) * self.speed

        # Apply movement, respecting map boundaries
        self.x = max(0, min(MAP_WIDTH - self.size, self.x + dx))
        self.y = max(0, min(MAP_HEIGHT - self.size, self.y + dy))

        # Update animation only if moving
        if moving:
            current_time = time.time()
            if current_time - self.last_animation_time >= self.animation_speed:
                self.animation_index = (self.animation_index + 1) % len(self.player_images[self.direction])
                self.last_animation_time = current_time
        else:
            self.animation_index = 0  # Reset animation to the first frame when not moving

    def gain_xp(self, amount):
        """Add XP and handle leveling up."""
        self.xp += amount
        self.current_xp += amount

        while self.current_xp >= self.xp_to_next_level:
            self.current_xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = round(self.xp_to_next_level * 1.2)
            self.level_up_pending = True  # Set flag to trigger level-up menu
            return True
        return False

    def apply_upgrade(self, upgrade):
        """Apply the chosen upgrade."""
        if not hasattr(self, "stat_upgrades"):
            self.stat_upgrades = {}  # Initialize the dictionary if not present

        # Initialize or increment the upgrade count
        if upgrade in self.stat_upgrades:
            if self.stat_upgrades[upgrade] >= 6:
                return  # Ignore the upgrade if it's already at the max level
            self.stat_upgrades[upgrade] += 1
        else:
            self.stat_upgrades[upgrade] = 1

        if upgrade == "fire_rate":
            self.fire_rate = max(200, self.fire_rate * 0.8)  # Faster shooting
        elif upgrade == "damage":
            self.projectile_damage = int(self.projectile_damage * 1.3)  # Increase damage
        elif upgrade == "health":
            self.health = min(self.max_health, self.health + 40)  # Restore health
        elif upgrade == "max_health":
            self.max_health += 25  # Increase max health
            self.health = min(self.max_health, self.health + 20)
        elif upgrade == "speed":
            self.speed += 0.15  # Increase movement speed
        elif upgrade == "crit_chance":
            self.crit_chance = min(200, self.crit_chance + 5)  # Increase crit chance (cap at 200%)

    def draw(self, screen):
        """Draw the player's current animation frame on the screen."""
        screen.blit(self.player_images[self.direction][self.animation_index], (self.x, self.y))

        # Debugging: Draw the hitbox as a rectangle
        pygame.draw.rect(screen, RED, self.get_hitbox(), 1)  # Outline the hitbox in red

    def draw_health(self, screen):
        """Draw hearts to represent health at the bottom-left corner of the screen."""
        # Load heart images (ensure these are loaded only once)
        if not hasattr(self, 'heart_images'):
            self.heart_images = {
                "empty": pygame.image.load('./assets/images/hp/empty.png'),
                "low": pygame.image.load('./assets/images/hp/low.png'),
                "half": pygame.image.load('./assets/images/hp/half.png'),
                "high": pygame.image.load('./assets/images/hp/high.png'),
                "full": pygame.image.load('./assets/images/hp/full.png')
            }

        # Resize heart images if needed
        heart_size = 32  # Adjust size as necessary
        for key in self.heart_images:
            self.heart_images[key] = pygame.transform.scale(self.heart_images[key], (heart_size, heart_size))

        # Calculate number of hearts based on max HP
        max_hearts = self.max_health // 20
        current_health = self.health
        margin = 10  # Margin from the edges
        spacing = 5  # Space between hearts

        # Position to start drawing hearts
        x = margin
        y = screen.get_height() - margin - heart_size

        # Draw each heart based on the current health
        for i in range(max_hearts):
            if current_health >= 20:
                heart_image = self.heart_images["full"]
            elif current_health >= 15:
                heart_image = self.heart_images["high"]
            elif current_health >= 10:
                heart_image = self.heart_images["half"]
            elif current_health >= 5:
                heart_image = self.heart_images["low"]
            else:
                heart_image = self.heart_images["empty"]

            # Blit the heart image
            screen.blit(heart_image, (x, y))

            # Reduce current health for the next heart
            current_health -= 20

            # Adjust x for the next heart
            x += heart_size + spacing

    def draw_score(self, screen):
        """Draw the player's score in the top-right corner."""
        if self.font_score:
            score_text = self.font_score.render(f"{self.score}", True, WHITE)
            score_x = screen.get_width() - score_text.get_width() - 20  # Position relative to the right edge
            screen.blit(score_text, (score_x, 25))
        else:
            # Fallback if font is not available
            print("[DEBUG] font_score not available for rendering score")

    def draw_xp(self, screen):
        """Draw XP bar at the top-center of the screen with the player's level in the middle."""
        # Load the XP bar images (ensure these are loaded only once)
        if not hasattr(self, 'xp_bar_background'):
            self.xp_bar_background = pygame.image.load('./assets/images/xp/xp-bar.png')
            self.xp_bar_green = pygame.image.load('./assets/images/xp/xp.png')

        # Reduce the size of the bars
        original_width = self.xp_bar_background.get_width()
        original_height = self.xp_bar_background.get_height()

        # Scale the bars to 75% of their original size
        scaled_width = int(original_width * 0.75)
        scaled_height = int(original_height * 0.75)

        # Resize the background bar
        xp_bar_background_scaled = pygame.transform.scale(self.xp_bar_background, (scaled_width, scaled_height))

        # Add left and right margin to the green bar
        green_bar_margin = 31.5  # Pixels on both sides
        max_green_width = scaled_width - 2 * green_bar_margin

        # Calculate the XP percentage and determine the green bar's width
        xp_percentage = self.current_xp / self.xp_to_next_level
        green_bar_width = int(max_green_width * xp_percentage)

        # Resize the green bar with adjusted height
        green_bar_height = int(scaled_height * 0.475)  # Make the green bar 50% of the background's height
        xp_bar_green_scaled = pygame.transform.scale(self.xp_bar_green, (green_bar_width, green_bar_height))

        # Calculate the top-center position for the bars
        screen_width = screen.get_width()
        bar_x = (screen_width - scaled_width) // 2
        bar_y = 20  # Small margin from the top

        # Draw the grey background bar
        screen.blit(xp_bar_background_scaled, (bar_x, bar_y))

        # Center the green bar vertically within the grey background
        green_bar_y = bar_y + (scaled_height - green_bar_height) // 2

        # Draw the green bar on top, respecting the margin
        screen.blit(xp_bar_green_scaled, (bar_x + green_bar_margin, green_bar_y))

        # Render the player's level in the middle of the XP bar
        level_text = self.font_credit.render(str(self.level), True, WHITE)
        text_width, text_height = level_text.get_size()

        # Center the text within the background bar
        text_x = bar_x + (scaled_width - text_width) // 2
        text_y = bar_y + (scaled_height - text_height) // 2

        # Draw the level text
        screen.blit(level_text, (text_x, text_y))

    def draw_with_offset(self, screen, camera_x, camera_y):
        """Draw player with camera offset."""
        screen.blit(self.player_images[self.direction][self.animation_index], (self.x - camera_x, self.y - camera_y))

    def apply_stat_upgrades(self, skills):
        """Apply stat upgrades based on skill levels."""
        if "max_health" in skills:
            level = skills["max_health"].get("level", 0)
            self.max_health = self.base_health + (20 * level)
            self.health = self.max_health

        if "speed" in skills:
            level = skills["speed"].get("level", 0)
            self.speed = self.base_speed + (0.2 * level)  # Example: +0.2 speed per level

        # Add other stats similarly
        if "damage" in skills:
            level = skills["damage"].get("level", 0)
            self.projectile_damage = self.base_projectile_damage + (2 * level)  # Example: +2 damage per level

        if "fire_rate" in skills:
            level = skills["fire_rate"].get("level", 0)
            self.fire_rate = self.base_fire_rate - (50 * level)

        if "crit_chance" in skills:
            level = skills["crit_chance"].get("level", 0)
            self.crit_chance = self.base_crit_chance + (2.5 * level)

        if "crit_damage" in skills:
            level = skills["crit_damage"].get("level", 0)
            self.crit_damage = self.crit_damage + (0.15 * level)

    def initialize_abilities(self, skills):
        """Initialize abilities based on skill levels."""
        for skill_name, skill_data in skills.items():
            if skill_data["type"] == "abilities" and skill_data["level"] > 0:
                if skill_name == "heal":
                    self.abilities.append(HealingAbility())
                elif skill_name == "shield":
                    self.abilities.append(ShieldAbility())
                elif skill_name == "invincibility":
                    self.abilities.append(InvincibilityAbility())
                
                # Activate the ability
                self.abilities[-1].active = True

    def apply_skill_upgrades(self, skills):
        """Update abilities based on skill upgrades."""
        for ability in self.abilities:
            if isinstance(ability, BurningAbility):
                burn_damage_level = skills.get("burn_damage", {}).get("level", 0)
                burn_duration_level = skills.get("burn_duration", {}).get("level", 0)
                ability.update_attributes(burn_damage_level, burn_duration_level)
            elif isinstance(ability, HealingAbility):
                heal_level = skills.get("heal", {}).get("level", 0)
                ability.heal_amount = 5 + (2 * heal_level)
                ability.cooldown = max(10 - heal_level, 3)
            elif isinstance(ability, ShieldAbility):
                shield_level = skills.get("shield", {}).get("level", 0)
                ability.cooldown = max(30 - (5 * shield_level), 10)
            elif isinstance(ability, InvincibilityAbility):
                invincibility_level = skills.get("invincibility", {}).get("level", 0)
                ability.duration = 0.5 + (0.5 * invincibility_level)
            if isinstance(ability, InvincibilityAbility):
                invincibility_level = skills.get("invincibility", {}).get("level", 0)
                ability.level = invincibility_level
                
    def apply_status(self, name, duration, tick_interval=None, tick_damage=None, enemy=None):
        """Apply a status effect to the player."""
        self.status_effects[name] = {
            "duration": duration,
            "start_time": pygame.time.get_ticks(),
            "tick_interval": tick_interval,
            "tick_damage": tick_damage,
            "last_tick": 0,
            "enemy": enemy
        }

    def update_status_effects(self):
        """Update the status effects, applying tick damage if applicable."""
        current_time = pygame.time.get_ticks()
        expired_effects = []
        for name, effect in self.status_effects.items():
            if current_time - effect["start_time"] > effect["duration"] * 1000:
                expired_effects.append(name)
            elif effect["tick_interval"] and effect["tick_damage"]:
                if current_time - effect["last_tick"] >= effect["tick_interval"] * 1000:
                    self.health -= effect["tick_damage"]
                    hurt_sound.play()
                    effect["last_tick"] = current_time

        for effect in expired_effects:
            del self.status_effects[effect]

    def update_abilities_effects(self):
        """Update passive effects from abilities."""
        for ability in self.abilities:
            if ability.active:
                if isinstance(ability, HealingAbility):
                    ability.heal(self)

    def draw_status_abilities_icons(self, screen):
        """Draw status effect and ability icons with frames at the top-left corner of the screen in a unified order."""
        # Define the size and spacing for the icons
        icon_size = 35
        frame_size = 45  # Slightly larger to encompass the icon
        spacing = 5

        # Calculate the starting position at the top-left corner
        margin = 10  # Margin from the screen edges
        x = screen.get_width() - frame_size - margin
        y = screen.get_height() - frame_size - margin # Start from the top-left corner

        # Load frame images (do this once to avoid repeated loading)
        status_frame_image = pygame.image.load('./assets/images/status/debuff-frame-2.png')
        status_frame_image = pygame.transform.scale(status_frame_image, (frame_size, frame_size))
        status_frame_boss_image = pygame.image.load('./assets/images/status/debuff-frame-boss.png')
        status_frame_boss_image = pygame.transform.scale(status_frame_boss_image, (frame_size, frame_size))
        ability_frame_images = {}

        # Preload ability frames dynamically for levels 1-5
        for level in range(1, 6):
            frame_path = f'./assets/images/abilities/abilities-frame-{level}.png'
            try:
                frame_image = pygame.image.load(frame_path)
                frame_image = pygame.transform.scale(frame_image, (frame_size, frame_size))
                ability_frame_images[level] = frame_image
            except FileNotFoundError:
                print(f"[DEBUG] Missing ability frame for level {level}.")

        # Combine abilities and statuses into a unified list
        icons_to_draw = []

        # Add active abilities to the list
        for ability in self.abilities:
            
            if isinstance(ability, ShieldAbility)and not ability.ready:
                    continue  # Skip further processing for this ability
            
            if ability.active:
                # Preload the ability's icon
                # Draw the ability icon
                ability.draw_icon(screen, x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2, icon_size)

                # Draw the ability frame based on its level
                level = getattr(ability, 'level', 1)  # Assume level 1 if not defined
                frame_path = f'./assets/images/abilities/abilities-frame-{min(level, 5)}.png'
                try:
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (frame_size, frame_size))
                    screen.blit(frame, (x, y))
                except FileNotFoundError:
                    print(f"[DEBUG] Frame file not found for level {level}.")

                # Adjust position for the next icon
                x -= frame_size + spacing  # Move left
                if x - frame_size < margin:  # If there's no more space in the row
                    x = screen.get_width() - frame_size - margin  # Reset to the right edge
                    y -= frame_size + spacing  # Move upward

        # Draw stat upgrades
        for stat, count in self.stat_upgrades.items():
            if count > 6:
                continue  # Skip displaying stats that have reached the maximum level

            icon_path = f'./assets/images/stats/{stat}.png'
            try:
                # Load the icon for the stat
                icon = pygame.image.load(icon_path)
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                screen.blit(icon, (x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2))

                # Draw a frame corresponding to the stat level
                frame_path = f'./assets/images/stats/stats-frame-{count}.png'
                frame = pygame.image.load(frame_path)
                frame = pygame.transform.scale(frame, (frame_size, frame_size))
                screen.blit(frame, (x, y))

                x -= frame_size + spacing  # Move left
                if x - frame_size < margin:  # If there's no more space in the row
                    x = screen.get_width() - frame_size - margin  # Reset to the right edge
                    y -= frame_size + spacing  # Move upward

            except FileNotFoundError:
                print(f"[DEBUG] Missing icon or frame for stat {stat}, level {count}")

        # Add active status effects to the list
        for status_name, status_data in self.status_effects.items():
            try:
                # Load the icon dynamically for the status
                icon = pygame.image.load(f'./assets/images/status/{status_name}.png')
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                if status_data.get("enemy") == "Boss":
                    frame_image = status_frame_boss_image
                else:
                    frame_image = status_frame_image
                icons_to_draw.append(("status", status_name, icon, frame_image))
            except FileNotFoundError:
                print(f"[DEBUG] Status icon for {status_name} not found.")

        # Draw icons in the unified order
        for item_type, item_name, icon, frame_image in icons_to_draw:
            # Draw the icon inside the frame
            screen.blit(icon, (x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2))
            # Draw the frame
            screen.blit(frame_image, (x, y))
            # Adjust position for the next icon
            x -= frame_size + spacing  # Move left

            # If the row is full, move to the row above
            if x - frame_size < margin:  # If there's no more space in the row
                x = screen.get_width() - frame_size - margin  # Reset to the right edge
                y -= frame_size + spacing  # Move upward