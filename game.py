# File: game.py
# Description: Provides useful classes and functions for the game

import pygame
from cairo._cairo import Surface
pygame.init()


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
    red =       (255,   0,   0)
    green =     (  0, 255,   0)
    blue =      (  0,   0, 255)

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

    def callback(self, func, *args):
        self.cb = func
        self.cb_args = args

    def do_callback(self):
        self.cb(*self.cb_args)

    def update(self):
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
        
        self.gs = gs
        
        self.image = pygame.surface.Surface((surface.get_rect().w, surface.get_rect().h*.25))
        self.image.fill(Color.white)
        self.rect = self.image.get_rect()
        self.rect.y = surface.get_rect().h*.75
        
        # Have focus on selected tower. If focus is None,
        # menu displays normal menu stuff
        self.focus = None
        
    def draw(self, surface):
        self.image.fill(Color.white)
        if self.focus == None:
            surface.blit(self.image, (self.rect.x, self.rect.y))
        
    def handlemousestate(self, (mx, my), mstate='N'):
        pass

class GameState(State):
    '''
    The class for handling the playing state
    '''
    def __init__(self, surface, rmanager):
        State.__init__(self, surface, rmanager, state=Mode.playing)
        
        # All sprite groups
        self.towers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.gm = GameMenu(self.surface, self.rmanager, self)
        
        # Some properties
        self.lives = 100
        self.money = 1000
        
        self.waves = []

    def draw(self):
        self.surface.fill(Color.black)
        
        self.enemies.draw(self.surface)
        self.towers.draw(self.surface)
        self.gm.draw(self.surface)

    def update(self):
        self.enemies.update()
        self.towers.update()

    def handlemousestate(self, (mx, my), mstate='N'):
        # Check all towers
        for s in self.towers.sprites():
            if s.rect.collidepoint(mx, my):
                s.state = mstate
            else:
                s.state = 'N'
        # Check the game menu
        if self.gm.rect.collidepoint(mx, my):
            self.gm.handlemousestate((mx, my), mstate)