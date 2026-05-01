import pygame
import settings


class Ship:
    def __init__(self):
        self.width = settings.SHIP_WIDTH
        self.height = settings.SHIP_HEIGHT
        self.x = settings.SCREEN_WIDTH // 2
        self.y = settings.SCREEN_HEIGHT - 80
        self.speed = settings.SHIP_SPEED
        self.color = settings.GALAXY_SILVER
        self.bullet_color = settings.BRIGHT_SILVER
        
        # Heavy attack charging
        self.is_charging = False
        self.charge_level = 0
        self.max_charge = settings.CHARGE_MAX
        self.is_charged = False
        
        # Health
        self.max_health = settings.SHIP_MAX_HEALTH
        self.health = self.max_health
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.width // 2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < settings.SCREEN_WIDTH - self.width // 2:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.height // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < settings.SCREEN_HEIGHT - self.height // 2:
            self.y += self.speed
    
    def start_charge(self):
        self.is_charging = True
    
    def update_charge(self):
        if self.is_charging and self.charge_level < self.max_charge:
            self.charge_level += 1
        if self.charge_level >= self.max_charge:
            self.is_charged = True
    
    def release_charge(self):
        if self.is_charged:
            self.is_charged = False
            self.charge_level = 0
            self.is_charging = False
            return True  # Fire heavy attack
        self.charge_level = 0
        self.is_charging = False
        self.is_charged = False
        return False
    
    def draw(self, surface):
        # Draw ship body (triangle shape)
        points = [
            (self.x, self.y - self.height // 2),  # Top
            (self.x - self.width // 2, self.y + self.height // 2),  # Bottom left
            (self.x, self.y + self.height // 4),  # Bottom center
            (self.x + self.width // 2, self.y + self.height // 2),  # Bottom right
        ]
        pygame.draw.polygon(surface, self.color, points, 2)
        pygame.draw.polygon(surface, settings.BRIGHT_SILVER, points[:3], 1)
        
        # Draw engine glow
        pygame.draw.circle(surface, settings.LIGHT_BLUE, (self.x, self.y + self.height // 2), 5)
        
        # Draw charge indicator
        if self.is_charging:
            charge_width = (self.charge_level / self.max_charge) * 50
            charge_color = settings.ORANGE if not self.is_charged else (255, 0, 0)
            pygame.draw.rect(surface, charge_color, 
                           (self.x - 25, self.y + self.height // 2 + 10, charge_width, 5))
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.height // 2 - 15
        
        # Background (red)
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health (green)
        health_width = (self.health / self.max_health) * bar_width
        if health_width > 0:
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        # Border
        pygame.draw.rect(surface, settings.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)