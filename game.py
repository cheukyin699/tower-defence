# File: game.py
# Description: Provides useful classes and functions for the game


# CLASSES
class Mode:
    '''
    Just some normal game modes
    '''
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



# FUNCTIONS
def displaysplash(surface, rmanager, SIZE=(500,500)):
    '''
    Displays the splash screen
    '''
    # Display the statuses
    stat = rmanager.fonts['monospace'].render(rmanager.status_text, True, Color.white)
    statrect = stat.get_rect()
    # Blit into middle of screen
    surface.blit(stat, (SIZE[0]/2-statrect.w/2, SIZE[1]/2-statrect.h/2))

def displaymenu(surface, rmanager, SIZE=(500,500)):
    '''
    Displays the main menu
    '''
    pass
