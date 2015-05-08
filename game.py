# -*- coding: utf-8 -*-
# File: game.py
# Description: Provides useful classes and functions for the game

import pygame
import towers
import enemy
import bullet
import math
pygame.init()

# FUNCTIONS
def getVeloc(a, b, veloc):
    '''
    a: [x,y]
    b: [x,y]
    veloc: The velocity scalar

    Uses the 'brute force' method for turning the angles.

    Returns list of 2 dimensions for a going to b
    '''
    # First, get angle (radians)
    if b[0]-a[0] == 0:
        angle = 0
    else:
        angle = math.atan(float(a[1]-b[1])/(b[0]-a[0]))
    vx = int(veloc*math.cos(angle))
    vy = int(veloc*math.sin(angle))
    if b[0]-a[0]>0 and a[1]-b[1]>0:
        vy = -vy
    elif b[0]-a[0]<0 and a[1]-b[1]>0:
        vx = -vx
    elif b[0]-a[0]<0 and a[1]-b[1]<0:
        vx = -vx
    elif b[0]-a[0]>0 and a[1]-b[1]<0:
        vy = -vy
    #print (math.degrees(angle), (b[0]-a[0]), a[1]-b[1], vx, vy)
    return [vx,vy]

# CLASSES
class Mode:
    '''
    Just some normal game modes
    '''
    errormsg = -1
    splash = 0
    menu = 1
    playing = 2
    config = 3
    exiting = 4

class Color:
    '''
    Some plain colors
    '''
    black =     (  0,   0,   0)
    white =     (255, 255, 255)
    red =       (200,   0,   0)
    green =     (  0, 200,   0)
    blue =      (  0,   0, 200)

    yellow =    (255, 255,   0)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, data, rmanager):
        pygame.sprite.Sprite.__init__(self)

        self.sname = data['sprite']
        self.type = data['type']
        self.text = data['text']
        self.state = ''

        self.rmanager = rmanager

        # If the type is a sprite, then load it up
        if self.type == 'sprite':
            self.image = rmanager.sprites[data['sprite']]
            if data.has_key('size'):
                self.image = pygame.transform.scale(self.image, data['size'])
            self.rect = self.image.get_rect()
            self.rect.x = data['pos'][0]
            self.rect.y = data['pos'][1]

class Button(Sprite):
    def __init__(self, data, rmanager):
        Sprite.__init__(self, data, rmanager)

        # Set to normal state (non-pressed)
        self.state = 'N'

        self.image = rmanager.sprites[self.sname + '-' + self.state]
        self.rect = self.image.get_rect()
        self.rect.x = data['pos'][0]
        self.rect.y = data['pos'][1]

        self.cb = None
        self.cb_args = []
        
        # Sound on button click
        self.sound = data['sound']
        self.played = False

    @classmethod
    def sMade(cls, *args, **kwargs):
        return cls(kwargs, kwargs.get('rmanager'))

    def callback(self, func, *args):
        self.cb = func
        self.cb_args = args

    def do_callback(self):
        self.cb(*self.cb_args)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        # If up
        if self.state == 'U':
            self.state = 'O'
        self.image = self.rmanager.sprites[self.sname + '-' + self.state].copy()
        label = self.rmanager.fonts['monospace'].render(self.text, False, Color.black)
        labelrect = label.get_rect()
        self.image.blit(label, (self.rect.w/2-labelrect.w/2, self.rect.h/2-labelrect.h/2))

        # If clicked
        if self.state == 'P' and self.cb:
            self.do_callback()
            
        # If hovered
        if self.state == 'O' and self.sound and not self.played:
            self.rmanager.sounds[self.sound].play()
            self.played = True
            
        # If normal
        if self.state == 'N':
            self.played = False

