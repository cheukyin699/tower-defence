import pygame
import game



class bEnemy(pygame.sprite.Sprite):
    def __init__(self, rmanager, data, pos):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = rmanager

        self.image = self.rmanager.sprites[data['sprite']].copy()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.orgimage = self.image.copy()
        self.cost = data['cost']
        self.eco = data['eco']
        self.sprite = data['sprite']
        self.name = data['name']
        self.hp = data['hp']
        self.maxhp = self.hp
        self.speed = data['speed']
        self.eid = data['eid']

        costlbl = self.rmanager.fonts['monospace'].render('$'+str(self.cost), True, game.Color.green)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        costlbl = pygame.transform.scale(costlbl, (self.rect.w, costlbl.get_rect().h))
        self.image.blit(costlbl, (0,0))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, e):
        pygame.sprite.Sprite.__init__(self)
        
        self.rmanager = e.rmanager

        self.image = self.rmanager.sprites[self.rmanager.data['enemies'][e.eid]['sprite']].copy()
        self.sprite = e.sprite

        self.rect = self.image.get_rect()
        self.rect.centerx = 0
        self.rect.centery = 200

        # Set hit-points
        self.maxhp = e.hp
        self.hp = e.hp

        # Other important variables set here
        self.speed = e.speed
        self.veloc = [0,0]

        # The path index
        self.pathind = 0
        self.path = []

        # If killed, will drop this amount
        self.cost = self.hp

    def update(self, gs):
        if self.hp <= 0:
            if self.child != None:
                datas = self.rmanager.data['enemies'][self.child]
                be = get_correct_enemy_type(self.child)(bEnemy(self.rmanager, datas, [0,0]))
                be.rect = self.rect
                be.veloc = self.veloc
                be.pathind = self.pathind
                be.path = self.path
                # Set the hp - if hp is negative, so be it
                be.hp += self.hp
                gs.enemies.append(be)
            if gs.state != game.Mode.sandbox:
                gs.money += self.cost

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

    def draw(self, surface):
        surface.blit(self.image, (self.rect.centerx, self.rect.centery))

class RedEnemy(Enemy):
    def __init__(self, en):
        self.eid = 0

        Enemy.__init__(self, en)

        self.child = None

    def update(self, gs):
        Enemy.update(self, gs)

    def draw(self, surface):
        Enemy.draw(self, surface)

class BlueEnemy(Enemy):
    def __init__(self, en):
        self.eid = 1

        Enemy.__init__(self, en)

        self.child = 0

    def update(self, gs):
        Enemy.update(self, gs)

    def draw(self, surface):
        Enemy.draw(self, surface)

class GreenEnemy(Enemy):
    def __init__(self, en):
        self.eid = 2

        Enemy.__init__(self, en)

        self.child = 1

    def update(self, gs):
        Enemy.update(self, gs)

    def draw(self, surface):
        Enemy.draw(self, surface)

class YellowEnemy(Enemy):
    def __init__(self, en):
        self.eid = 3

        Enemy.__init__(self, en)

        self.child = 2

    def update(self, gs):
        Enemy.update(self, gs)

    def draw(self, surface):
        Enemy.draw(self, surface)

class PinkEnemy(Enemy):
    def __init__(self, en):
        self.eid = 4

        Enemy.__init__(self, en)

        self.child = 3

    def update(self, gs):
        Enemy.update(self, gs)

    def draw(self, surface):
        Enemy.draw(self, surface)
 
enem_Map = [RedEnemy, BlueEnemy, GreenEnemy, YellowEnemy, PinkEnemy]


def get_correct_enemy_type(num):
    try:
        return enem_Map[num]
    except:
        raise Exception("Enemy #%d not found exception" % num)