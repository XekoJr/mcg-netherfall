import math
import pygame
import time
from assets import *
from abilities import HealingAbility, ShieldAbility, InvincibilityAbility, BurningAbility

class Character:
    """Base class for all playable characters."""
    
    def __init__(self, fonts=None):
        # Position and movement
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 60
        self.speed = 2
        self.base_speed = 2
        
        # Health and combat stats
        self.health = 40
        self.max_health = 40
        self.base_health = 40
        
        # Progression
        self.xp = 0
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 75
        self.score = 0
        self.level_up_pending = False
        
        # Fonts
        self.fonts = fonts or {}
        self.font_credit = self.fonts.get('credit')
        self.font_score = self.fonts.get('score')
        self.font_health = self.fonts.get('health')
        
        # Hitbox
        self.hitbox_offset = (10, 10)
        self.hitbox_size = (40, 40)
        
        # Animation
        self.animation_index = 0
        self.animation_timer = 0
        self.direction = 'down'
        self.current_image = None
        self.last_move_time = time.time()
        self.animation_speed = 0.2
        self.last_animation_time = time.time()
        self.player_images = {}
        
        # Status effects and abilities
        self.status_effects = {}
        self.abilities = []
        self.invincibility_time = 0.35
        self.base_invincibility_time = 0.35
        self.last_damage_time = 0
        
        # Stat upgrades
        self.stat_upgrades = {}

    def get_hitbox(self):
        """Get character's collision rectangle."""
        return pygame.Rect(
            self.x + self.hitbox_offset[0],
            self.y + self.hitbox_offset[1],
            self.hitbox_size[0],
            self.hitbox_size[1]
        )

    def move(self):
        """Handle character movement."""
        keys = pygame.key.get_pressed()
        moving = False
        dx, dy = 0, 0

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

        # Normalize diagonal movement
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        if magnitude > 0:
            dx = (dx / magnitude) * self.speed
            dy = (dy / magnitude) * self.speed

        # Apply movement with map boundaries
        self.x = max(0, min(MAP_WIDTH - self.size, self.x + dx))
        self.y = max(0, min(MAP_HEIGHT - self.size, self.y + dy))

        # Update animation
        if moving:
            current_time = time.time()
            if current_time - self.last_animation_time >= self.animation_speed:
                self.animation_index = (self.animation_index + 1) % len(self.player_images[self.direction])
                self.last_animation_time = current_time
        else:
            self.animation_index = 0

    def attack(self, camera_x, camera_y):
        """Override this in child classes for different attack types."""
        raise NotImplementedError("Each character must implement their own attack method")

    def gain_xp(self, amount):
        """Add XP and handle leveling."""
        self.xp += amount
        self.current_xp += amount

        while self.current_xp >= self.xp_to_next_level:
            self.current_xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = round(self.xp_to_next_level * 1.2)
            self.level_up_pending = True
            return True
        return False

    def apply_upgrade(self, upgrade):
        """Apply stat upgrade."""
        if not hasattr(self, "stat_upgrades"):
            self.stat_upgrades = {}

        if upgrade in self.stat_upgrades:
            if self.stat_upgrades[upgrade] >= 6:
                return
            self.stat_upgrades[upgrade] += 1
        else:
            self.stat_upgrades[upgrade] = 1

        if upgrade == "health":
            self.health = min(self.max_health, self.health + 40)
        elif upgrade == "max_health":
            self.max_health += 25
            self.health = min(self.max_health, self.health + 20)
        elif upgrade == "speed":
            self.speed += 0.15

    def draw(self, screen):
        """Draw the character's current animation frame."""
        screen.blit(self.player_images[self.direction][self.animation_index], (self.x, self.y))
        pygame.draw.rect(screen, RED, self.get_hitbox(), 1)

    def draw_with_offset(self, screen, camera_x, camera_y):
        """Draw character with camera offset."""
        screen.blit(self.player_images[self.direction][self.animation_index], 
                   (self.x - camera_x, self.y - camera_y))

    def draw_health(self, screen):
        """Draw hearts to represent health at bottom-left."""
        if not hasattr(self, 'heart_images'):
            self.heart_images = {
                "empty": pygame.image.load('./assets/images/hp/empty.png'),
                "low": pygame.image.load('./assets/images/hp/low.png'),
                "half": pygame.image.load('./assets/images/hp/half.png'),
                "high": pygame.image.load('./assets/images/hp/high.png'),
                "full": pygame.image.load('./assets/images/hp/full.png')
            }

        heart_size = 32
        for key in self.heart_images:
            self.heart_images[key] = pygame.transform.scale(self.heart_images[key], (heart_size, heart_size))

        max_hearts = self.max_health // 20
        current_health = self.health
        margin = 10
        spacing = 5

        x = margin
        y = screen.get_height() - margin - heart_size

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

            screen.blit(heart_image, (x, y))
            current_health -= 20
            x += heart_size + spacing

    def draw_score(self, screen):
        """Draw score at top-left (HUD handles this now)."""
        if self.font_score:
            score_text = self.font_score.render(f"{self.score}", True, WHITE)
            screen.blit(score_text, (20, 25))

    def draw_xp(self, screen):
        """Draw XP bar at top-center."""
        if not hasattr(self, 'xp_bar_background'):
            self.xp_bar_background = pygame.image.load('./assets/images/xp/xp-bar.png')
            self.xp_bar_green = pygame.image.load('./assets/images/xp/xp.png')

        original_width = self.xp_bar_background.get_width()
        original_height = self.xp_bar_background.get_height()

        scaled_width = int(original_width * 0.75)
        scaled_height = int(original_height * 0.75)

        xp_bar_background_scaled = pygame.transform.scale(self.xp_bar_background, (scaled_width, scaled_height))

        green_bar_margin = 31.5
        max_green_width = scaled_width - 2 * green_bar_margin

        xp_percentage = self.current_xp / self.xp_to_next_level
        green_bar_width = int(max_green_width * xp_percentage)

        green_bar_height = int(scaled_height * 0.475)
        xp_bar_green_scaled = pygame.transform.scale(self.xp_bar_green, (green_bar_width, green_bar_height))

        screen_width = screen.get_width()
        bar_x = (screen_width - scaled_width) // 2
        bar_y = 20

        screen.blit(xp_bar_background_scaled, (bar_x, bar_y))

        green_bar_y = bar_y + (scaled_height - green_bar_height) // 2
        screen.blit(xp_bar_green_scaled, (bar_x + green_bar_margin, green_bar_y))

        level_text = self.font_credit.render(str(self.level), True, WHITE)
        text_width, text_height = level_text.get_size()

        text_x = bar_x + (scaled_width - text_width) // 2
        text_y = bar_y + (scaled_height - text_height) // 2

        screen.blit(level_text, (text_x, text_y))

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
                ability.level = invincibility_level

    def apply_status(self, name, duration, tick_interval=None, tick_damage=None, enemy=None):
        """Apply a status effect to the character."""
        self.status_effects[name] = {
            "duration": duration,
            "start_time": pygame.time.get_ticks(),
            "tick_interval": tick_interval,
            "tick_damage": tick_damage,
            "last_tick": 0,
            "enemy": enemy
        }

    def update_status_effects(self):
        """Update status effects, applying tick damage."""
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
        """Draw status effects and ability icons."""
        icon_size = 35
        frame_size = 45
        spacing = 5

        margin = 10
        x = screen.get_width() - frame_size - margin
        y = screen.get_height() - frame_size - margin

        status_frame_image = pygame.image.load('./assets/images/status/debuff-frame-2.png')
        status_frame_image = pygame.transform.scale(status_frame_image, (frame_size, frame_size))
        status_frame_boss_image = pygame.image.load('./assets/images/status/debuff-frame-boss.png')
        status_frame_boss_image = pygame.transform.scale(status_frame_boss_image, (frame_size, frame_size))

        icons_to_draw = []

        # Draw active abilities
        for ability in self.abilities:
            if isinstance(ability, ShieldAbility) and not ability.ready:
                continue
            
            if ability.active:
                ability.draw_icon(screen, x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2, icon_size)

                level = getattr(ability, 'level', 1)
                frame_path = f'./assets/images/abilities/abilities-frame-{min(level, 5)}.png'
                try:
                    frame = pygame.image.load(frame_path)
                    frame = pygame.transform.scale(frame, (frame_size, frame_size))
                    screen.blit(frame, (x, y))
                except FileNotFoundError:
                    print(f"[DEBUG] Frame file not found for level {level}.")

                x -= frame_size + spacing
                if x - frame_size < margin:
                    x = screen.get_width() - frame_size - margin
                    y -= frame_size + spacing

        # Draw stat upgrades
        for stat, count in self.stat_upgrades.items():
            if count > 6:
                continue

            icon_path = f'./assets/images/stats/{stat}.png'
            try:
                icon = pygame.image.load(icon_path)
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                screen.blit(icon, (x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2))

                frame_path = f'./assets/images/stats/stats-frame-{count}.png'
                frame = pygame.image.load(frame_path)
                frame = pygame.transform.scale(frame, (frame_size, frame_size))
                screen.blit(frame, (x, y))

                x -= frame_size + spacing
                if x - frame_size < margin:
                    x = screen.get_width() - frame_size - margin
                    y -= frame_size + spacing

            except FileNotFoundError:
                print(f"[DEBUG] Missing icon or frame for stat {stat}, level {count}")

        # Draw status effects
        for status_name, status_data in self.status_effects.items():
            try:
                icon = pygame.image.load(f'./assets/images/status/{status_name}.png')
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                if status_data.get("enemy") == "Boss":
                    frame_image = status_frame_boss_image
                else:
                    frame_image = status_frame_image
                icons_to_draw.append(("status", status_name, icon, frame_image))
            except FileNotFoundError:
                print(f"[DEBUG] Status icon for {status_name} not found.")

        for item_type, item_name, icon, frame_image in icons_to_draw:
            screen.blit(icon, (x + (frame_size - icon_size) // 2, y + (frame_size - icon_size) // 2))
            screen.blit(frame_image, (x, y))
            x -= frame_size + spacing

            if x - frame_size < margin:
                x = screen.get_width() - frame_size - margin
                y -= frame_size + spacing