import pygame
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

        costlbl = self.rmanager.fonts['monospace'].render('$'+str(self.cost), True, game.Color.yellow)
        self.image.blit(costlbl, (25-costlbl.get_rect().w/2,25-costlbl.get_rect().h/2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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

        self.rect = self.image.get_rect()
        self.rect.x = t.rect.x
        self.rect.y = t.rect.y
        
        '''
        Targeting:
        0: First (in range)
        1: Last (in range)
        2: Closest (to tower)
        3: Strongest (in range)

        Defaults to First (0)
        '''
        self.target = 0
