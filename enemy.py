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

        # Other important variables set here
        self.speed = 3
        self.veloc = [0,0]

        # The path index
        self.pathind = 0
        self.path = []

        # If killed, will drop this amount
        self.cost = self.hp*5

    def update(self, gs):
        if self.hp <= 0:
            gs.money += self.cost
            self.kill()
        ''' Old sin-wave pathing NO_MORE
        self.rect.centerx += 1
        self.rect.centery = 150*math.sin(math.radians(self.rect.centerx%360))+200
        '''
        # New point-to-point pathing system
        if self.pathind == 0:
            # If you have just spawned in, then take you to the location pls
            self.rect.center = self.path[self.pathind]
            self.pathind += 1
        else:
            # If you are doing the pathing, add to center coords
            self.veloc = game.getVeloc(self.rect.center, self.path[self.pathind], self.speed)

        # If you have just hit the next path part, update index
        if self.rect.collidepoint(self.path[self.pathind]) and self.pathind < len(self.path)-1:
            self.rect.center = self.path[self.pathind]
            self.pathind += 1

        self.rect.centerx += self.veloc[0]
        self.rect.centery += self.veloc[1]

        # Blit the green health bar
        self.image = pygame.surface.Surface((30,30))
        pygame.draw.circle(self.image, game.Color.white, (15,15), 15)
        pygame.draw.rect(self.image, game.Color.green, (0,0,self.rect.w*self.hp/self.maxhp,5))

    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx, self.rect.centery))