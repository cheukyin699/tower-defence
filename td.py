#!/usr/bin/env python
# File: td.py
import pygame                   # Pygame
from pygame.locals import *     # Pygame

# Import resource manager
import res_man
# Import game helper functions
import game


# Global variables
rmanager = res_man.Resources()

mode = game.Mode.splash





# Initializations
pygame.init()
pygame.mixer.init()

rmanager.loadFromJson('res/resources.json')
rmanager.loadFonts()


# The main loop
while mode != game.Mode.exiting:
    for evt in pygame.event.get():
        if evt.type == QUIT:
            mode = game.Mode.exiting


pygame.quit()
