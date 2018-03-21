import pygame, time, random
from vector import Vector

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, vel, acc, width=5,height=5,color=(255,0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width,height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.pos = Vector(pos.x,pos.y)
        self.vel = Vector(vel.x,vel.y)
        self.acc = Vector(acc.x,acc.y)
        self.width = width
        self.height = height
        self.name = "Projectile"
        self.dead = False
        self.damage = 25

    def update(self):
        self.vel.addV(self.acc)
        self.vel.round(2)
        self.pos.addV(self.vel)
        self.rect.topleft = self.pos.get()
        if self.pos.boundedX(self.pos.x) != 0 or self.pos.boundedY(self.pos.y) != 0:
            self.dead = True

class Bullet(Projectile):
    def __init__(self, pos, vel, acc, width=10, height=10, color=(255,0,0)):
        super(Bullet, self).__init__(pos,vel,acc,width,height,color)
        self.spriteSheet = pygame.image.load("images/beams.png").convert_alpha()
        self.image = pygame.Surface((16,16),flags=pygame.SRCALPHA)
        self.image.blit(self.spriteSheet, (0,0), (40,2,20,20))
        self.image = pygame.transform.scale(self.image,(width,height))
        self.rect = self.image.get_rect()
        self.name = "Bullet"

class SoftBullet(Bullet):
    def __init__(self, pos, vel, acc, width=10,height=10,color=(255,0,0)):
        super(SoftBullet,self).__init__(pos, vel, acc, width, height, color)
        self.image = pygame.Surface((16,16),flags=pygame.SRCALPHA)
        self.image.blit(self.spriteSheet, (0,0), (37,116,16,16))
        self.image = pygame.transform.scale(self.image,(width,height))
        self.name = "Soft Bullet"
        self.damage = 5

class HardBullet(Bullet):
    def __init__(self, pos, vel, acc, width=10,height=10,color=(255,0,0)):
        super(HardBullet,self).__init__(pos, vel, acc, width, height, color)
        self.image = pygame.Surface((16,16),flags=pygame.SRCALPHA)
        self.image.blit(self.spriteSheet, (0,0), (37,116,16,16))
        self.image = pygame.transform.scale(self.image,(width,height))
        self.name = "Hard Bullet"
        self.damage = 10
