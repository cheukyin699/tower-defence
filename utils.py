# File: utils.py
import math

def getVeloc(a, b, veloc):
    '''
    a: [x,y]
    b: [x,y]
    veloc: The velocity scalar

    Uses the 'brute force' method for turning the angles.

    Returns list of 2 dimensions for a going to b
    '''
    # First, get angle (radians)
    if b[0] - a[0] == 0:
        angle = 0
    else:
        angle = math.atan(float(a[1] - b[1]) / (b[0] - a[0]))
    vx = int(veloc * math.cos(angle))
    vy = int(veloc * math.sin(angle))
    if b[0] - a[0] > 0 and a[1] - b[1] > 0:
        vy = -vy
    elif b[0] - a[0] < 0 and a[1] - b[1] > 0:
        vx = -vx
    elif b[0] - a[0] < 0 and a[1] - b[1] < 0:
        vx = -vx
    elif b[0] - a[0] > 0 and a[1] - b[1] < 0:
        vy = -vy
    return [vx,vy]

def getAngle(a, b):
    '''
    a: [x,y]
    b: [x,y]

    Uses the 'brute force' method for turning the angles.

    Returns the angle
    '''
    # First, get relative angle (radians)
    if b[0] - a[0] == 0:
        angle = 0
    else:
        angle = math.degrees(math.atan(float(a[1] - b[1]) / (b[0] - a[0])))
    if b[0] - a[0] > 0 and a[1]-b[1]>0:
        angle -= 90
    elif b[0] - a[0] < 0 and a[1] - b[1] > 0:
        angle += 90
    elif b[0] - a[0] < 0 and a[1] - b[1] < 0:
        angle += 90
    elif b[0] - a[0] > 0 and a[1] - b[1] < 0:
        angle -= 90
    return angle

def getDist(a, b):
    '''
    a: rect
    b: rect

    Returns the straight line distance between the 2 points
    '''
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class Mode:
    '''
    Just some normal game modes (Treat this as an enum)
    '''
    errormsg = -1
    splash = 0
    menu = 1
    freeplay = 2
    sandbox = 3
    multiplayer = 4
    config = 5
    exiting = 6

class Color:
    '''
    Some plain colors
    '''
    black =     (  0,   0,   0)
    white =     (255, 255, 255)
    red =       (200,   0,   0)
    green =     (  0, 200,   0)
    blue =      (  0,   0, 200)

    yellow =    (255, 255,   0)
