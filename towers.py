import pygame
import math
import game
import bullet

def getDist(a, b):
    return math.sqrt((a.centerx-b.centerx)**2+(a.centery-b.centery)**2)

def get_enemy_pathpoints(e):
    prior = e.pathind + 1 - game.getDist(e.path[e.pathind], e.rect.center)/game.getDist(e.path[e.pathind], e.path[e.pathind-1])
    return prior

class Tower(pygame.sprite.Sprite):
    '''
    The tower with the money displayed
    Only used in menus
    '''
    def __init__(self, rmanager, data, (x,y), gs):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = rmanager
        self.gs = gs

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
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        costlbl = pygame.transform.scale(costlbl, (self.rect.w, costlbl.get_rect().h))
        self.image.blit(costlbl, (0,0))

        # What tower is this going to become?
        if self.sprite == 'gunturret':
            self.projectile = bullet.Bullet
            self.tower = rTower
        elif self.sprite == 'missturret':
            self.projectile = bullet.Missile
            self.tower = rTower
        elif self.sprite == 'sniperturret':
            self.projectile = None
            self.tower = SniperTower

class rTower(pygame.sprite.Sprite):
    '''
    The tower displayed that does the actual fighting
    Used in-game only
    '''
    def __init__(self, t):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = t.rmanager
        self.gs = t.gs

        self.image = self.rmanager.sprites[t.sprite].copy()
        self.cost = t.cost
        self.dmg = t.dmg
        self.rate = t.rate
        self.range = t.range
        self.sprite = t.sprite
        self.name = t.name
        self.shotveloc = t.shotveloc
        self.angle = 0
        self.sold = False

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
        self.targetbt = game.Button.sMade(type="button",text='First', sprite='Button1',sound='wood-click',
                pos=[0,30*2], rmanager=self.rmanager)
        self.targetbt.callback(self.cycle_targeting)

        # Sell button
        self.sellbt = game.Button.sMade(type="button",text="Sell",sprite='Button1',sound='wood-click',
                pos=[0,30*3+5],size=[120,30],rmanager=self.rmanager)
        self.sellbt.callback(self.sell)

        '''
        Now, for the type of projectile (if any)
        that this tower would shoot
        '''
        if self.sprite == 'gunturret':
            self.projectile = bullet.Bullet
        elif self.sprite == 'missturret':
            self.projectile = bullet.Missile
        elif self.sprite == 'sniperturret':
            self.projectile = None

    def cost_update(self):
        self.sellbt.text = "Sell $%d" % int(self.cost * .75)

    def sell(self):
        if not self.sold:
            self.sold = True
            if self.gs.state != game.Mode.sandbox:
                # Give moneys if not sandbox
                self.gs.money += int(self.cost * 0.75)
            self.kill()

    def cycle_targeting(self):
        self.target = (self.target+1)%4
        if self.target == 0:
            self.targetbt.text = 'First'
        elif self.target == 1:
            self.targetbt.text = 'Last'
        elif self.target == 2:
            self.targetbt.text = 'Close'
        else:
            self.targetbt.text = 'Strong'

    def handlemousestate(self, (mx, my), mstate='N'):
        self.targetbt.state = 'N'
        self.sellbt.state = 'N'
        if self.targetbt.rect.collidepoint(mx, my):
            self.targetbt.state = mstate
        elif self.sellbt.rect.collidepoint(mx, my):
            self.sellbt.state = mstate

    def update(self, enemies):
        if self.reloading <= 0:
            # If you have finished reloading
            # Get list of enemies in range
            enems_rng = []
            for e in enemies:
                dist = getDist(e.rect, self.rect)
                if dist <= self.range:
                    prior = get_enemy_pathpoints(e)
                    enems_rng.append([e, dist, prior])

            # Check for shooting target priority
            if len(enems_rng) >= 1:
                if self.target == 0:
                    # Shoot the first
                    s = max(enems_rng, key=lambda e:e[2])
                    self.shoot = [s[0].rect.centerx,s[0].rect.centery]
                elif self.target == 1:
                    # Shoot the last
                    s = min(enems_rng, key=lambda e:e[2])
                    self.shoot = [s[0].rect.centerx,s[0].rect.centery]
                elif self.target == 2:
                    # Find the one that is closest to tower
                    s = min(enems_rng, key=lambda e:e[1])
                    self.shoot = [s[0].rect.centerx,s[0].rect.centery]
                elif self.target == 3:
                    # Shoot the strongest
                    # Actually, they are ordered by enemy_id
                    s = max(enems_rng, key=lambda e:e[0].eid)
                    self.shoot = [s[0].rect.centerx,s[0].rect.centery]
                # Change the shooting angle
                self.angle = game.getAngle((self.rect.centerx, self.rect.centery), self.shoot)
                self.image = pygame.transform.rotate(self.rmanager.sprites[self.sprite].copy(), self.angle)
                # Change rects
                x, y = self.rect.centerx, self.rect.centery
                self.rect = self.image.get_rect()
                self.rect.centerx, self.rect.centery = x, y
                self.reloading = self.rate
        else:
            self.reloading -= 1

    def draw_to_menu(self, surface):
        '''
        Draws to the menu
        '''
        # Draws the label
        namelbl = self.rmanager.fonts['monospace'].render(self.name, True, game.Color.blue)
        surface.blit(namelbl, (0, namelbl.get_rect().h*2))
        # Update buttons
        self.cost_update()
        self.targetbt.update()
        self.sellbt.update()
        # Draw buttons
        self.targetbt.draw(surface)
        self.sellbt.draw(surface)

class SniperTower(rTower):
    def __init__(self, t):
        rTower.__init__(self, t)

    def update(self, enemies):
        if self.reloading <= 0:
            # Finished sniper reloading
            # Just attack (no need for range)
            if len(enemies) > 0:
                self.shoot = 'C'
                e = None
                if self.target == 0:
                    # Shoot the first in line
                    e = max(enemies, key=lambda enem:get_enemy_pathpoints(enem))
                elif self.target == 1:
                    # Shoot the last in line
                    e = min(enemies, key=lambda enem:get_enemy_pathpoints(enem))
                elif self.target == 2:
                    # Shoot the one that is the closest to tower
                    e = min(enemies, key=lambda enem:getDist(self.rect, enem.rect))
                elif self.target == 3:
                    # Shoot the strongest one
                    e = max(enemies, key=lambda enem:enem.eid)

                if e:
                    self.angle = game.getAngle((self.rect.centerx, self.rect.centery), (e.rect.centerx, e.rect.centery))
                    self.image = pygame.transform.rotate(self.rmanager.sprites[self.sprite].copy(), self.angle)
                    # Attack
                    e.hp -= self.dmg
                    # Rect changing
                    x, y = self.rect.centerx, self.rect.centery
                    self.rect = self.image.get_rect()
                    self.rect.centerx, self.rect.centery = x, y
                    self.reloading = self.rate
        else:
            self.reloading -= 1
