# File: states.py
import pygame
from sprites import *
from utils import *
from menus import *
from jsonmaputils import TMXJsonMap

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
    The class for handling the splash screen state.
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
    The class for handling the menu state.
    '''
    def __init__(self, surface, rmanager):
        State.__init__(self, surface, rmanager, state=Mode.menu)

        self.layout = self.rmanager.menulayout
        self.sprites = pygame.sprite.Group()

        for key, data in self.layout.iteritems():
            if data['type'] == 'button':
                bt = Button(data, rmanager)
                if key == 'play-bt':
                    bt.callback(self.tog_play_menu)
                elif key == 'freeplay-bt':
                    bt.callback(self.changestate, Mode.freeplay)
                elif key == 'sandbox-bt':
                    bt.callback(self.changestate, Mode.sandbox)
                elif key == 'multiplayer-bt':
                    bt.callback(self.changestate, Mode.multiplayer)
                elif key == 'quit-bt':
                    bt.callback(self.changestate, Mode.exiting)
                self.sprites.add(bt)
            elif key == 'background':
                s = Sprite(data, rmanager)
                self.bg = s
            else:
                self.sprites.add(Sprite(data, rmanager))

    def tog_play_menu(self):
        '''
        Toggles the play menu when you click the
        play button
        '''
        for s in self.sprites.sprites():
            if s.group == 'play':
                s.visible = not s.visible

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

        self.surface.blit(self.bg.image, (0, 0))
        for s in self.sprites.sprites():
            s.draw(self.surface)

    def update(self):
        self.sprites.update()

class GameState(State):
    '''
    The class for handling the playing state
    '''
    def __init__(self, surface, rmanager, state):
        State.__init__(self, surface, rmanager, state=state)

        # All sprite groups
        self.towers = pygame.sprite.Group()
        self.enemies = []
        self.projectiles = pygame.sprite.Group()
        self.fx = pygame.sprite.Group()
        self.gm = GameMenu(self.surface, self.rmanager, self)

        # The backdrop/map
        # TODO: Let the player select which map they want to play
        self.bg = TMXJsonMap('res/maps/grass-map1.json')

        # Some properties
        self.lives = 100
        self.money = 650

        # The wave that you are currently on
        self.wave = 0
        # The index of the wave that you are currently on
        self.noen = 0
        # Count of enemies to spawn and enemy id
        self.enem_on = [0,0]
        # Should I spawn enemies?
        self.runthru_enemy = False
        # Timer
        self.en_cd = 0
        # Crowd density
        self.density = 50
        # End the game?
        self.end_game = False

        # TODO: Grab the current map
        self.currentmap = "grass-map1"

    def draw(self):
        self.surface.fill(Color.black)

        # Draw the background on first
        self.surface.blit(self.bg.layers['background'].image, (0,0))

        if not self.end_game:
            for i in xrange(len(self.enemies)):
                self.enemies[i].draw(self.surface)
            self.towers.draw(self.surface)
            self.projectiles.draw(self.surface)
            self.fx.draw(self.surface)
            self.gm.draw(self.surface)

        # Check for dragging something
        if self.gm.drag != None:
            mp = list(pygame.mouse.get_pos())
            # Draw the range without ALPHA
            overlap = False
            for t in self.towers.sprites():
                if t.rect.collidepoint(mp[0], mp[1]):
                    overlap = True
                    break
            col = Color.white
            if overlap:
                col = Color.red
            pygame.draw.circle(self.surface, col, (mp[0],mp[1]), self.gm.drag.range, 1)
            mp[0] -= self.gm.drag.rect.w / 2
            mp[1] -= self.gm.drag.rect.h / 2
            self.surface.blit(self.gm.drag.orgimage, mp)

        pygame.draw.circle(self.surface, Color.red, [32,240], 1)

    def update(self):
        if self.runthru_enemy and self.en_cd <= 0 and self.state != Mode.sandbox:
            if self.noen >= len(self.rmanager.data['waves'][self.wave]) and self.enem_on[0] <= 0:
                # If done spawning enemies
                # And you have cleared the enemy buffer
                self.noen = 0
                self.wave += 1
                self.runthru_enemy = False
            elif self.enem_on[0] > 0:
                en = enemy.get_correct_enemy_type(self.enem_on[1])(enemy.bEnemy(self.rmanager,self.rmanager.data['enemies'][self.enem_on[1]], [0,0]))
                en.path = self.rmanager.data['maps'][self.currentmap]['path']
                self.enemies.append(en)
                # Subtract from enem_on[0]
                self.enem_on[0] -= 1
                # Wait 50 ticks
                self.en_cd = self.density
            else:
                enno = self.rmanager.data['waves'][self.wave][self.noen].split('x')
                ttime = self.rmanager.data['waves'][self.wave][self.noen].split(':')
                if len(enno) > 1:
                    # Set the spawn buffer
                    self.enem_on = [int(enno[0]), int(enno[1])]
                    self.noen += 1
                elif len(ttime) > 1:
                    if ttime[0] == 'T':
                        self.density = int(ttime[1])
                    self.noen += 1
        elif self.en_cd > 0 and self.state != Mode.sandbox:
            self.en_cd -= 1

        # Enemy
        for e in self.enemies:
            pe = pygame.sprite.spritecollide(e, self.projectiles, False)
            if len(pe) > 0:
                # If you collided with projectile
                for p in pe:
                    p.hit(self, e)
            if e.rect.centerx > self.SIZE[0]:
                if self.state != Mode.sandbox:
                    self.lives -= e.hp
                    e.hp = 0
                    e.offscreen = True
                    e.update(self)
                else:
                    # Just remove them if they are in sandbox
                    self.enemies.remove(e)
                    continue    # Must continue or else may cause error
            else:
                e.update(self)
            if e.hp <= 0:
                self.enemies.remove(e)

        if not self.end_game:
            self.towers.update(self.enemies)
            self.projectiles.update(self.SIZE)
            self.gm.update()
        self.fx.update()

        # Shoot stuff
        for t in self.towers.sprites():
            # Find all towers that have things to shoot
            if t.shoot != None and t.shoot != 'C':
                # Spawn a bullet at some velocity
                veloc = getVeloc((t.rect.centerx, t.rect.centery), t.shoot, t.shotveloc)
                b = t.projectile((t.rect.centerx, t.rect.centery), veloc, t.dmg, 1)
                self.projectiles.add(b)

                # Reset tower shot to None
                t.shoot = None

        # If you lose (0 lives), then go back to menu after displaying message
        if self.lives <= 0 and not self.end_game:
            ot = OverheadText(self.rmanager, 'You SUCK', [self.SIZE[0] / 2, self.SIZE[1] / 2], [200,200])
            self.fx.add(ot)
            self.fadeout = ot.life
            self.end_game = True
        if self.end_game:
            if self.fadeout <= 0:
                self.state = Mode.menu
            else:
                self.fadeout -= 1

    def nextWave(self):
        '''
        Starts the next wave when all enemies are killed
        '''
        if len(self.enemies) == 0:
            # When all enemies are killed, start next wave
            self.runthru_enemy = True

    def handlemousestate(self, (mx, my), mstate='N'):
        if mstate == 'U':
            # Check to see if you are clicking off the focused
            # tower. To click off the focused tower, click on
            # something else
            if self.gm.focus and not self.gm.rect.collidepoint(mx,my):
                self.gm.focus = None

            # Check all towers
            for t in self.towers.sprites():
                if t.rect.collidepoint(mx, my):
                    # Set the focus point
                    # Break after setting the focus point
                    self.gm.focus = t
                    break

        # Check the game menu
        if self.gm.rect.collidepoint(mx, my):
            self.gm.handlemousestate((mx, my - self.gm.rect.y), mstate)
        # Check if you are dragging something from the game menu
        # and you drop it in the screen
        if self.gm.drag != None and mstate == 'U':
            # If you've just placed down something from the menu...
            # ...and you didn't place it on top another tower
            overlap = False
            for t in self.towers.sprites():
                if t.rect.collidepoint(mx, my):
                    overlap = True
                    break
            if not overlap:
                t = self.gm.drag.tower(self.gm.drag)
                t.rect.x = mx-t.rect.w / 2
                t.rect.y = my-t.rect.h / 2
                self.towers.add(t)
                self.gm.drag = None
                # TAKE YO MONEY
                if not self.state == Mode.sandbox:
                    self.money -= t.cost
            else:
                # If you placed it on top of another
                # tower, remove and try again
                self.gm.drag = None
