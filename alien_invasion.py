import pygame
import random
import math
import settings
import ship as ship_module
import bullet as bullet_module

# Initialize pygame
pygame.init()

# Create screen
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption(settings.SCREEN_TITLE)

# Set clock for 60 FPS
clock = pygame.time.Clock()

# Generate stars for galaxy effect
stars = []
for _ in range(settings.STAR_COUNT):
    star = {
        'x': random.randint(0, settings.SCREEN_WIDTH),
        'y': random.randint(0, settings.SCREEN_HEIGHT),
        'size': random.randint(settings.STAR_MIN_SIZE, settings.STAR_MAX_SIZE),
        'color': random.choice([settings.WHITE, settings.YELLOW, settings.LIGHT_BLUE]),
        'brightness': random.randint(settings.STAR_MIN_BRIGHTNESS, settings.STAR_MAX_BRIGHTNESS)
    }
    stars.append(star)


# Alien class (kept in main file for now, or could be moved to alien.py)
class Alien:
    def __init__(self, x, y, pattern_type=0):
        self.width = settings.ALIEN_WIDTH
        self.height = settings.ALIEN_HEIGHT
        self.x = x
        self.y = y
        self.start_x = x
        self.pattern_type = pattern_type
        self.pattern_offset = 0
        self.speed = settings.ALIEN_SPEED
        self.color = settings.ALIEN_GREEN if pattern_type == 0 else settings.ALIEN_RED
        
        # Health
        self.max_health = settings.ALIEN_MAX_HEALTH
        self.health = self.max_health
        
    def update(self):
        self.pattern_offset += 1
        
        if self.pattern_type == 0:
            # Horizontal zigzag pattern
            self.x = self.start_x + math.sin(self.pattern_offset * 0.05) * 100
        elif self.pattern_type == 1:
            # Simple left-right sweep
            self.x = self.start_x + math.sin(self.pattern_offset * 0.03) * 80
        elif self.pattern_type == 2:
            # Figure-8 pattern
            self.x = self.start_x + math.sin(self.pattern_offset * 0.04) * 60
            self.y += math.sin(self.pattern_offset * 0.08) * 0.5
        
        # Keep within screen bounds
        self.x = max(self.width, min(settings.SCREEN_WIDTH - self.width, self.x))
    
    def draw(self, surface):
        # Draw alien body (oval shape)
        pygame.draw.ellipse(surface, self.color, 
                          (self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height), 2)
        
        # Draw eyes
        pygame.draw.circle(surface, (255, 255, 0), (self.x - 8, self.y - 5), 4)
        pygame.draw.circle(surface, (255, 255, 0), (self.x + 8, self.y - 5), 4)
        pygame.draw.circle(surface, (0, 0, 0), (self.x - 8, self.y - 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 8, self.y - 5), 2)
        
        # Draw antennae
        pygame.draw.line(surface, self.color, (self.x - 10, self.y - self.height // 2),
                        (self.x - 15, self.y - self.height), 2)
        pygame.draw.line(surface, self.color, (self.x + 10, self.y - self.height // 2),
                        (self.x + 15, self.y - self.height), 2)
        pygame.draw.circle(surface, self.color, (self.x - 15, self.y - self.height), 3)
        pygame.draw.circle(surface, self.color, (self.x + 15, self.y - self.height), 3)


# Enemy bullet class
class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = settings.ENEMY_BULLET_WIDTH
        self.height = settings.ENEMY_BULLET_HEIGHT
        self.speed = settings.ENEMY_BULLET_SPEED
        self.color = settings.ENEMY_BULLET
        self.damage = settings.ENEMY_BULLET_DAMAGE
    
    def move(self):
        self.y += self.speed
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                        (self.x - self.width // 2, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 150, 150),
                        (self.x - 2, self.y, 2, self.height))
    
    def is_off_screen(self):
        return self.y > settings.SCREEN_HEIGHT


# Create ship
player_ship = ship_module.Ship()

# Bullets list
bullets = []

# Create aliens in top third
aliens = []
for i in range(5):
    aliens.append(Alien(150 + i * 150, 80, i % 3))

# Enemy bullets list
enemy_bullets = []

# Auto-fire timer
auto_fire_counter = 0

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # Release charge - fire heavy attack if charged
                if player_ship.release_charge():
                    bullets.append(bullet_module.Bullet(player_ship.x, player_ship.y - player_ship.height // 2, is_heavy=True))
    
    # Get pressed keys
    keys = pygame.key.get_pressed()
    
    # Handle charging
    if keys[pygame.K_SPACE]:
        player_ship.start_charge()
    player_ship.update_charge()
    
    # Move ship
    player_ship.move(keys)
    
    # Auto-fire bullets (constant firing)
    auto_fire_counter += 1
    if auto_fire_counter >= settings.AUTO_FIRE_DELAY:
        auto_fire_counter = 0
        # Don't auto-fire if fully charged (wait for release)
        if not player_ship.is_charged:
            bullets.append(bullet_module.Bullet(player_ship.x, player_ship.y - player_ship.height // 2, is_heavy=False))
    
    # Move bullets and check collision with aliens
    for bullet in bullets[:]:
        bullet.move()
        if bullet.is_off_screen():
            bullets.remove(bullet)
        else:
            # Check collision with aliens
            for alien in aliens[:]:
                if (abs(bullet.x - alien.x) < (bullet.width + alien.width) // 2 and
                    bullet.y < alien.y + alien.height // 2 and
                    bullet.y + bullet.height > alien.y - alien.height // 2):
                    alien.health -= bullet.damage
                    bullets.remove(bullet)
                    if alien.health <= 0:
                        aliens.remove(alien)
                    break
    
    # Update aliens
    for alien in aliens:
        alien.update()
    
    # Alien fires projectiles (slow rate)
    if random.randint(1, settings.ALIEN_FIRE_RATE) == 1:
        firing_alien = random.choice(aliens)
        enemy_bullets.append(EnemyBullet(firing_alien.x, firing_alien.y + firing_alien.height // 2))
    
    # Move enemy bullets and check collision with ship
    for eb in enemy_bullets[:]:
        eb.move()
        if eb.is_off_screen():
            enemy_bullets.remove(eb)
        else:
            # Check collision with ship
            if (abs(eb.x - player_ship.x) < (eb.width + player_ship.width) // 2 and
                eb.y < player_ship.y + player_ship.height // 2 and
                eb.y + eb.height > player_ship.y - player_ship.height // 2):
                player_ship.health -= eb.damage
                enemy_bullets.remove(eb)
                if player_ship.health <= 0:
                    running = False  # Game over
    
    # Draw midnight purple background
    screen.fill(settings.MIDNIGHT_PURPLE)
    
    # Draw stars for galaxy effect
    for star in stars:
        brightness = (star['brightness'] + random.randint(-10, 10)) % 256
        brightness = max(100, min(255, brightness))
        color = list(star['color'])
        color = tuple(min(255, c * brightness // 255) for c in star['color'])
        pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])
    
    # Draw ship
    player_ship.draw(screen)
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)
    
    # Draw aliens
    for alien in aliens:
        alien.draw(screen)
    
    # Draw enemy bullets
    for eb in enemy_bullets:
        eb.draw(screen)
    
    # Update display
    pygame.display.flip()
    
    # Maintain 60 FPS
    clock.tick(settings.FPS)

# Quit pygame
pygame.quit()
        self.y = SCREEN_HEIGHT - 80
        self.speed = 5
        self.color = GALAXY_SILVER
        self.bullet_color = BRIGHT_SILVER
        
        # Heavy attack charging
        self.is_charging = False
        self.charge_level = 0
        self.max_charge = 60  # 1 second at 60 FPS
        self.is_charged = False
        
        # Health
        self.max_health = 10
        self.health = self.max_health
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.width // 2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width // 2:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.height // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height // 2:
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
        pygame.draw.polygon(surface, BRIGHT_SILVER, points[:3], 1)
        
        # Draw engine glow
        pygame.draw.circle(surface, LIGHT_BLUE, (self.x, self.y + self.height // 2), 5)
        
        # Draw charge indicator
        if self.is_charging:
            charge_width = (self.charge_level / self.max_charge) * 50
            charge_color = ORANGE if not self.is_charged else (255, 0, 0)
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
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)


# Bullet class
class Bullet:
    def __init__(self, x, y, is_heavy=False):
        self.x = x
        self.y = y
        self.is_heavy = is_heavy
        if is_heavy:
            self.width = 10
            self.height = 30
            self.speed = 12
            self.color = ORANGE
            self.damage = 2  # Double damage
        else:
            self.width = 4
            self.height = 15
            self.speed = 10
            self.color = BRIGHT_SILVER
            self.damage = 1
    
    def move(self):
        self.y -= self.speed
    
    def draw(self, surface):
        if self.is_heavy:
            # Heavy bullet with glow effect
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.width // 2, self.y, self.width, self.height))
            pygame.draw.rect(surface, YELLOW, 
                           (self.x - 2, self.y, 4, self.height))
        else:
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.width // 2, self.y, self.width, self.height))
    
    def is_off_screen(self):
        return self.y < -self.height


# Alien class
class Alien:
    def __init__(self, x, y, pattern_type=0):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.start_x = x
        self.pattern_type = pattern_type
        self.pattern_offset = 0
        self.speed = 2
        self.color = ALIEN_GREEN if pattern_type == 0 else ALIEN_RED
        
        # Health
        self.max_health = 10
        self.health = self.max_health
        
    def update(self):
        self.pattern_offset += 1
        
        if self.pattern_type == 0:
            # Horizontal zigzag pattern
            self.x = self.start_x + math.sin(self.pattern_offset * 0.05) * 100
        elif self.pattern_type == 1:
            # Simple left-right sweep
            self.x = self.start_x + math.sin(self.pattern_offset * 0.03) * 80
        elif self.pattern_type == 2:
            # Figure-8 pattern
            self.x = self.start_x + math.sin(self.pattern_offset * 0.04) * 60
            self.y += math.sin(self.pattern_offset * 0.08) * 0.5
        
        # Keep within screen bounds
        self.x = max(self.width, min(SCREEN_WIDTH - self.width, self.x))
    
    def draw(self, surface):
        # Draw alien body (oval shape)
        pygame.draw.ellipse(surface, self.color, 
                          (self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height), 2)
        
        # Draw eyes
        pygame.draw.circle(surface, (255, 255, 0), (self.x - 8, self.y - 5), 4)
        pygame.draw.circle(surface, (255, 255, 0), (self.x + 8, self.y - 5), 4)
        pygame.draw.circle(surface, (0, 0, 0), (self.x - 8, self.y - 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 8, self.y - 5), 2)
        
        # Draw antennae
        pygame.draw.line(surface, self.color, (self.x - 10, self.y - self.height // 2),
                        (self.x - 15, self.y - self.height), 2)
        pygame.draw.line(surface, self.color, (self.x + 10, self.y - self.height // 2),
                        (self.x + 15, self.y - self.height), 2)
        pygame.draw.circle(surface, self.color, (self.x - 15, self.y - self.height), 3)
        pygame.draw.circle(surface, self.color, (self.x + 15, self.y - self.height), 3)


# Enemy bullet class
class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 12
        self.speed = 4
        self.color = ENEMY_BULLET
        self.damage = 1
    
    def move(self):
        self.y += self.speed
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                        (self.x - self.width // 2, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 150, 150),
                        (self.x - 2, self.y, 2, self.height))
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT


# Create ship
ship = Ship()

# Bullets list
bullets = []

# Create aliens in top third
aliens = []
for i in range(5):
    aliens.append(Alien(150 + i * 150, 80, i % 3))

# Enemy bullets list
enemy_bullets = []

# Auto-fire timer
AUTO_FIRE_DELAY = 15  # Frames between auto-shots
auto_fire_counter = 0

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # Release charge - fire heavy attack if charged
                if ship.release_charge():
                    bullets.append(Bullet(ship.x, ship.y - ship.height // 2, is_heavy=True))
    
    # Get pressed keys
    keys = pygame.key.get_pressed()
    
    # Handle charging
    if keys[pygame.K_SPACE]:
        ship.start_charge()
    ship.update_charge()
    
    # Move ship
    ship.move(keys)
    
    # Auto-fire bullets (constant firing)
    auto_fire_counter += 1
    if auto_fire_counter >= AUTO_FIRE_DELAY:
        auto_fire_counter = 0
        # Don't auto-fire if fully charged (wait for release)
        if not ship.is_charged:
            bullets.append(Bullet(ship.x, ship.y - ship.height // 2, is_heavy=False))
    
    # Move bullets and check collision with aliens
    for bullet in bullets[:]:
        bullet.move()
        if bullet.is_off_screen():
            bullets.remove(bullet)
        else:
            # Check collision with aliens
            for alien in aliens[:]:
                if (abs(bullet.x - alien.x) < (bullet.width + alien.width) // 2 and
                    bullet.y < alien.y + alien.height // 2 and
                    bullet.y + bullet.height > alien.y - alien.height // 2):
                    alien.health -= bullet.damage
                    bullets.remove(bullet)
                    if alien.health <= 0:
                        aliens.remove(alien)
                    break
    
    # Update aliens
    for alien in aliens:
        alien.update()
    
    # Alien fires projectiles (slow rate - every 90 frames)
    if random.randint(1, 90) == 1:
        firing_alien = random.choice(aliens)
        enemy_bullets.append(EnemyBullet(firing_alien.x, firing_alien.y + firing_alien.height // 2))
    
    # Move enemy bullets and check collision with ship
    for eb in enemy_bullets[:]:
        eb.move()
        if eb.is_off_screen():
            enemy_bullets.remove(eb)
        else:
            # Check collision with ship
            if (abs(eb.x - ship.x) < (eb.width + ship.width) // 2 and
                eb.y < ship.y + ship.height // 2 and
                eb.y + eb.height > ship.y - ship.height // 2):
                ship.health -= eb.damage
                enemy_bullets.remove(eb)
                if ship.health <= 0:
                    running = False  # Game over
    
    # Draw midnight purple background
    screen.fill(MIDNIGHT_PURPLE)
    
    # Draw stars for galaxy effect
    for star in stars:
        brightness = (star['brightness'] + random.randint(-10, 10)) % 256
        brightness = max(100, min(255, brightness))
        color = list(star['color'])
        color = tuple(min(255, c * brightness // 255) for c in star['color'])
        pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])
    
    # Draw ship
    ship.draw(screen)
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)
    
    # Draw aliens
    for alien in aliens:
        alien.draw(screen)
    
    # Draw enemy bullets
    for eb in enemy_bullets:
        eb.draw(screen)
    
    # Update display
    pygame.display.flip()
    
    # Maintain 60 FPS
    clock.tick(FPS)

# Quit pygame
pygame.quit()