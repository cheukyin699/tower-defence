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
states = []





# Initializations
pygame.display.set_caption('Tower Defence')

rmanager.loadFromJson('res/resources.json')
rmanager.loadFonts()

states.append(game.SplashState(surface, rmanager))


# Set up multithreading
def managerinitwork():
    '''
    Asynchronus loading of sounds and sprites:
    Loads all sprites
    Loads all sounds/musics
    '''
    rmanager.loadSounds()
    rmanager.loadMusics()
    rmanager.loadSprites()
    rmanager.loaded = True
    return

loadstuff = threading.Thread(target=managerinitwork)
loadstuff.start()



# The loading splash screen
while mode == game.Mode.splash:
    # Checks if it is still loading stuff
    if rmanager.loaded:
        mode = game.Mode.menu

    # Draw it!
    states[-1].draw()

    clock.tick(60)
    pygame.display.flip()

# Now that everything has been loaded successfully,
# play some music for the menu.
pygame.mixer.music.load(rmanager.musics['menu'])
pygame.mixer.music.play(-1)


# Remove the state off the stack
# Add the menu state on the stack
states.pop()
states.append(game.MenuState(surface, rmanager))

# The main loop
while mode != game.Mode.exiting:
    # VERY IMPORTANT: If the game state changes in class,
    # but not outside, queue the state for deletion
    # and delete it.
    if states[-1].state != mode:
        # TURN THEM
        mode = states[-1].state

        # Checks them ONE BY ONE
        if states[-1].state == game.Mode.menu:
            states.append(game.MenuState(surface, rmanager))

        # Remove the LONER (safety issue)
        if len(states) > 1:
            states.pop(0)


    for evt in pygame.event.get():
        if evt.type == QUIT:
            mode = game.Mode.exiting

    states[-1].draw()

    clock.tick(60)
    pygame.display.flip()


pygame.mixer.quit()
pygame.quit()
