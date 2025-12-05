import pygame

class Ability:
    """
    Base class for all abilities.
    
    Abilities can be passive (always on) or active (triggered).
    """
    def __init__(self, name, description, cost, icon_path=None, images=None, active=False):
        self.name = name  
        self.description = description  
        self.cost = cost  # Skill points to unlock
        self.icon_path = icon_path  
        self.images = images if images else []  # Animation frames
        self.active = active  # Is active?

    def draw_icon(self, screen, x, y, size=35):
        """Draw the ability icon."""
        if self.icon_path:
            try:
                icon = pygame.image.load(self.icon_path)
                icon = pygame.transform.scale(icon, (size, size))
                screen.blit(icon, (x, y))
            except FileNotFoundError:
                print(f"Icon not found for {self.name}: {self.icon_path}")
        else:
            print(f"No icon path for {self.name}")

    def activate(self):
        """Enable the ability."""
        self.active = True

    def deactivate(self):
        """Disable the ability."""
        self.active = False

    def __str__(self):
        return f"{self.name} - {self.description} (Cost: {self.cost}, Active: {self.active})"
