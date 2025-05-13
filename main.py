
import pygame


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.x = x
        self.y = y
        self.image = pygame.Surface([20, 20])
        self.image.fill((0, 0, 255))
        self.rect = pygame.Rect(x, y, 20, 20)

    def update(self):
        if not pygame.sprite.spritecollideany(self, vertical_borders):
            self.rect = self.rect.move(0, 1)

    def remo(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def f(self, m):
        self.rect = self.rect.move(m, 0)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1):
        super().__init__(all_sprites)
        self.add(vertical_borders)
        self.image = pygame.Surface([50, 10])
        self.image.fill((125, 125, 125))
        self.rect = pygame.Rect(x1, y1, 50, 10)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Платформы')
    size = width, height = 400, 300
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))
    running = True
    all_sprites = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    clock = pygame.time.Clock()
    b = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Border(event.pos[0], event.pos[1])
                elif event.button == 3:
                    if not b:
                        a0 = Ball(event.pos[0], event.pos[1])
                        b = not b
                    else:
                        a0.remo(event.pos[0], event.pos[1])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    a0.f(10)
                if event.key == pygame.K_LEFT:
                    a0.f(-10)
        all_sprites.update()
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(20)