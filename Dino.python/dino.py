import pygame
import os
import random
import json

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 600, 300
FPS = 60
GRAVITY = 0.5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run - Upgraded Version")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NIGHT = (15, 15, 40)  # Dark blue night sky

# Resource loader
def load_image(name, size=None):
    path = os.path.join(r'Dino.python\resources', name)
    image = pygame.image.load(path).convert()
    image.set_colorkey(BLACK)
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_sprite_sheet(name, cols, rows, size=None):
    path = os.path.join(r'Dino.python\resources', name)
    sheet = pygame.image.load(path).convert()
    sheet.set_colorkey(BLACK)
    sprite_width = sheet.get_width() // cols
    sprite_height = sheet.get_height() // rows
    sprites = []
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x * sprite_width, y * sprite_height, sprite_width, sprite_height)
            image = pygame.Surface(rect.size).convert()
            image.blit(sheet, (0, 0), rect)
            image.set_colorkey(BLACK)
            if size:
                image = pygame.transform.scale(image, size)
            sprites.append(image)
    return sprites

# Dino class
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = load_sprite_sheet('dino.png', 5, 1, (44, 47))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, HEIGHT - 30)
        self.velocity = 0
        self.is_jumping = False

    def update(self):
        if self.is_jumping:
            self.velocity += GRAVITY
            self.rect.y += self.velocity
            if self.rect.bottom >= HEIGHT - 30:
                self.rect.bottom = HEIGHT - 30
                self.is_jumping = False
                self.velocity = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity = -12

# Cactus obstacle
class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = load_image('cactus-small.png', (40, 40))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + 10, HEIGHT - 30)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Ground that loops
class Ground(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = load_image('ground.png', (WIDTH, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, HEIGHT - 30)
        self.x1 = 0
        self.x2 = self.rect.width
        self.speed = speed

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 <= -self.rect.width:
            self.x1 = self.rect.width
        if self.x2 <= -self.rect.width:
            self.x2 = self.rect.width

    def draw(self, surface):
        surface.blit(self.image, (self.x1, self.rect.y))
        surface.blit(self.image, (self.x2, self.rect.y))

# Cloud for background
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('cloud.png', (90, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH, random.randint(30, HEIGHT // 2))

    def update(self):
        self.rect.x -= 1
        if self.rect.right < 0:
            self.kill()

# High Score persistence
def load_high_score():
    if os.path.exists("highscore.json"):
        with open("highscore.json", "r") as f:
            return json.load(f).get("high_score", 0)
    return 0

def save_high_score(score):
    with open("highscore.json", "w") as f:
        json.dump({"high_score": score}, f)

# Main game loop
def main():
    font = pygame.font.SysFont(None, 28)
    running = True
    game_over = False
    score = 0
    high_score = load_high_score()
    spawn_timer = 0
    speed = 5
    bg_color = list(WHITE)
    day_to_night = True

    # Initialize game objects
    dino = Dino()
    ground = Ground(speed)
    cacti = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(dino)

    def reset_game():
        nonlocal dino, ground, cacti, clouds, all_sprites, score, spawn_timer, speed, bg_color, day_to_night
        dino = Dino()
        speed = 5
        ground = Ground(speed)
        cacti = pygame.sprite.Group()
        clouds = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group(dino)
        score = 0
        spawn_timer = 0
        bg_color = list(WHITE)
        day_to_night = True

    def draw_restart_button():
        button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 20, 120, 40)
        pygame.draw.rect(screen, BLACK, button_rect, border_radius=5)
        text = font.render("Restart", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        return button_rect

    while running:
        clock.tick(FPS)
        screen.fill(bg_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    dino.jump()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        reset_game()
                        game_over = False

        if not game_over:
            # Update game elements
            all_sprites.update()
            cacti.update()
            clouds.update()
            ground.update()

            # Spawn cactus
            spawn_timer += 1
            if spawn_timer > 90:
                cactus = Cactus(speed)
                cacti.add(cactus)
                all_sprites.add(cactus)
                spawn_timer = 0

            # Random cloud
            if random.randint(1, 120) == 1:
                cloud = Cloud()
                clouds.add(cloud)

            # Collision
            if pygame.sprite.spritecollideany(dino, cacti):
                if score > high_score:
                    high_score = score
                    save_high_score(int(high_score))
                game_over = True

            # Score & Speed increase
            score += 0.1
            if int(score) % 50 == 0:
                speed += 0.002  # gradually faster
                ground.speed = speed
                for cactus in cacti:
                    cactus.speed = speed

            # Day/Night cycle
            if day_to_night:
                for i in range(3):
                    bg_color[i] = max(bg_color[i] - 0.05, NIGHT[i])
                if bg_color[0] <= NIGHT[0] + 5:
                    day_to_night = False
            else:
                for i in range(3):
                    bg_color[i] = min(bg_color[i] + 0.05, WHITE[i])
                if bg_color[0] >= WHITE[0] - 5:
                    day_to_night = True

        # Drawing
        clouds.draw(screen)
        ground.draw(screen)
        all_sprites.draw(screen)

        # Draw score and high score
        score_surface = font.render(f"Score: {int(score)}  High Score: {int(high_score)}", True, BLACK)
        screen.blit(score_surface, (10, 10))

        # If game over, show Game Over text and Restart button
        if game_over:
            over_text = font.render("Game Over", True, BLACK)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
            restart_button = draw_restart_button()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
