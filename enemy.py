import pygame
import math
import game

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp=1, cost=1):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface((30,30))
        pygame.draw.circle(self.image, game.Color.white, (15,15), 15)

        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 200

        # Set hit-points
        self.maxhp = hp
        self.hp = hp

        # If killed, will drop this amount
        self.cost = self.hp*5

    def update(self, gs):
        if self.hp <= 0:
            gs.money += self.cost
            self.kill()
        self.rect.centerx += 1
        self.rect.centery = 150*math.sin(math.radians(self.rect.centerx%360))+200

        # Blit the green health bar
        self.image = pygame.surface.Surface((30,30))
        pygame.draw.circle(self.image, game.Color.white, (15,15), 15)
        pygame.draw.rect(self.image, game.Color.green, (0,0,self.rect.w*self.hp/self.maxhp,5))
