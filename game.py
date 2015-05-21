# -*- coding: utf-8 -*-
# File: game.py
# Description: Provides useful classes and functions for the game

import pygame
import towers
import enemy
import math
from jsonmaputils import TMXJsonMap
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
    return [vx,vy]

def getAngle(a, b):
    '''
    a: [x,y]
    b: [x,y]

    Uses the 'brute force' method for turning the angles.

    Returns the angle
    '''
    # First, get relative angle (radians)
    if b[0]-a[0] == 0:
        angle = 0
    else:
        angle = math.degrees(math.atan(float(a[1]-b[1])/(b[0]-a[0])))
    if b[0]-a[0]>0 and a[1]-b[1]>0:
        angle -= 90
    elif b[0]-a[0]<0 and a[1]-b[1]>0:
        angle += 90
    elif b[0]-a[0]<0 and a[1]-b[1]<0:
        angle += 90
    elif b[0]-a[0]>0 and a[1]-b[1]<0:
        angle -= 90
    return angle

def getDist(a, b):
    '''
    a: rect
    b: rect

    Returns the straight line distance between the 2 points
    '''
    return math.sqrt((a.centerx-b.centerx)**2+(a.centery-b.centery)**2)

# CLASSES
class Mode:
    '''
    Just some normal game modes
    '''
    errormsg = -1
    splash = 0
    menu = 1
    freeplay = 2
    sandbox = 3
    multiplayer = 4
    config = 5
    exiting = 6

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
        # If has visible(true on default)
        if data.has_key('visible'):
            self.visible = data['visible']
        else:
            self.visible = True
        # If has group
        if data.has_key('group'):
            self.group = data['group']
        else:
            self.group = None
        # If has size
        if data.has_key('size'):
            self.size = data['size']
        else:
            self.size = None

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, (self.rect.x, self.rect.y))

