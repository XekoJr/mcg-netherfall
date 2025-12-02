"""Utility functions and reusable UI components for the game."""

import pygame
import math
import time
import sys

# Import colors and sounds from assets - these are in parent directory
from assets import (
    WHITE, BLACK, GRAY, DARK_GRAY, RED, DARK_RED, 
    GREEN, DARK_GREEN, hover_sound, click_sound
)


class LoadingSpinner:
    """Animated loading spinner component."""
    
    @staticmethod
    def draw(screen, x, y, radius=30, thickness=4, angle=0):
        """
        Draw a spinning circle animation.
        
        Args:
            screen: Pygame surface to draw on
            x, y: Center position of the spinner
            radius: Radius of the spinner
            thickness: Line thickness
            angle: Current rotation angle (0-360)
        """
        num_segments = 8
        segment_angle = 360 / num_segments
        
        for i in range(num_segments):
            segment_start = (angle + i * segment_angle) % 360
            opacity = int(255 * (i / num_segments))
            
            arc_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            
            start_angle = math.radians(segment_start)
            end_angle = math.radians(segment_start + segment_angle)
            
            arc_color = (255, 255, 255, opacity)
            
            for thickness_offset in range(thickness):
                current_radius = radius - thickness_offset
                points = []
                steps = 10
                for step in range(steps + 1):
                    angle_step = start_angle + (end_angle - start_angle) * (step / steps)
                    px = radius + 5 + int(current_radius * math.cos(angle_step))
                    py = radius + 5 + int(current_radius * math.sin(angle_step))
                    points.append((px, py))
                
                if len(points) > 1:
                    pygame.draw.lines(arc_surface, arc_color, False, points, 2)
            
            screen.blit(arc_surface, (x - radius - 5, y - radius - 5))