class State:
    '''
    The base class for all game states
    '''
    def __init__(self, surface, rmanager, state=Mode.splash):
        self.surface = surface
        self.rmanager = rmanager
        self.state = state

        self.SIZE = (surface.get_rect().w, surface.get_rect().h)

    def changestate(self, state):
        self.state = state

    def handlemousestate(self, (x, y), mstate):
        pass

    def update(self):
        pass

class ErrorState(State):
    '''
    The class for handling unexpected errors.
    Expect use in debugging ONLY.
    (Or maybe if the sky is falling, then I'll consider.)
    '''
    def __init__(self, surface, rmanager, mesg):
        State.__init__(self, surface, rmanager, state=Mode.errormsg)

        self.mesg = mesg

    def draw(self):
        self.surface.fill(Color.black)

        # Display the error message in RED
        stat = self.rmanager.fonts['monospace'].render(self.mesg, True, Color.red)
        statrect = stat.get_rect()
        # ... in the middle of the screen
        self.surface.blit(stat, (self.SIZE[0]/2-statrect.w/2, self.SIZE[1]/2-statrect.h/2))

class SplashState(State):
    '''
    The class for handling the splash state
    '''
    def __init__(self, surface, rmanager):
        State.__init__(self, surface, rmanager, state=Mode.splash)

    def draw(self):
        self.surface.fill(Color.black)

        # Display the status text
        stat = self.rmanager.fonts['monospace'].render(self.rmanager.status_text, True, Color.white)
        statrect = stat.get_rect()
        # ... in the middle of the screen
        self.surface.blit(stat, (self.SIZE[0]/2-statrect.w/2, self.SIZE[1]/2-statrect.h/2))

    def update(self):
        '''
        Updates the state of this guy.
        Probably won't be used at all since 2 lines of code
        is fairly easy to understand in a <10 line loop.
        '''
        if self.rmanager.loaded:
            self.state = Mode.menu


class MenuState(State):
    '''
    The class for handling the menu state
    '''
    def __init__(self, surface, rmanager):
        State.__init__(self, surface, rmanager, state=Mode.menu)

        self.layout = self.rmanager.menulayout
        self.sprites = pygame.sprite.Group()

        for key, data in self.layout.iteritems():
            if data['type'] == 'button':
                bt = Button(data, rmanager)
                if key == 'play-bt':
                    bt.callback(self.changestate, Mode.playing)
                elif key == 'quit-bt':
                    bt.callback(self.changestate, Mode.exiting)
                self.sprites.add(bt)
            elif key == 'background':
                s = Sprite(data, rmanager)
                self.bg = s
            else:
                self.sprites.add(Sprite(data, rmanager))

    def handlemousestate(self, (mx, my), mstate='N'):
        '''
        'N' is for normal
        'O' is for over
        'P' is for pressed
        '''
        for s in self.sprites.sprites():
            if s.rect.collidepoint(mx, my):
                s.state = mstate
            else:
                s.state = 'N'

    def draw(self):
        self.surface.fill(Color.black)

        self.surface.blit(self.bg.image, (0, 0))
        self.sprites.draw(self.surface)

    def update(self):
        self.sprites.update()
        
