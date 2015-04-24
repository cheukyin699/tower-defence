# File: game.py
# Description: Provides useful classes and functions for the game

import pygame
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

        self.sprites.draw(self.surface)

    def update(self):
        self.sprites.update()

