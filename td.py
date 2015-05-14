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
SIZE = 1200, 600


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
    # Load from main res file
    rmanager.loadSounds()
    rmanager.loadMusics()
    rmanager.loadSprites()

    # Load layouts from other res files
    rmanager.loadFromJson('res/mainmenu.json')
    rmanager.loadMenu()

    # Load tower, waves, enemy data
    rmanager.loadFromJson('res/datas.json')
    rmanager.loadData()

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
            # Check for menu
            states.append(game.MenuState(surface, rmanager))
        elif states[-1].state == game.Mode.freeplay:
            # Check for playing
            states.append(game.GameState(surface, rmanager, game.Mode.freeplay))
        elif states[-1].state == game.Mode.exiting:
            # Check for exit
            pass
        else:
            # Error: unknown/unimplemented state
            states.append(game.ErrorState(surface, rmanager, 'Error: Unimplemented state. Please contact author of program.'))

        # Remove the LONER (safety issue)
        if len(states) > 1:
            states.pop(0)

    # Handles mouse
    states[-1].handlemousestate(pygame.mouse.get_pos(), 'O')

    for evt in pygame.event.get():
        if evt.type == QUIT:
            mode = game.Mode.exiting
        elif evt.type == MOUSEBUTTONDOWN:
            states[-1].handlemousestate(pygame.mouse.get_pos(), 'P')
        elif evt.type == MOUSEBUTTONUP:
            states[-1].handlemousestate(pygame.mouse.get_pos(), 'U')

    # Update and draw
    states[-1].update()
    states[-1].draw()

    clock.tick(60)
    pygame.display.flip()


pygame.mixer.quit()
pygame.quit()
