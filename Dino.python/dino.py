import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 600, 300
FPS = 60
GRAVITY = 0.5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run - Clean Version")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = WHITE

# Resource loader
def load_image(name, size=None):
    path = os.path.join('resources', name)
    image = pygame.image.load(path).convert()
    image.set_colorkey(BLACK)
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_sprite_sheet(name, cols, rows, size=None):
    path = os.path.join('resources', name)
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
    def __init__(self):
        super().__init__()
        self.image = load_image('cactus-small.png', (40, 40))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + 10, HEIGHT - 30)

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

# Ground that loops
class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('ground.png', (WIDTH, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, HEIGHT - 30)
        self.x1 = 0
        self.x2 = self.rect.width

    def update(self):
        self.x1 -= 5
        self.x2 -= 5
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

# Main game loop
def main():
    dino = Dino()
    ground = Ground()
    cacti = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(dino)

    score = 0
    font = pygame.font.SysFont(None, 28)

    running = True
    spawn_timer = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                dino.jump()

        all_sprites.update()
        cacti.update()
        clouds.update()
        ground.update()

        # Spawn cactus
        spawn_timer += 1
        if spawn_timer > 90:
            cactus = Cactus()
            cacti.add(cactus)
            all_sprites.add(cactus)
            spawn_timer = 0

        # Random cloud
        if random.randint(1, 120) == 1:
            cloud = Cloud()
            clouds.add(cloud)

        # Collision
        if pygame.sprite.spritecollideany(dino, cacti):
            running = False

        # Draw
        screen.fill(BG_COLOR)
        clouds.draw(screen)
        ground.draw(screen)
        all_sprites.draw(screen)

        # Score
        score += 0.1
        score_surface = font.render(f"Score: {int(score)}", True, BLACK)
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
