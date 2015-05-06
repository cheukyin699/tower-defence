import pygame
import game
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp=1):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface((30,30))
        pygame.draw.circle(self.image, game.Color.white, (15,15), 15)

        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 200

        # Set hit-points
        self.hp = hp

    def update(self):
        if self.hp <= 0:
            self.kill()
        self.rect.centerx += 1
        self.rect.centery = 200*math.sin(math.radians(self.rect.centerx%360))+200
