import pygame
import math
import game

class Tower(pygame.sprite.Sprite):
    '''
    The tower with the money displayed
    Only used in menus
    '''
    def __init__(self, rmanager, data, (x,y)):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = rmanager

        self.image = self.rmanager.sprites[data['sprite']].copy()
        self.orgimage = self.image.copy()
        self.cost = data['cost']
        self.dmg = data['dmg']
        self.rate = data['rate']
        self.range = data['range']
        self.sprite = data['sprite']
        self.name = data['name']
        self.shotveloc = data['shotveloc']

        costlbl = self.rmanager.fonts['monospace'].render('$'+str(self.cost), True, game.Color.green)
        #self.image.blit(costlbl, (25-costlbl.get_rect().w/2,25-costlbl.get_rect().h/2))
        self.image.blit(costlbl, (0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def getDist(a, b):
    return math.sqrt((a.centerx-b.centerx)**2+(a.centery-b.centery)**2)

class rTower(pygame.sprite.Sprite):
    '''
    The tower displayed that does the actual fighting
    Used in-game only
    '''
    def __init__(self, t):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = t.rmanager

        self.image = self.rmanager.sprites[t.sprite].copy()
        self.cost = t.cost
        self.dmg = t.dmg
        self.rate = t.rate
        self.range = t.range
        self.sprite = t.sprite
        self.name = t.name
        self.shotveloc = t.shotveloc

        self.rect = self.image.get_rect()
        self.rect.x = t.rect.x
        self.rect.y = t.rect.y

        self.reloading = 0
        self.shoot = None

        '''
        Targeting:
        0: First (in range)
        1: Last (in range)
        2: Closest (to tower)
        3: Strongest (in range)

        Defaults to First (0)
        '''
        self.target = 0

    def update(self, enemies):
        if self.reloading <= 0:
            # If you have finished reloading
            # Get list of enemies in range
            enems_rng = []
            for e in enemies.sprites():
                dist = getDist(e.rect, self.rect)
                if dist <= self.range:
                    enems_rng.append([e, dist])

            # Check for shooting target priority
            if len(enems_rng) >= 1:
                if self.target == 0:
                    # Shoot the first
                    self.shoot = [enems_rng[0][0].rect.centerx,enems_rng[0][0].rect.centery]
                self.reloading = self.rate
        else:
            self.reloading -= 1
