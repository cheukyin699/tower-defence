# File: sprites.py
import pygame
from utils import *

class Sprite(pygame.sprite.Sprite):
    '''
    Base class for a normal sprite
    '''
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
        # If has visible (true on default)
        self.visible = True
        if data.has_key('visible'):
            self.visible = data['visible']
        # If has group
        self.group = None
        if data.has_key('group'):
            self.group = data['group']
        # If has size
        self.size = None
        if data.has_key('size'):
            self.size = data['size']

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, (self.rect.x, self.rect.y))

class Explosion(Sprite):
    '''
    Base class for an explosion, inherits Sprite
    '''
    def __init__(self, data, rmanager):
        Sprite.__init__(self, data, rmanager)

        # Set pos in middle
        self.rect.center = data['pos']

        self.life = data['life']

    def update(self):
        if self.life <= 0:
            self.kill()
        else:
            self.life -= 1

class OverheadText(pygame.sprite.Sprite):
    '''
    A small class that adds some text to display to the user.
    You can set a timer on it.
    '''
    def __init__(self, rmanager, text, pos, size):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(rmanager.fonts['monospace'].render(text, True, Color.red), size)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.life = 450

    def update(self):
        if self.life <= 0:
            self.kill()
        else:
            self.life -= 1

class Button(Sprite):
    '''
    The base class for a button. This is an actual full-on class for a button,
    and it works similar to FLTK ones in that it tracks callbacks.
    '''
    def __init__(self, data, rmanager):
        Sprite.__init__(self, data, rmanager)

        # Set to normal state (non-pressed)
        # 'N' --> normal
        # 'O' --> over
        # 'P' --> pressed
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
