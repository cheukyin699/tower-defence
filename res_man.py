# File: res_man.py
# Description: Manages all the resources

import pygame, json

class Resources:
    '''
    We are going to use a spritesheet for handling of sprites.
    '''
    def __init__(self):
        self.sounds = {}
        self.musics = {}
        self.sprites = {}
        self.parsetree = {}
        self.fonts = {}

        self.status_text = ''

        self.loaded = False

    def loadFromJson(self, fn):
        '''
        Loads datas from json file 'fn'
        '''
        f = open(fn, 'r')
        self.parsetree = {}
        self.parsetree = json.load(f)

    def loadFonts(self):
        '''
        Loads some fonts
        '''
        # Monospace
        self.fonts['monospace'] = pygame.font.SysFont('monospace', 15)

    def loadMusics(self):
        '''
        Loads some music filenames
        '''
        for key, data in self.parsetree['musics'].iteritems():
            self.musics[key] = data
            self.status_text = 'Loading ' + data


    def loadSounds(self):
        '''
        Loads sounds and musics specified in Json file
        '''
        for key, data in self.parsetree['sounds'].iteritems():
            self.sounds[key] = pygame.mixer.Sound(data)
            self.status_text = 'Loading ' + data

    def loadSprites(self):
        '''
        Loads the sprites specified in Json file
        '''
        # Load the sprite sheet
        self.ssheet = pygame.image.load(self.parsetree['sprites']['file'])

        for key, data in self.parsetree['sprites']['sprites'].iteritems():
            # NOTE: data = rectangle which 'key' is located
            self.sprites[key] = self.ssheet.subsurface(data)
            self.status_text = 'Loading ' + key

    def loadMenu(self):
        '''
        Loads the menu json file for the layout
        '''
        self.menulayout = self.parsetree
