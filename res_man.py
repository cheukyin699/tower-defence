# File: res_man.py
# Description: Manages all the resources

import pygame, json

class Resources:
    '''
    We are going to use a spritesheet for handling of sprites.
    '''
    def __init__(self):
        self.sounds = {}
        self.sprites = {}
        self.parsetree = {}
        self.fonts = {}

    def loadFromJson(self, fn):
        '''
        Loads datas from json file 'fn'
        '''
        self.parsetree = json.loads(fn)

    def loadFonts(self):
        '''
        Loads some fonts
        '''
        # Monospace
        self.fonts['monospace'] = pygame.font.SysFont('monospace', 15)
