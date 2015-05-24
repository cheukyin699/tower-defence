import pygame
import game

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, veloc, dmg, hp):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.surface.Surface((10,10))
        pygame.draw.circle(self.image, game.Color.red, (5,5), 5)

        self.rect = self.image.get_rect()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        self.veloc = veloc
        self.hp = hp
        self.dmg = dmg

    def update(self, size):
        if self.hp <= 0 or\
        (self.rect.centerx < 0 or self.rect.centery < 0 or self.rect.centerx > size[0] or self.rect.centery > size[1]):
            self.kill()
        self.rect.centerx += self.veloc[0]
        self.rect.centery += self.veloc[1]

    def hit(self, gs, enem):
        if self.hp > 0 and enem.hp > 0:
            enem.hp -= self.dmg
            self.hp -= 1

class Missile(Bullet):
    def __init__(self, pos, veloc, dmg, hp):
        Bullet.__init__(self, pos, veloc, 1, 1)

        # The explosion radius
        self.exp_rad = 100
        
    def hit(self, gs, enem):
        for e in gs.enemies:
            dist = game.getDist(self.rect, e.rect)
            if dist <= self.exp_rad and e.hp > 0:
                e.hp -= self.dmg
        # Add special effects
        data = {"type": "sprite", "sprite": "explosion", "text": '', "size": [self.exp_rad*2, self.exp_rad*2],
                "pos": [self.rect.centerx,self.rect.centery], "life": 10}
        gs.fx.add(game.Explosion(data, gs.rmanager))
        # You have already exploded (died)
        self.hp = 0

    def update(self, size):
        Bullet.update(self, size)