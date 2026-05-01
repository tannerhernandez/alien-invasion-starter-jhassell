import pygame
import settings


class Bullet:
    def __init__(self, x, y, is_heavy=False):
        self.x = x
        self.y = y
        self.is_heavy = is_heavy
        if is_heavy:
            self.width = settings.BULLET_WIDTH_HEAVY
            self.height = settings.BULLET_HEIGHT_HEAVY
            self.speed = settings.BULLET_SPEED_HEAVY
            self.color = settings.ORANGE
            self.damage = settings.BULLET_DAMAGE_HEAVY
        else:
            self.width = settings.BULLET_WIDTH_NORMAL
            self.height = settings.BULLET_HEIGHT_NORMAL
            self.speed = settings.BULLET_SPEED_NORMAL
            self.color = settings.BRIGHT_SILVER
            self.damage = settings.BULLET_DAMAGE_NORMAL
    
    def move(self):
        self.y -= self.speed
    
    def draw(self, surface):
        if self.is_heavy:
            # Heavy bullet with glow effect
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.width // 2, self.y, self.width, self.height))
            pygame.draw.rect(surface, settings.YELLOW, 
                           (self.x - 2, self.y, 4, self.height))
        else:
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.width // 2, self.y, self.width, self.height))
    
    def is_off_screen(self):
        return self.y < -self.height