import pygame
import game
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, veloc):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface((10,10))
        pygame.draw.circle(self.image, game.Color.red, (5,5), 5)

        self.rect = self.image.get_rect()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        self.veloc = veloc

    def update(self):
        self.rect.centerx += self.veloc[0]
        self.rect.centery += self.veloc[1]