class Arrow:
    """Arrow component for navigation."""
    
    @staticmethod
    def draw_left(screen, x, y, size=20, color=WHITE):
        """Draw a left-pointing arrow."""
        pygame.draw.polygon(screen, color, [
            (x + size, y),
            (x, y + size // 2),
            (x + size, y + size)
        ])
    
    @staticmethod
    def draw_right(screen, x, y, size=20, color=WHITE):
        """Draw a right-pointing arrow."""
        pygame.draw.polygon(screen, color, [
            (x, y),
            (x + size, y + size // 2),
            (x, y + size)
        ])
    
    @staticmethod
    def get_left_rect(x, y, size=20):
        """Get the bounding rect for a left arrow."""
        return pygame.Rect(x, y, size, size)
    
    @staticmethod
    def get_right_rect(x, y, size=20):
        """Get the bounding rect for a right arrow."""
        return pygame.Rect(x, y, size, size)


class IconButton:
    """Icon-based button component."""
    
    def __init__(self, x, y, size, icon_path, hover_color=DARK_GRAY, normal_color=GRAY):
        """
        Initialize an icon button.
        
        Args:
            x, y: Position
            size: Button size (square)
            icon_path: Path to icon image
            hover_color: Color when hovered
            normal_color: Normal color
        """
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.hover_color = hover_color
        self.normal_color = normal_color
        self.hovered = False
        self.was_hovered = False
        
        # Debug counter
        self.debug_update_count = 0
        self.debug_sound_play_count = 0
        
        # Load icon
        try:
            self.icon = pygame.image.load(icon_path)
            self.icon = pygame.transform.scale(self.icon, (int(size * 0.6), int(size * 0.6)))
        except pygame.error as e:
            print(f"[WARNING] Failed to load icon: {icon_path} - {e}")
            self.icon = None
    
    def update(self, mouse_pos):
        """Update button hover state."""
        self.debug_update_count += 1
        
        prev_hovered = self.hovered  # Store BEFORE checking collision
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Play sound only when transitioning from not-hovered to hovered
        if self.hovered and not prev_hovered:
            self.debug_sound_play_count += 1
            if hover_sound:
                hover_sound.play()
    
    def draw(self, screen):
        """Draw the icon button."""
        color = self.hover_color if self.hovered else self.normal_color
        
        # Draw background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw icon
        if self.icon:
            icon_x = self.rect.x + (self.size - self.icon.get_width()) // 2
            icon_y = self.rect.y + (self.size - self.icon.get_height()) // 2
            screen.blit(self.icon, (icon_x, icon_y))
    
    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)


class TextButton:
    """Text-based button component with hover effects."""
    
    def __init__(self, x, y, width, height, text, font, 
                 hover_color=DARK_RED, normal_color=RED, text_color=WHITE):
        """
        Initialize a text button.
        
        Args:
            x, y: Position
            width, height: Button dimensions
            text: Button text
            font: Pygame font object
            hover_color: Color when hovered
            normal_color: Normal color
            text_color: Text color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hover_color = hover_color
        self.normal_color = normal_color
        self.text_color = text_color
        self.hovered = False
        self.was_hovered = False
        
        # Debug counter
        self.debug_update_count = 0
        self.debug_sound_play_count = 0
    
    def update(self, mouse_pos):
        """Update button hover state."""
        self.debug_update_count += 1
        
        prev_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Play sound only when entering hover state
        if self.hovered and not prev_hovered:
            self.debug_sound_play_count += 1
            if hover_sound:
                hover_sound.play()
    
    def draw(self, screen):
        """Draw the text button."""
        color = self.hover_color if self.hovered else self.normal_color
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)


class Panel:
    """Panel component with border."""
    
    @staticmethod
    def draw(screen, x, y, width, height, bg_color=(20, 20, 20), border_color=WHITE, border_width=3):
        """
        Draw a panel with background and border.
        
        Args:
            screen: Pygame surface
            x, y: Position
            width, height: Panel dimensions
            bg_color: Background color
            border_color: Border color
            border_width: Border thickness
        """
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        pygame.draw.rect(screen, border_color, (x, y, width, height), border_width)


class RepeatingBackground:
    """Repeating pattern background component."""
    
    def __init__(self, pattern_path="./assets/images/background/background-pattern.png", fallback_color=BLACK):
        """
        Initialize repeating background.
        
        Args:
            pattern_path: Path to pattern image (leave None for placeholder)
            fallback_color: Fallback color if image not found
        """
        self.pattern = None
        self.fallback_color = fallback_color
        
        if pattern_path:
            try:
                self.pattern = pygame.image.load(pattern_path)
            except pygame.error as e:
                print(f"[WARNING] Failed to load pattern: {pattern_path} - {e}")
    
    def draw(self, screen):
        """Draw the repeating background."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if self.pattern:
            # Calculate how many tiles we need
            pattern_width = self.pattern.get_width()
            pattern_height = self.pattern.get_height()
            
            tiles_x = (screen_width // pattern_width) + 2
            tiles_y = (screen_height // pattern_height) + 2
            
            # Draw repeating pattern
            for ty in range(tiles_y):
                for tx in range(tiles_x):
                    screen.blit(self.pattern, (tx * pattern_width, ty * pattern_height))
        else:
            # Fallback to solid color
            screen.fill(self.fallback_color)


class Slider:
    """Horizontal slider component."""
    
    def __init__(self, x, y, width, height, min_val=0, max_val=100, current_val=50):
        """
        Initialize a slider.
        
        Args:
            x, y: Position
            width, height: Slider dimensions
            min_val: Minimum value
            max_val: Maximum value
            current_val: Current value
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.dragging = False
    
    def update(self, mouse_pos, mouse_pressed):
        """Update slider state."""
        if mouse_pressed and self.rect.collidepoint(mouse_pos):
            self.dragging = True
        
        if not mouse_pressed:
            self.dragging = False
        
        if self.dragging:
            # Calculate value based on mouse position
            relative_x = mouse_pos[0] - self.rect.x
            relative_x = max(0, min(relative_x, self.rect.width))
            self.current_val = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)
    
    def draw(self, screen, bg_color=GRAY, fill_color=GREEN):
        """Draw the slider."""
        # Draw background
        pygame.draw.rect(screen, bg_color, self.rect)
        
        # Draw fill
        fill_width = int((self.current_val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, fill_color, fill_rect)
    
    def get_value(self):
        """Get current slider value."""
        return int(self.current_val)


def show_loading_screen(screen, image_path=None, duration=1.5):
    """
    Show a loading screen with spinning animation.
    
    Args:
        screen: Pygame surface
        image_path: Path to loading image (optional)
        duration: Minimum display duration in seconds
    """
    bg_color = (5, 7, 6)
    
    # Load loading image
    loading_image = None
    image_x, image_y = 0, 0
    
    if image_path:
        try:
            loading_image = pygame.image.load(image_path)
            img_rect = loading_image.get_rect()
            screen_rect = screen.get_rect()
            
            scale = min(screen_rect.width / img_rect.width, screen_rect.height / img_rect.height)
            new_width = int(img_rect.width * scale * 0.8)
            new_height = int(img_rect.height * scale * 0.8)
            
            loading_image = pygame.transform.scale(loading_image, (new_width, new_height))
            
            image_x = (screen.get_width() - new_width) // 2
            image_y = (screen.get_height() - new_height) // 2
        except pygame.error as e:
            print(f"[WARNING] Failed to load loading screen image: {e}")
            loading_image = None
    
    # Spinner position
    circle_margin = 50
    circle_radius = 30
    circle_x = screen.get_width() - circle_margin - circle_radius
    circle_y = screen.get_height() - circle_margin - circle_radius
    
    start_time = time.time()
    clock = pygame.time.Clock()
    angle = 0
    
    while time.time() - start_time < duration:
        screen.fill(bg_color)
        
        if loading_image:
            screen.blit(loading_image, (image_x, image_y))
        
        LoadingSpinner.draw(screen, circle_x, circle_y, circle_radius, 4, angle)
        
        angle = (angle + 5) % 360
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        clock.tick(60)