class Explosion(Sprite):
    def __init__(self, data, rmanager):
        Sprite.__init__(self, data, rmanager)
        
        # Set pos in middle
        self.rect.centerx = data['pos'][0]
        self.rect.centery = data['pos'][1]
        
        self.life = data['life']
        
    def update(self):
        if self.life <= 0:
            self.kill()
        else:
            self.life -= 1

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
        if self.visible:
            surface.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        if self.visible:
            # If up
            if self.state == 'U':
                self.state = 'O'
            self.image = self.rmanager.sprites[self.sname + '-' + self.state].copy()
            if self.size:
                # If you have specified the size for this
                self.image = pygame.transform.scale(self.image, self.size)
                x,y = self.rect.x, self.rect.y
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
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
                    bt.callback(self.tog_play_menu)
                elif key == 'freeplay-bt':
                    bt.callback(self.changestate, Mode.freeplay)
                elif key == 'sandbox-bt':
                    bt.callback(self.changestate, Mode.sandbox)
                elif key == 'multiplayer-bt':
                    bt.callback(self.changestate, Mode.multiplayer)
                elif key == 'quit-bt':
                    bt.callback(self.changestate, Mode.exiting)
                self.sprites.add(bt)
            elif key == 'background':
                s = Sprite(data, rmanager)
                self.bg = s
            else:
                self.sprites.add(Sprite(data, rmanager))

    def tog_play_menu(self):
        '''
        Toggles the play menu when you click the
        play button
        '''
        for s in self.sprites.sprites():
            if s.group == 'play':
                s.visible = not s.visible

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
        for s in self.sprites.sprites():
            s.draw(self.surface)

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
        if self.gs.state != Mode.freeplay:
            self.elist = pygame.sprite.Group()

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
        if self.gs.state == Mode.freeplay:
            self.play_bt = Button.sMade(type='button', text='Play', sprite='Button1', sound='wood-click',
                    pos=[self.rect.w*.75, 0], size=[80, self.rect.h], rmanager=self.rmanager)
            self.play_bt.callback(self.gs.nextWave)

        # Init towers
        ind = 0
        for data in self.rmanager.data['towers'].itervalues():
            t = towers.Tower(self.rmanager, data, (50*ind+100, 5))
            self.tlist.add(t)
            ind += 1

        # Init enemies
        if self.gs.state != Mode.freeplay:
            ind = 0
            # It is an array, so it is different
            for data in self.rmanager.data['enemies']:
                e = enemy.bEnemy(self.rmanager, data, (50*ind+100, 55))
                self.elist.add(e)
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
            # Draw towers
            self.tlist.draw(self.image)
            # If in sandbox/multiplayer, draw enemies (to buy)
            if self.gs.state != Mode.freeplay:
                self.elist.draw(self.image)

            # If you are dragging
            if self.drag != None:
                mp = list(pygame.mouse.get_pos())
                mp[0] -= self.drag.rect.w/2
                mp[1] -= self.drag.rect.h/2
                surface.blit(self.drag.orgimage, mp)

            # Update play button
            if self.gs.state == Mode.freeplay:
                self.play_bt.update()
                # Draw play button
                self.play_bt.draw(self.image)
        else:
            # If you have focused on some random tower,
            # display the upgrade menu
            namelbl = self.rmanager.fonts['monospace'].render(self.focus.name, True, Color.blue)
            self.image.blit(namelbl, (0, namelbl.get_rect().h*2))
            # Draw the range (without alpha)
            pygame.draw.circle(surface, Color.white, (self.focus.rect.centerx,self.focus.rect.centery), self.focus.range, 1)

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
    def __init__(self, surface, rmanager, state):
        State.__init__(self, surface, rmanager, state=state)

        # All sprite groups
        self.towers = pygame.sprite.Group()
        self.enemies = []
        self.projectiles = pygame.sprite.Group()
        self.fx = pygame.sprite.Group()
        self.gm = GameMenu(self.surface, self.rmanager, self)

        # The backdrop
        self.bg = TMXJsonMap('res/maps/grass-map1.json')

        # Some properties
        self.lives = 100
        self.money = 650

        # The wave that you are currently on
        self.wave = 0
        # The index of the wave that you are currently on
        self.noen = 0
        # Count of enemies to spawn and enemy id
        self.enem_on = [0,0]
        # Should I spawn enemies?
        self.runthru_enemy = False
        # Timer
        self.en_cd = 0

    def draw(self):
        self.surface.fill(Color.black)

        # Draw the background on first
        self.surface.blit(self.bg.layers['background'].image, (0,0))

        for i in xrange(len(self.enemies)):
            self.enemies[i].draw(self.surface)
        self.towers.draw(self.surface)
        self.projectiles.draw(self.surface)
        self.fx.draw(self.surface)
        self.gm.draw(self.surface)

        # Check for dragging something
        if self.gm.drag != None:
            mp = list(pygame.mouse.get_pos())
            # Draw the range without ALPHA
            overlap = False
            for t in self.towers.sprites():
                if t.rect.collidepoint(mp[0], mp[1]):
                    overlap = True
                    break
            col = Color.white
            if overlap:
                col = Color.red
            pygame.draw.circle(self.surface, col, (mp[0],mp[1]), self.gm.drag.range, 1)
            mp[0] -= self.gm.drag.rect.w/2
            mp[1] -= self.gm.drag.rect.h/2
            self.surface.blit(self.gm.drag.orgimage, mp)

    def update(self):
        if self.runthru_enemy and self.en_cd <= 0 and self.state != Mode.sandbox:
            if self.noen >= len(self.rmanager.data['waves'][self.wave]) and self.enem_on[0] <= 0:
                # If done spawning enemies
                # And you have cleared the enemy buffer
                self.noen = 0
                self.wave += 1
                self.runthru_enemy = False
            elif self.enem_on[0] > 0:
                en = enemy.get_correct_enemy_type(self.enem_on[1])
                en.path = self.rmanager.data['maps'][self.currentmap]['path']
                self.enemies.append(en)
                # Wait 3 ticks
                self.en_cd = 3
            else:
                enno = self.rmanager.data['waves'][self.wave][self.noen].split('x')
                # Set the spawn buffer
                self.enem_on = [int(enno[0]), int(enno[1])]
                self.noen += 1
        elif self.en_cd > 0 and self.state != Mode.sandbox:
            self.en_cd -= 1

        # Enemy
        for e in self.enemies:
            pe = pygame.sprite.spritecollide(e, self.projectiles, False)
            if len(pe) > 0:
                # If you collided with projectile
                for p in pe:
                    p.hit(self, e)
            if e.rect.centerx > self.SIZE[0]:
                self.lives -= e.hp
                self.enemies.remove(e)
            else:
                e.update(self)
            if e.hp <= 0:
                self.enemies.remove(e)

        self.towers.update(self.enemies)
        self.projectiles.update(self.SIZE)
        self.fx.update()

        # Shoot stuff
        for t in self.towers.sprites():
            # Find all towers that have things to shoot
            if t.shoot != None and t.shoot != 'C':
                # Spawn a bullet at some velocity
                veloc = getVeloc((t.rect.centerx, t.rect.centery), t.shoot, t.shotveloc)
                b = t.projectile((t.rect.centerx, t.rect.centery), veloc, t.dmg, 1)
                self.projectiles.add(b)

                # Reset tower shot to None
                t.shoot = None

    def nextWave(self):
        '''
        Starts the next wave when all enemies are killed
        '''
        if len(self.enemies) == 0:
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
                t = self.gm.drag.tower(self.gm.drag)
                t.rect.x = mx-t.rect.w/2
                t.rect.y = my-t.rect.h/2
                self.towers.add(t)
                self.gm.drag = None
                # TAKE YO MONEY
                self.money -= t.cost
            else:
                # If you placed it on top of another
                # tower, remove and try again
                self.gm.drag = None
