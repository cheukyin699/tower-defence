# File: menus.py
import pygame
import towers
import enemy
from utils import *
from sprites import *

class GameMenu(pygame.sprite.Sprite):
    '''
    The class responsible for responding to
    clicks on the menu
    The in-game menu will be positioned on the
    bottom of the screen

    Buttons that should be included:
    - Buy tower(s) selection
    - Upgrade menu
    '''
    def __init__(self, surface, rmanager, gs):
        pygame.sprite.Sprite.__init__(self)

        self.rmanager = rmanager
        self.gs = gs

        self.tlist = pygame.sprite.Group()
        if self.gs.state != Mode.freeplay:
            self.elist = pygame.sprite.Group()

        self.image = pygame.surface.Surface((surface.get_rect().w, surface.get_rect().h*.25))
        self.image.fill(Color.white)
        self.rect = self.image.get_rect()
        self.rect.y = surface.get_rect().h*.75

        # Have focus on selected tower. If focus is None,
        # menu displays normal menu stuff
        self.focus = None

        # Drag selected tower (buy it)
        self.drag = None

        # The play button (starts rounds)
        if self.gs.state == Mode.freeplay:
            self.play_bt = Button.sMade(type='button', text='Play', sprite='Button1', sound='wood-click',
                    pos=[self.rect.w*.75, 0], size=[80, self.rect.h], rmanager=self.rmanager)
            self.play_bt.callback(self.gs.nextWave)

        # Depressed enemy button
        if self.gs.state != Mode.freeplay:
            self.depressed_enemy = None

        # Init towers
        ind = 0
        for data in self.rmanager.data['towers'].itervalues():
            t = towers.Tower(self.rmanager, data, (50*ind+100, 5), self.gs)
            self.tlist.add(t)
            ind += 1

        # Init enemies
        if self.gs.state != Mode.freeplay:
            ind = 0
            # It is an array, so it is different
            for data in self.rmanager.data['enemies']:
                e = enemy.bEnemy(self.rmanager, data, (30*ind+100, 55))
                self.elist.add(e)
                ind += 1

    def drawMoney(self):
        text = "$" + str(self.gs.money)
        if self.gs.state == Mode.sandbox:
            text = "$$$$"
        moneylbl = self.rmanager.fonts['monospace'].render(text, True, Color.green)
        self.image.blit(moneylbl, (0,0))

    def drawLives(self):
        text = "LF:" + str(self.gs.lives)
        if self.gs.state == Mode.sandbox:
            text = "<3<3"
        liveslbl = self.rmanager.fonts['monospace'].render(text, False, Color.red)
        self.image.blit(liveslbl, (0, liveslbl.get_rect().h))

    def draw(self, surface):
        self.image.fill(Color.white)

        # Draw some labels first
        self.drawMoney()
        self.drawLives()

        if self.focus == None:
            # Display the main game menu
            # Draw some other stuffs
            # Draw towers
            self.tlist.draw(self.image)
            # If in sandbox/multiplayer, draw enemies (to buy)
            if self.gs.state != Mode.freeplay:
                self.elist.draw(self.image)

            # If you are dragging
            if self.drag != None:
                mp = list(pygame.mouse.get_pos())
                mp[0] -= self.drag.rect.w/2
                mp[1] -= self.drag.rect.h/2
                surface.blit(self.drag.orgimage, mp)

            # Update play button
            if self.gs.state == Mode.freeplay:
                self.play_bt.update()
                # Draw play button
                self.play_bt.draw(self.image)
        else:
            # If you have focused on some random tower,
            # display the upgrade menu
            self.focus.draw_to_menu(self.image)
            # Draw the range (without alpha)
            pygame.draw.circle(surface, Color.white, (self.focus.rect.centerx,self.focus.rect.centery), self.focus.range, 1)

        surface.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        if self.focus and self.focus.sold:
            self.focus = None

        if self.gs.state == Mode.sandbox and self.depressed_enemy:
            spawnen = enemy.get_correct_enemy_type(self.depressed_enemy.eid)(self.depressed_enemy)
            spawnen.path = self.rmanager.data['maps'][self.gs.currentmap]['path']
            self.gs.enemies.append(spawnen)

    def handlemousestate(self, (mx, my), mstate='N'):
        if self.focus == None:
            if self.drag != None and mstate == 'U':
                self.drag = None
            elif mstate == 'P':
                for t in self.tlist.sprites():
                    if t.rect.collidepoint(mx,my) and (self.gs.money-t.cost >= 0 or self.gs.state == Mode.sandbox):
                        # If you clicked the tower, just set dragged tower
                        # and break out of loop, because it is impossible to
                        # click on multiple ones
                        self.drag = t
                        break
            if self.gs.state == Mode.freeplay:
                if self.play_bt.rect.collidepoint(mx,my):
                    self.play_bt.state = mstate
                elif self.play_bt.state == 'O':
                    self.play_bt.state = 'N'
            else:
                for e in self.elist.sprites():
                    if e.rect.collidepoint(mx,my) and (self.gs.money-e.cost >= 0 or self.gs.state == Mode.sandbox) and mstate == 'P':
                        # If you clicked on the enemy, just buy it (in multiplayer) and
                        # send it out on your own side (if sandbox)
                        spawnen = enemy.get_correct_enemy_type(e.eid)(e)
                        spawnen.path = self.rmanager.data['maps'][self.gs.currentmap]['path']
                        self.depressed_enemy = e
                        self.gs.enemies.append(spawnen)
                    elif e.rect.collidepoint(mx,my) and (self.gs.money-e.cost >= 0 or self.gs.state == Mode.sandbox) and mstate == 'U':
                        self.depressed_enemy = None
        else:
            # Handle focus
            self.focus.handlemousestate((mx, my), mstate)
