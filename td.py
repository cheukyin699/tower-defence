#!/usr/bin/env python
# File: td.py
import pygame                   # Pygame
from pygame.locals import *     # Pygame
import threading                # Threading, cause we need it

# Import resource manager
import res_man
# Import game helper functions
import game


# Constants
SIZE = 800, 500



pygame.init()
pygame.mixer.init()

# Global variables
rmanager = res_man.Resources()
surface = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
mode = game.Mode.splash





# Initializations
pygame.display.set_caption('Tower Defence')

rmanager.loadFromJson('res/resources.json')
rmanager.loadFonts()


# Set up multithreading
def managerinitwork():
    '''
    Asynchronus loading of sounds and sprites:
    Loads all sprites
    Loads all sounds/musics
    '''
    rmanager.loadSounds()
    rmanager.loadSprites()
    rmanager.loaded = True
    return

loadstuff = threading.Thread(target=managerinitwork)
loadstuff.start()


# The loading splash screen
while mode == game.Mode.splash:
    surface.fill(game.Color.black)

    # Checks if it is still loading stuff
    if rmanager.loaded:
        mode = game.Mode.menu

    game.displaysplash(surface, rmanager, SIZE=SIZE)

    clock.tick(60)
    pygame.display.flip()


# The main loop
while mode != game.Mode.exiting:
    surface.fill(game.Color.black)
    for evt in pygame.event.get():
        if evt.type == QUIT:
            mode = game.Mode.exiting

    # For the different modes, draw different
    # things on the screen (obviously)
    if mode == game.Mode.menu:
        # Draw the menu screen thingy
        game.displaymenu(surface, rmanager, SIZE=SIZE)


    clock.tick(60)
    pygame.display.flip()


pygame.quit()