class GameMenu(pygame.sprite.Sprite):
    '''
    The class responsible for responding to
    clicks on the menu
    The in-game menu will be positioned on the
    bottom of the screen
    
    Buttons that should be included:
    - Buy tower(s) selection
    - Upgrade menu
    '''
    def __init__(self, surface, rmanager, gs):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = rmanager
        self.gs = gs

        self.tlist = pygame.sprite.Group()
        
        self.image = pygame.surface.Surface((surface.get_rect().w, surface.get_rect().h*.25))
        self.image.fill(Color.white)
        self.rect = self.image.get_rect()
        self.rect.y = surface.get_rect().h*.75
        
        # Have focus on selected tower. If focus is None,
        # menu displays normal menu stuff
        self.focus = None

        # Drag selected tower (buy it)
        self.drag = None

        # The play button (starts rounds)
        self.play_bt = Button.sMade(type='button', text='Play', sprite='Button1', sound='wood-click',
                pos=[self.rect.w*.75, 0], size=[80, self.rect.h], rmanager=self.rmanager)
        self.play_bt.callback(self.gs.nextWave)

        # Init towers
        ind = 0
        for  data in self.rmanager.data['towers'].itervalues():
            t = towers.Tower(self.rmanager, data, (50*ind+100, 5))
            self.tlist.add(t)
            ind += 1

    def drawMoney(self):
        moneylbl = self.rmanager.fonts['monospace'].render("$"+str(self.gs.money), True, Color.green)
        self.image.blit(moneylbl, (0,0))

    def drawLives(self):
        liveslbl = self.rmanager.fonts['monospace'].render("LF:"+str(self.gs.lives), False, Color.red)
        self.image.blit(liveslbl, (0, liveslbl.get_rect().h))

    def draw(self, surface):
        self.image.fill(Color.white)

        # Draw some labels first
        self.drawMoney()
        self.drawLives()

        if self.focus == None:
            # Display the main game menu
            # Draw some other stuffs
            self.tlist.draw(self.image)

            # If you are dragging
            if self.drag != None:
                mp = list(pygame.mouse.get_pos())
                mp[0] -= 25
                mp[1] -= 25
                surface.blit(self.drag.orgimage, mp)

            # Update play button
            self.play_bt.update()
            # Draw play button
            self.play_bt.draw(self.image)
        else:
            # If you have focused on some random tower,
            # display the upgrade menu
            namelbl = self.rmanager.fonts['monospace'].render(self.focus.name, True, Color.blue)
            self.image.blit(namelbl, (0, namelbl.get_rect().h*2))
            # Draw the range (with some ALPHA)
            rngcircle = pygame.surface.Surface((self.focus.range*2, self.focus.range*2))
            rngcircle.set_alpha(150)
            # Draw the circle
            pygame.draw.circle(rngcircle, (50,50,50,75), (self.focus.range, self.focus.range), self.focus.range)
            # Blit the circle
            surface.blit(rngcircle, (self.focus.rect.centerx-self.focus.range, self.focus.rect.centery-self.focus.range))

        surface.blit(self.image, (self.rect.x, self.rect.y))

    def handlemousestate(self, (mx, my), mstate='N'):
        if self.focus == None:
            if self.drag != None and mstate == 'U':
                self.drag = None
            elif mstate == 'P':
                for t in self.tlist.sprites():
                    if t.rect.collidepoint(mx,my) and self.gs.money-t.cost >= 0:
                        # If you clicked the tower, just set dragged tower
                        # and break out of loop, because it is impossible to
                        # click on multiple ones
                        self.drag = t
                        break
            if self.play_bt.rect.collidepoint(mx,my):
                self.play_bt.state = mstate
            elif self.play_bt.state == 'O':
                self.play_bt.state = 'N'

