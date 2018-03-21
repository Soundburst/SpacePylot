import pygame, time, math
from vector import Vector
from projectiles import *

class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255,0,255)):
        pygame.sprite.Sprite.__init__(self)
        self.origImage = pygame.Surface((width,height))
        self.origImage.fill(color)
        self.image = self.origImage.copy()
        self.blank = pygame.Surface([width,height], pygame.SRCALPHA, 32)
        self.blank = self.blank.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.acc = Vector(0, 0)
        self.width = width
        self.height = height
        self.name = "Ship"
        self.degrees = 0
        self.maxHealth = 100
        self.health = 100
        #-1 means alive, 0 means dying (animation occurring), 1 means dead
        self.dead = -1
        #blinkCount used for tracking invulnerability animation
        self.blinkCount = 10
        self.currImg = "sprite"
        self.rotation = 0
        #60 frames ~= 1 second
        self.invulFrames = 0

    def isAlive(self):
        if self.dead == -1:
            return True

    def isDead(self):
        if self.dead == 1:
            return True

    def deathAnimation(self):
        self.bullets = []
        #if ship has just died
        if self.invulFrames == 0 and self.dead == -1:
            self.dead = 0
            self.invulFrames = 60
            self.vel = Vector(0,0)
            self.acc = Vector(0,0)

        self.blink()
        if self.invulFrames == 0:
            self.dead = 1

    def blink(self):
        if self.invulFrames > 0:
            self.invulFrames -= 1
            if self.currImg == "blank":
                self.image = self.blank.copy()
            if self.blinkCount < 5:
                self.blinkCount += 1
            else:
                self.cycleSprite()
                self.blinkCount = 0
        elif self.currImg == "blank":
            self.currImg = "sprite"
            self.image = self.origImage.copy()
            self.rot_center(self.rotation)

    def cycleSprite(self):
        if self.currImg == "sprite":
            self.currImg = "blank"
            self.image = self.blank.copy()
        elif self.currImg == "blank":
            self.currImg = "sprite"
            self.image = self.origImage.copy()
            self.rot_center(self.rotation)

    def rot_center(self,angle):
        """rotate an image while keeping its center and size"""
        self.rotation = angle
        orig_rect = self.origImage.get_rect()
        rot_image = pygame.transform.rotate(self.origImage, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image

    def update(self):
        self.vel.addV(self.acc)
        #if ship stops moving, slow it down
        if self.acc.x == 0:
            self.vel.x *= .95
        if self.acc.y == 0:
            self.vel.y *= .95

        #fix decimal rounding problems
        self.vel.round(2)
        if abs(self.vel.x) == 0.1:
            self.vel.x = 0
        if abs(self.vel.y) == 0.1:
            self.vel.y = 0

        
        self.pos.addV(self.vel)
        self.rect.topleft = self.pos.get()
        
        if self.health <= 0 and not self.isAlive():
            self.deathAnimation()

    def setBounds(self,minX=None,minY=None,maxX=None,maxY=None):
        self.pos.lBound(minX,minY)
        self.pos.uBound(maxX-self.width,maxY-self.height)

    def hit(self,damage):
        if self.invulFrames == 0:
            self.health -= damage

    def calcAcc(self, up, down, left, right):
        tempAcc = Vector(0,0)
        tempVel = self.vel.getV()
        tempPos = self.pos.getV()
        boundX = self.pos.boundedX(self.pos.x)
        boundY = self.pos.boundedY(self.pos.y)
        #this block of if statements tests if a direction is being pressed
        #then accounts for if the ship is hitting a wall, in which case
        #its acceleration will be set to 0
        if up:
            if boundY > 0:
                self.vel.y = 0
                tempAcc.add(0,-1)
            elif boundY == 0:
                tempAcc.add(0,-1)
            else:
                self.vel.y = 0
        if down:
            if boundY < 0:
                self.vel.y = 0
                tempAcc.add(0,1)
            elif boundY == 0:
                tempAcc.add(0,1)
            else:
                self.vel.y = 0
        if left:
            if boundX > 0:
                self.vel.x = 0
                tempAcc.add(-1,0)
            elif boundX == 0:
                tempAcc.add(-1,0)
            else:
                self.vel.x = 0
        if right:
            if boundX < 0:
                self.vel.x = 0
                tempAcc.add(1,0)
            elif boundX == 0:
                tempAcc.add(1,0)
            else:
                self.vel.x = 0

        tempAcc.dot(.25)

        self.acc = tempAcc

    def collideEnt(self, entity):
        r1 = self.rect
        r2 = entity.rect
        if r1.x < r2.x + r2.width and r1.x + r1.width > r2.x and\
           r1.y < r2.y + r2.height and r1.height + r1.y > r2.y:
            return True
        else:
            return False

    def bounce(self, entity):
        r1 = self.rect
        r2 = entity.rect
        #creates an imaginary rectangle, containing the area in which
        #the rectangles are colliding
        intersectT = max(r1.top,r2.top)
        intersectB = min(r1.bottom,r2.bottom)
        intersectL = max(r1.left,r2.left)
        intersectR = min(r1.right,r2.right)
        #determines which sides are colliding, and modifies velocities
        #accordingly
        if intersectT <= intersectB and intersectL <= intersectR:
            if (intersectR-intersectL > intersectB-intersectT):
                if r1.bottom < r2.bottom:
                    self.pos.y = r2.top-r1.height
                else:
                    self.pos.y = r2.top+r1.height
                #self.vel.y *= -1
                #self.acc.y = 0

            if (intersectR-intersectL < intersectB-intersectT):
                if r1.right > r2.right:
                    self.pos.x = r2.left+r1.width
                else:
                    self.pos.x = r2.left-r1.width
                #self.acc.x = 0
                #self.vel.x *= -1

            if (intersectR-intersectL == intersectB-intersectT):
                if r1.bottom < r2.bottom:
                    self.pos.y = r2.top-r1.height
                else:
                    self.pos.y = r2.top+r1.height
                
                if r1.right > r2.right:
                    self.pos.x = r2.left+r1.width
                else:
                    self.pos.x = r2.left-r1.width
                #self.acc.x = self.acc.y = 0
                #self.vel.x *= -1
                #self.vel.y *= -1

    def edgePos(self, theta):
        rect = self.rect
        if theta == 90:
            x = rect.centerx
            y = rect.top
        elif theta == 270:
            x = rect.centerx
            y = rect.bottom
        elif theta == 0 or theta == 360:
            x = rect.right
            y = rect.centery
        elif theta == 180:
            x = rect.left
            y = rect.centery
        elif theta > 315 or theta < 45:
            x = rect.right
            y = rect.centery-int((rect.right-rect.centerx)*math.tan(math.radians(theta)))
        elif theta == 45:
            x = rect.right
            y = rect.top
        elif theta > 45 and theta < 135:
            y = rect.top
            x = int((rect.centery-rect.top)/math.tan(math.radians(theta)))+rect.centerx
        elif theta == 135:
            x = rect.left
            y = rect.top
        elif theta > 135 and theta < 225:
            x = rect.left
            y = rect.centery+int((rect.centerx-rect.left)*math.tan(math.radians(theta)))
        elif theta == 225:
            x = rect.left
            y = rect.bottom
        elif theta > 225 and theta < 315:
            y = rect.bottom
            x = -int((rect.bottom-rect.centery)/math.tan(math.radians(theta)))+rect.centerx
        elif theta == 315:
            x = rect.right
            y = rect.bottom

        return x,y

class Player(Ship):
    def __init__(self,x, y, width, height, color=(255,0,255)):
        super(Player,self).__init__(x, y, width, height, color)
        self.origImage = pygame.image.load("images/userSpaceship.png")
        self.origImage.convert()
        self.origImage = pygame.transform.scale(self.origImage,
            (width,height))
        self.image = self.origImage.copy()
        self.name = "Player"
        self.rot_center(270)
        self.bullets = []
        self.vel.bound(5,5)
        #how fast one can shoot, determined by frames
        self.shootFreq = 25
        self.shootFrame = 1
        #self.maxHealth = 10000
        #self.health = 10000
        self.upHealth = 0
        self.upFR = 0
        self.upDmg = 0

    def applyUpgrades(self,newHealth,newFR,newDmg):
        self.upHealth = newHealth
        self.maxHealth = 100+(self.upHealth*10)
        self.health = self.maxHealth
        
        self.upFR = newFR
        
        self.upDmg = newDmg

    def update(self):
        self.shootFrame += 1
        if self.health <= 0 and not self.isDead():
            self.deathAnimation()
        else:
            self.blink()
            self.vel.addV(self.acc)
            if self.acc.x == 0:
                self.vel.x *= .95
            if self.acc.y == 0:
                self.vel.y *= .95
            self.vel.round(2)
            if abs(self.vel.x) == 0.1:
                self.vel.x = 0
            if abs(self.vel.y) == 0.1:
                self.vel.y = 0
            self.pos.addV(self.vel)
            self.rect.topleft = self.pos.get()
            for b in self.bullets:
                b.update()

            self.remDeadBullets()

    def remDeadBullets(self):
        living = []
        for b in self.bullets:
            if not b.dead:
                living.append(b)

        self.bullets = living

    def addBullet(self, toPos, slack=Vector(0,0)):
        if self.shootFrame > self.shootFreq-self.upFR:
            #shoot a bullet
            bulVel = Vector(toPos[0]+slack.x-self.rect.centerx,
                            self.rect.centery-toPos[1]-slack.y)
            bulVel.normalize()
            theta = int(bulVel.theta(False))
            x,y = self.edgePos(theta)
            pos = Vector(x,y)
            vel = Vector(toPos[0]+slack.x-self.rect.centerx,
                            toPos[1]-self.rect.centery+slack.y)
            #change to unit circle (direction)
            vel.normalize()
            #ensures bullet cannot be stationary
            if vel.x == 0 and vel.y == 0:
                vel.y = 1
            #increase speed of bullet
            vel.dot(10)
            acc = Vector(0,0)
            newBul = Bullet(pos,vel,acc)
            #damage upgrades
            newBul.damage += (self.upDmg*2)
            maxX = self.pos.uBoundX+self.width
            maxY = self.pos.uBoundY+self.height
            newBul.pos.lBound(0,0)
            newBul.pos.uBound(maxX-newBul.width,maxY-newBul.height)
            self.bullets.append(newBul)
            self.shootFrame = 1

class Enemy(Ship):
    def __init__(self,x, y, width, height, pShip, color =(150,150,0)):
        super(Enemy,self).__init__(x,y,width,height,color)
        self.name = "Enemy"
        self.vel.bound(3,3)
        self.bullets = []
        #shooting details
        self.shootFreq = random.randint(80,120)
        self.shootFrame = 1
        self.origImage = pygame.image.load("images/basicEnemy.png")
        self.origImage.convert()
        self.origImage = pygame.transform.scale(self.origImage,
                        (width,height))
        
        self.image = pygame.transform.scale(self.origImage,(width,height))
        #rotation details:
        #number of degrees ship can turn in one frame
        #do NOT set above 359!! 10 is recommended
        self.rotateSpeed = 10
        self.rotation = 0
        self.rot_center(270)
        #allows enemy to always track player ship
        self.pShip = pShip
        #distance from player ship that enemy tries to stay near
        self.shipDist = [150,400]
        #value to add to player's score + money
        self.worth = 100

    def update(self):
        self.shootFrame += 1
        if self.health <= 0 and not self.isDead():
            self.deathAnimation()
        else:
            self.faceShip(self.pShip)
            #test to start shooting
            #Get vector pointing from ship to mouse position
            v = Vector(self.pShip.rect.centerx-self.rect.centerx,
                       self.rect.centery-self.pShip.rect.centery)
            #change to unit circle
            v.normalize()
            theta = v.theta(False)-90
            if theta < 0:
                theta += 360
            if abs(self.rotation-theta) < 5:
                self.shoot(theta,self.pShip)
            
            self.acc = Vector(0,0)
            self.acc.addV(self.avoidBullet(self.pShip))
            self.acc.addV(self.minimizeDist(self.pShip,self.shipDist))
            self.acc.addV(self.maximizeDist(self.pShip,self.shipDist))
            self.acc = self.randomizeAcc(self.acc)
            self.vel.addV(self.acc)
            
            if self.acc.x == 0:
                self.vel.x *= .95
            if self.acc.y == 0:
                self.vel.y *= .95
            self.vel.round(2)
            if abs(self.vel.x) == 0.1:
                self.vel.x = 0
            if abs(self.vel.y) == 0.1:
                self.vel.y = 0
                
            self.pos.addV(self.vel)
            self.rect.topleft = self.pos.get()
            for b in self.bullets:
                b.update()

            self.remDeadBullets()

    def shoot(self,theta,ship):
        if self.shootFrame > self.shootFreq:
            s = ship
            if theta < 270:
                theta = theta-270+360
            else:
                theta -= 270
            x,y = self.edgePos(theta)
            bulPos = Vector(x,y)
            bulVel = Vector(s.rect.centerx-self.rect.centerx,
                            s.rect.centery-self.rect.centery)
            if bulVel.x == 0 and bulVel.y == 0:
                bulVel.y = 1
            bulVel.normalize()
            bulVel.dot(5)
            bulAcc = Vector(0,0)
            self.shootFrame = 1
            self.addBullet(bulPos,bulVel,bulAcc)

    def addBullet(self, pos, vel, acc):
        newBul = HardBullet(pos,vel,acc)
        maxX = self.pos.uBoundX+self.width
        maxY = self.pos.uBoundY+self.height
        #print maxX,maxY
        newBul.pos.lBound(0,0)
        newBul.pos.uBound(maxX-newBul.width,maxY-newBul.height)
        self.bullets.append(newBul)

    def remDeadBullets(self):
        living = []
        for b in self.bullets:
            if not b.dead:
                living.append(b)

        self.bullets = living

    def faceShip(self,ship):
        #Get vector pointing from ship to mouse position
        v = Vector(ship.rect.centerx-self.rect.centerx,self.rect.centery-ship.rect.centery)
        #change to unit circle
        v.normalize()
        theta = v.theta(False)-90
        if theta < 0:
            theta += 360
        #rotate ship based on angle between x axis, y axis, and mouse
        self.rotate(theta)

    def rotate(self, degrees):
        degrees = int(degrees)

        clockwise = int(self.rotation - self.rotateSpeed)
        cClockwise = int(self.rotation + self.rotateSpeed)
        if clockwise < 0:
            clockwise += 360
        elif clockwise >= 360:
            clockwise -= 360

        if cClockwise < 0:
            cClockwise += 360
        elif cClockwise >= 360:
            cClockwise -= 360

        #print degrees,self.rotation,clockwise,cClockwise

        if self.rotation == degrees:
            newDegrees = degrees
        #if next step crosses the 360/0 degree line and degrees is within
        # that overlap, set newDegrees equal to degrees
        elif self.rotation < clockwise and (degrees < self.rotation\
             or degrees > clockwise):
            newDegrees = degrees
        elif self.rotation > cClockwise and (degrees > self.rotation\
             or degrees < cClockwise):
            newDegrees = degrees
        # if next step goes past desired rotation
        elif (self.rotation > degrees and clockwise < degrees) or\
             (self.rotation < degrees and cClockwise > degrees):
            newDegrees = degrees
        else:
            cw = 0
            ccw = 0

            if degrees > clockwise:
                cw = clockwise + 360-degrees
            else:
                cw = clockwise-degrees

            if degrees < cClockwise:
                ccw = 360-cClockwise+degrees
            else:
                ccw = degrees-cClockwise

            if cw < ccw:
                newDegrees = int(clockwise)
            else:
                newDegrees = int(cClockwise)

        self.rot_center(newDegrees)

    def rot_center(self,angle):
        angle = int(angle)
        self.rotation = angle
        """rotate an image while keeping its center and size"""
        orig_rect = self.origImage.get_rect()
        rot_image = pygame.transform.rotate(self.origImage, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image

    def avoidBullet(self,pShip):
        closestBullet = None
        minDistance = 0
        #find the closest bullet to the ship
        for b in pShip.bullets:
            distVect = Vector(b.rect.centerx-self.rect.centerx,
                              b.rect.centery-self.rect.centery)
            dist = distVect.length()
            stepVect = Vector(b.rect.centerx,b.rect.centery)
            stepVect.addV(b.vel)
            stepDistVect = Vector(stepVect.x-self.rect.centerx,
                                  stepVect.y-self.rect.centery)
            stepDist = stepDistVect.length()
            #dist and stepDist are used to check if bullet is
            #getting closer to ship
            if (closestBullet == None and stepDist < dist) or\
                (dist < minDistance and stepDist < dist):
                closestBullet = b
                minDistance = dist

        if closestBullet != None:
            vel = closestBullet.vel.getV()
            vel.normalize()
            normal1 = vel.getV()
            normal1.rotate(math.radians(90))
            normal2 = vel.getV()
            normal2.rotate(math.radians(-90))
            normVec1 = Vector(self.rect.centerx,self.rect.centery)
            normVec1.addV(normal1)
            normVec2 = Vector(self.rect.centerx,self.rect.centery)
            normVec2.addV(normal2)

            dist1 = Vector(closestBullet.rect.centerx-normVec1.x,
                           closestBullet.rect.centery-normVec1.y).length()
            dist2 = Vector(closestBullet.rect.centerx-normVec2.x,
                           closestBullet.rect.centery-normVec2.y).length()

            if dist1 > dist2:
                normal1.normalize()
                normal1.dot(.1)
                return normal1.getV()
            else:
                normal2.normalize()
                normal2.dot(.1)
                return normal2.getV()
        else:
            return Vector(0,0)

    def minimizeDist(self, ship, dist):
        dirVec = Vector(ship.rect.centerx-self.rect.centerx,
                        ship.rect.centery-self.rect.centery)
        l = dirVec.length()
        if l > dist[1]:
            dirVec.normalize()
            dirVec.dot(.2)
            return dirVec
        else:
            return Vector(0,0)

    def maximizeDist(self, ship, dist):
        dirVec = Vector(ship.rect.centerx-self.rect.centerx,
                        ship.rect.centery-self.rect.centery)
        l = dirVec.length()
        if l < dist[0]:
            dirVec.normalize()
            dirVec.rotate(math.radians(180))
            dirVec.dot(.2)
            return dirVec
        else:
            return Vector(0,0)

    def randomizeAcc(self, acc):
        x,y = acc.get()
        x += random.uniform(-.5,.5)
        y += random.uniform(-.5,.5)
        x = round(x,2)
        y = round(y,2)
        return Vector(x,y)

class StillShip(Enemy):
    def __init__(self,x, y, width, height, pShip, color=(255,0,255)):
        super(StillShip,self).__init__(x, y, width, height, pShip, color)
        self.worth = 0
        self.name = "StillShip"

    def update(self):
        self.shootFrame += 1
        if self.health <= 0 and not self.isDead():
            self.deathAnimation()
        else:
            self.faceShip(self.pShip)
            self.rect.topleft = self.pos.get()
        
class AutoPlayer(Enemy):
    def __init__(self, x, y, width, height, enemies, color= (255,0,255)):
        super(AutoPlayer,self).__init__(x,y,width,height,None,color)
        self.origImage = pygame.image.load("images/userSpaceship.png")
        self.origImage.convert()
        self.origImage = pygame.transform.scale(self.origImage,
            (width,height))
        self.image = self.origImage.copy()
        self.name = "AutoPlayer"
        self.enemies = enemies
        self.pastEnemy = None
        self.rot_center(270)
        self.vel.bound(5,5)
        self.shootFreq = 30

    def addBullet(self, pos, vel, acc):
        vel.dot(2)
        newBul = Bullet(pos,vel,acc)
        maxX = self.pos.uBoundX+self.width
        maxY = self.pos.uBoundY+self.height
        #print maxX,maxY
        newBul.pos.lBound(0,0)
        newBul.pos.uBound(maxX-newBul.width,maxY-newBul.height)
        self.bullets.append(newBul)

    def getTarget(self):
        for ship in self.enemies.cShips:
            if ship.name != "AutoPlayer":
                self.pastEnemy = ship
                return ship

        return self.pastEnemy

    def update(self):
        target = self.getTarget()
        self.shootFrame += 1
        if self.health <= 0 and not self.isDead():
            self.deathAnimation()
        else:
            self.faceShip(target)
            self.blink()
            #test to start shooting
            #Get vector pointing from ship to mouse position
            v = Vector(target.rect.centerx-self.rect.centerx,
                       self.rect.centery-target.rect.centery)
            #change to unit circle
            v.normalize()
            theta = v.theta(False)-90
            if theta < 0:
                theta += 360
            if abs(self.rotation-theta) < 5:
                self.shoot(theta,target)
            
            self.acc = Vector(0,0)
            self.acc.addV(self.avoidBullet(target))
            self.acc.addV(self.minimizeDist(target,self.shipDist))
            self.acc.addV(self.maximizeDist(target,self.shipDist))
            self.acc = self.randomizeAcc(self.acc)
            self.vel.addV(self.acc)
            
            if self.acc.x == 0:
                self.vel.x *= .95
            if self.acc.y == 0:
                self.vel.y *= .95
            self.vel.round(2)
            if abs(self.vel.x) == 0.1:
                self.vel.x = 0
            if abs(self.vel.y) == 0.1:
                self.vel.y = 0
                
            self.pos.addV(self.vel)
            self.rect.topleft = self.pos.get()
            for b in self.bullets:
                b.update()

            self.remDeadBullets()

class Quickie(Enemy):
    def __init__(self, x, y, width, height, pShip, color= (255,0,255)):
        super(Quickie,self).__init__(x,y,width,height,pShip,color)
        self.name = "Quickie"
        self.vel.bound(5,5)
        self.shipDist = [100,150]
        self.worth = 150
        self.shootFreq = 50

        self.origImage = pygame.image.load("images/quickieEnemy.png")
        self.origImage.convert()
        self.origImage = pygame.transform.scale(self.origImage,
                        (width,height))
        
        self.image = pygame.transform.scale(self.origImage,(width,height))

    def avoidBullet(self, ship):
        closestBullet = None
        minDistance = 0
        #find the closest bullet to the ship
        for b in self.pShip.bullets:
            distVect = Vector(b.rect.centerx-self.rect.centerx,
                              b.rect.centery-self.rect.centery)
            dist = distVect.length()
            stepVect = Vector(b.rect.centerx,b.rect.centery)
            stepVect.addV(b.vel)
            stepDistVect = Vector(stepVect.x-self.rect.centerx,
                                  stepVect.y-self.rect.centery)
            stepDist = stepDistVect.length()
            #dist and stepDist are used to check if bullet is
            #getting closer to ship
            if (closestBullet == None and stepDist < dist) or\
                (dist < minDistance and stepDist < dist):
                closestBullet = b
                minDistance = dist

        if closestBullet != None:
            vel = closestBullet.vel.getV()
            vel.normalize()
            normal1 = vel.getV()
            normal1.rotate(math.radians(90))
            normal2 = vel.getV()
            normal2.rotate(math.radians(-90))
            normVec1 = Vector(self.rect.centerx,self.rect.centery)
            normVec1.addV(normal1)
            normVec2 = Vector(self.rect.centerx,self.rect.centery)
            normVec2.addV(normal2)

            dist1 = Vector(closestBullet.rect.centerx-normVec1.x,
                           closestBullet.rect.centery-normVec1.y).length()
            dist2 = Vector(closestBullet.rect.centerx-normVec2.x,
                           closestBullet.rect.centery-normVec2.y).length()

            if dist1 > dist2:
                normal1.normalize()
                normal1.dot(.3)
                return normal1.getV()
            else:
                normal2.normalize()
                normal2.dot(.3)
                return normal2.getV()
        else:
            return Vector(0,0)

    def addBullet(self, pos, vel, acc):
        vel.dot(2)
        newBul = SoftBullet(pos,vel,acc)
        maxX = self.pos.uBoundX+self.width
        maxY = self.pos.uBoundY+self.height
        #print maxX,maxY
        newBul.pos.lBound(0,0)
        newBul.pos.uBound(maxX-newBul.width,maxY-newBul.height)
        self.bullets.append(newBul)

    def minimizeDist(self, ship, dist):
        dirVec = Vector(ship.rect.centerx-self.rect.centerx,
                        ship.rect.centery-self.rect.centery)
        l = dirVec.length()
        #determine if there will be a collision with the player
        posCopy = self.pos.getV()
        velCopy = self.vel.getV()
        accCopy = self.acc.getV()
        velCopy.addV(accCopy)
        posCopy.addV(velCopy)
        newDirVec = Vector(ship.rect.centerx-posCopy.x+32,
                        ship.rect.centery-posCopy.y+32)
        newL = newDirVec.length()

        if l > dist[1] and newL > dist[1]:
            dirVec.normalize()
            dirVec.dot(.5)
            return dirVec
        else:
            return Vector(0,0)

    def maximizeDist(self, ship, dist):
        dirVec = Vector(ship.rect.centerx-self.rect.centerx,
                        ship.rect.centery-self.rect.centery)
        l = dirVec.length()
        if l < dist[0]:
            dirVec.normalize()
            dirVec.rotate(math.radians(180))
            dirVec.dot(.5)
            return dirVec
        else:
            return Vector(0,0)

class Trireme(Enemy):
    def __init__(self, x, y, width, height, pShip, color= (255,0,255)):
        super(Trireme,self).__init__(x,y,width,height,pShip,color)
        self.name = "Trireme"
        self.shipDist = [0,0]
        self.vel.bound(9,9)
        self.worth = 200
        self.health = 1
        self.maxHealth = 1

        self.origImage = pygame.image.load("images/fastEnemy.png")
        self.origImage.convert()
        self.origImage = pygame.transform.scale(self.origImage,
                        (width,height))
        
        self.image = pygame.transform.scale(self.origImage,(width,height))

    def update(self):
        self.shootFrame += 1
        if self.health <= 0 and not self.isDead():
            self.deathAnimation()
        else:
            self.faceShip(self.pShip)
            
            self.acc = Vector(0,0)
            self.acc.addV(self.minimizeDist(self.pShip,self.shipDist))

            tempAcc = self.acc.getV()
            tempAcc.dot(35)
            self.vel = tempAcc.getV()
            
            self.pos.addV(self.vel)
            self.rect.topleft = self.pos.get()
            for b in self.bullets:
                b.update()

            self.remDeadBullets()
