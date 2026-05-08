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

# Start menu fonts and button
font = pygame.font.SysFont(None, 48)
level_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)
button_width, button_height = 300, 80
start_button_rect = pygame.Rect(
    (settings.SCREEN_WIDTH - button_width) // 2,
    (settings.SCREEN_HEIGHT - button_height) // 2,
    button_width,
    button_height
)

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
        
    def update(self):
        self.x += self.speed * alien_direction
    
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

# Alien formation helper

def create_alien_formation(level, speed):
    alien_count = 5 + (level - 1)
    formation = []
    cols = 6
    x_start = 100
    x_spacing = 110
    y_start = 80
    y_spacing = 70
    for i in range(alien_count):
        row = i // cols
        col = i % cols
        x = x_start + col * x_spacing
        y = y_start + row * y_spacing
        alien = Alien(x, y, i % 3)
        alien.speed = speed
        formation.append(alien)
    return formation

level = 1
alien_speed = settings.ALIEN_SPEED
score = 0

def reset_game():
    global player_ship, bullets, enemy_bullets, aliens, alien_direction, auto_fire_counter, level, alien_speed, score
    player_ship = ship_module.Ship()
    bullets = []
    enemy_bullets = []
    level = 1
    alien_speed = settings.ALIEN_SPEED
    score = 0
    alien_direction = 1
    auto_fire_counter = 0
    aliens = create_alien_formation(level, alien_speed)

# Create aliens in top third
aliens = create_alien_formation(level, alien_speed)

# Start menu draw helper

def draw_start_menu():
    screen.fill(settings.MIDNIGHT_PURPLE)
    for star in stars:
        brightness = (star['brightness'] + random.randint(-10, 10)) % 256
        brightness = max(100, min(255, brightness))
        color = tuple(min(255, c * brightness // 255) for c in star['color'])
        pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])

    pygame.draw.rect(screen, settings.ALIEN_GREEN, start_button_rect)
    pygame.draw.rect(screen, settings.WHITE, start_button_rect, 4)
    start_text = font.render("START GAME", True, settings.MIDNIGHT_PURPLE)
    start_text_rect = start_text.get_rect(center=start_button_rect.center)
    screen.blit(start_text, start_text_rect)
    pygame.display.flip()

# Show start menu until the button is clicked
running = True
menu_active = True
while menu_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu_active = False
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button_rect.collidepoint(event.pos):
                menu_active = False

    draw_start_menu()
    clock.tick(settings.FPS)

# Enemy bullets list
enemy_bullets = []

# Shared alien formation direction
alien_direction = 1

# Auto-fire timer
auto_fire_counter = 0

game_over = False

# Main game loop
while running:
    if not game_over:
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
                        aliens.remove(alien)
                        bullets.remove(bullet)
                        score += 100
                        break

        # Advance level when all aliens are destroyed
        if not aliens:
            level += 1
            alien_direction = 1
            alien_speed = settings.ALIEN_SPEED + (level - 1)
            aliens = create_alien_formation(level, alien_speed)

        # Move alien formation together and reverse at screen edges
        if aliens:
            current_speed = aliens[0].speed
            left_edge = min(alien.x - alien.width // 2 for alien in aliens)
            right_edge = max(alien.x + alien.width // 2 for alien in aliens)
            next_left = left_edge + current_speed * alien_direction
            next_right = right_edge + current_speed * alien_direction
            if next_left < 0 or next_right > settings.SCREEN_WIDTH:
                alien_direction *= -1
                for alien in aliens:
                    alien.y += settings.ALIEN_HEIGHT
        for alien in aliens:
            alien.update()

        # Check if any alien reached the bottom
        for alien in aliens:
            if alien.y > settings.SCREEN_HEIGHT:
                game_over = True
                break

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
                        game_over = True

        # Draw midnight purple background
        screen.fill(settings.MIDNIGHT_PURPLE)

        # Draw stars for galaxy effect
        for star in stars:
            brightness = (star['brightness'] + random.randint(-10, 10)) % 256
            brightness = max(100, min(255, brightness))
            color = list(star['color'])
            color = tuple(min(255, c * brightness // 255) for c in star['color'])
            pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])

        # Draw score and level indicators
        score_text = level_font.render(f"SCORE: {score}", True, settings.WHITE)
        screen.blit(score_text, (10, 10))
        level_text = level_font.render(f"LEVEL {level}", True, settings.WHITE)
        screen.blit(level_text, (10, 40))

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
    else:
        screen.fill(settings.MIDNIGHT_PURPLE)
        for star in stars:
            brightness = (star['brightness'] + random.randint(-10, 10)) % 256
            brightness = max(100, min(255, brightness))
            color = list(star['color'])
            color = tuple(min(255, c * brightness // 255) for c in star['color'])
            pygame.draw.circle(screen, color, (star['x'], star['y']), star['size'])

        game_over_text = game_over_font.render("GAME OVER", True, settings.WHITE)
        final_score_text = level_font.render(f"FINAL SCORE: {score}", True, settings.WHITE)
        restart_text = level_font.render("PRESS R TO RESTART", True, settings.WHITE)

        center_x = settings.SCREEN_WIDTH // 2
        screen.blit(game_over_text, game_over_text.get_rect(center=(center_x, 220)))
        screen.blit(final_score_text, final_score_text.get_rect(center=(center_x, 300)))
        screen.blit(restart_text, restart_text.get_rect(center=(center_x, 360)))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_over = False
        clock.tick(settings.FPS)

# Quit pygame
pygame.quit()