class GameState(State):
    '''
    The class for handling the playing state
    '''
    def __init__(self, surface, rmanager):
        State.__init__(self, surface, rmanager, state=Mode.playing)

        # All sprite groups
        self.towers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.gm = GameMenu(self.surface, self.rmanager, self)

        # Some properties
        self.lives = 100
        self.money = 1000

        # The wave that you are currently on
        self.wave = 0
        # The enemy that you are currently on
        self.noen = 0
        # Should I spawn enemies?
        self.runthru_enemy = False
        # Timer
        self.en_cd = 0

    def draw(self):
        self.surface.fill(Color.black)

        self.enemies.draw(self.surface)
        self.towers.draw(self.surface)
        self.projectiles.draw(self.surface)
        self.gm.draw(self.surface)

        # Check for dragging something
        if self.gm.drag != None:
            mp = list(pygame.mouse.get_pos())
            # Draw the range first (with some ALPHA)
            rngcircle = pygame.surface.Surface((self.gm.drag.range*2, self.gm.drag.range*2))
            rngcircle.set_alpha(150)
            # Check for overlapping
            overlap = False
            for t in self.towers.sprites():
                if t.rect.collidepoint(mp[0], mp[1]):
                    overlap = True
                    break
            col = (50,50,50,75)
            if overlap:
                col = (200,0,0,75)
            mp[0] -= 25
            mp[1] -= 25
            # Draw circle with alpha
            pygame.draw.circle(rngcircle, col, (self.gm.drag.range, self.gm.drag.range), self.gm.drag.range)
            self.surface.blit(rngcircle, (mp[0]-self.gm.drag.range+25, mp[1]-self.gm.drag.range+25))
            self.surface.blit(self.gm.drag.orgimage, mp)

    def update(self):
        if self.runthru_enemy and self.en_cd <= 0:
            if self.noen >= len(self.rmanager.data['waves'][self.wave]):
                # If done spawning enemies
                self.noen = 0
                self.wave += 1
                self.runthru_enemy = False
            else:
                enno = self.rmanager.data['waves'][self.wave][self.noen]
                if enno == 0:
                    # WAIT FOR TICKS (15)
                    self.en_cd = 15
                else:
                    self.enemies.add(enemy.Enemy(enno))
                self.noen += 1
        elif self.en_cd > 0:
            self.en_cd -= 1

        # Projectile-enemy collision
        pe_col = pygame.sprite.groupcollide(self.projectiles, self.enemies, False, False)
        for k, d in pe_col.iteritems():
            for item in d:
                if k.hp > 0:
                    item.hp -= 1
                    k.hp -= 1
                    
        # Enemy-End_wall collision
        for e in self.enemies.sprites():
            if e.rect.centerx > self.SIZE[0]:
                self.lives -= e.hp
                e.kill()

        self.enemies.update(self)
        self.towers.update(self.enemies)
        self.projectiles.update()

        # Shoot stuff
        for t in self.towers.sprites():
            # Find all towers that have things to shoot
            if t.shoot != None and t.shoot != 'C':
                # Spawn a bullet at some velocity
                veloc = getVeloc((t.rect.centerx, t.rect.centery), t.shoot, t.shotveloc)
                b = bullet.Bullet((t.rect.centerx, t.rect.centery), veloc)
                self.projectiles.add(b)

                # Reset tower shot to None
                t.shoot = None

    def nextWave(self):
        '''
        Starts the next wave when all enemies are killed
        '''
        if len(self.enemies.sprites()) == 0:
            # When all enemies are killed, start next wave
            self.runthru_enemy = True

    def handlemousestate(self, (mx, my), mstate='N'):
        if mstate == 'U':
            # Check to see if you are clicking off the focused
            # tower. To click off the focused tower, click on
            # something else
            if self.gm.focus:
                self.gm.focus = None

            # Check all towers
            for t in self.towers.sprites():
                if t.rect.collidepoint(mx, my):
                    # Set the focus point
                    # Break after setting the focus point
                    self.gm.focus = t
                    break

        # Check the game menu
        if self.gm.rect.collidepoint(mx, my):
            self.gm.handlemousestate((mx, my-self.gm.rect.y), mstate)
        # Check if you are dragging something from the game menu
        # and you drop it in the screen
        if self.gm.drag != None and mstate == 'U':
            # If you've just placed down something from the menu...
            # ...and you didn't place it on top another tower
            overlap = False
            for t in self.towers.sprites():
                if t.rect.collidepoint(mx, my):
                    overlap = True
                    break
            if not overlap:
                t = towers.rTower(self.gm.drag)
                t.rect.x = mx-25
                t.rect.y = my-25
                self.towers.add(t)
                self.gm.drag = None
                # TAKE YO MONEY
                self.money -= t.cost
            else:
                # If you placed it on top of another
                # tower, remove and try again
                self.gm.drag = None
