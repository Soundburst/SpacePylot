from vector import Vector
import pygame, ships, random, time

class GameEnvironment:
    def __init__(self,WIN_WIDTH,WIN_HEIGHT,BGWIDTH,BGHEIGHT,AI=False):
        self.WIN_WIDTH = WIN_WIDTH
        self.WIN_HEIGHT = WIN_HEIGHT
        self.BGWIDTH = BGWIDTH
        self.BGHEIGHT = BGHEIGHT
        self.score = 0
        self.multiplier = 1.0
        self.upgrading = False
        self.won = False
        self.AI = AI
        self.endTime = None
        if self.AI:
            self.pShip = ships.AutoPlayer(BGWIDTH/2,BGHEIGHT/2,64,64,
                                          None)
        else:
            self.pShip = ships.Player(BGWIDTH/2, BGHEIGHT/2, 64, 64)
        self.pShip.setBounds(0,0,BGWIDTH-10,BGHEIGHT-10)
        self.slack = self.cameraUpdate(self.pShip)
        self.initWaves()

    def makeShip(self, enemy):
        e = enemy(random.randint(20,self.BGWIDTH-90),
                            random.randint(20,self.BGHEIGHT-90), 64, 64,
                            self.pShip)

        e.setBounds(0,0,self.BGWIDTH-10,self.BGHEIGHT-10)

        while e.collideEnt(self.pShip) or self.inScreen(e.pos):
            e = enemy(random.randint(20,self.BGWIDTH-90),
                        random.randint(20,self.BGHEIGHT-90), 64, 64,
                            self.pShip)

            e.setBounds(0,0,self.BGWIDTH-10,self.BGHEIGHT-10)

        return e

    def initWaves(self):
        self.waves = []
        #tutorial wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        e = ships.StillShip(self.BGWIDTH/2+200,self.BGHEIGHT/2,64,64,self.pShip)
        shipGroup.add(e)
        self.waves[0] = Wave(enemies, 1, 1, shipGroup, 0, self)
        #first wave, fifteen enemies
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 4
        for i in range(8):
            e = self.makeShip(ships.Enemy)

            if i <= maxSpawn-1:
                shipGroup.add(e)
            else:
                enemies.append(e)

        self.waves[1] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #second wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 5
        for i in range(12):
            #regular enemy
            if i%3 != 0:
                e = self.makeShip(ships.Enemy)
            #quick enemy
            else:
                e = self.makeShip(ships.Quickie)

            enemies.append(e)

        self.waves[2] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #third wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 2
        for i in range(8):
            if i % 3 != 0:
                e = self.makeShip(ships.Trireme)
            else:
                e = self.makeShip(ships.Enemy)

            enemies.append(e)

        self.waves[3] = Wave(enemies, maxSpawn, 0, shipGroup, 60, self)

        #fourth wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 5
        for i in range(15):
            if i % 3 == 0:
                e = self.makeShip(ships.Enemy)
            else:
                e = self.makeShip(ships.Quickie)

            enemies.append(e)

        self.waves[4] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)
    
        #fifth wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 5
        for i in range(15):
            if i % 4 == 0:
                e = self.makeShip(ships.Trireme)
            else:
                e = self.makeShip(ships.Quickie)

            enemies.append(e)

        self.waves[5] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #sixth wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 5
        for i in range(15):
            if i < 2:
                e = self.makeShip(ships.Enemy)
            elif i < 4:
                e = self.makeShip(ships.Quickie)
            elif i < 5:
                e = self.makeShip(ships.Trireme)
            elif i < 7:
                e = self.makeShip(ships.Enemy)
            elif i < 9:
                e = self.makeShip(ships.Quickie)
            elif i < 10:
                e = self.makeShip(ships.Trireme)
            elif i < 12:
                e = self.makeShip(ships.Enemy)
            elif i < 14:
                e = self.makeShip(ships.Quickie)
            else:
                e = self.makeShip(ships.Trireme)

            enemies.append(e)

        self.waves[6] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #seventh wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 4
        for i in range(15):
            if i == 4 or i == 9 or i == 14:
                e = self.makeShip(ships.Quickie)
            else:
                e = self.makeShip(ships.Trireme)

            enemies.append(e)

        self.waves[7] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #eighth wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 4
        for i in range(15):
            e = self.makeShip(ships.Quickie)

            enemies.append(e)

        self.waves[8] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #ninth wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 3
        for i in range(15):
            e = self.makeShip(ships.Trireme)

            enemies.append(e)

        self.waves[9] = Wave(enemies, maxSpawn, 1, shipGroup, 60, self)

        #tenth and final wave
        self.waves.append([])
        enemies = []
        shipGroup = pygame.sprite.Group()
        shipGroup.add(self.pShip)
        maxSpawn = 5
        for i in range(15):
            if i == 2 or i == 5 or i == 12:
                e = self.makeShip(ships.Enemy)
            elif i == 4 or i == 13 or i == 7:
                e = self.makeShip(ships.Trireme)
            else:
                e = self.makeShip(ships.Quickie)

            enemies.append(e)

        self.waves[10] = Wave(enemies, maxSpawn, 0, shipGroup, 60, self)

        if self.AI:
            self.currWave = 1
        else:
            self.currWave = 0
        
    def cameraUpdate(self,player):
        offset = Vector(0,0)
        if player.rect.centerx >= self.WIN_WIDTH/2 and \
           player.rect.centerx + self.WIN_WIDTH/2 < self.BGWIDTH:
            offset.x = player.rect.centerx - self.WIN_WIDTH/2
            
        elif player.rect.centerx >= self.WIN_WIDTH/2 and \
           player.rect.centerx + self.WIN_WIDTH/2 >= self.BGWIDTH:
            offset.x = self.BGWIDTH-self.WIN_WIDTH
            
        if player.rect.centery >= self.WIN_HEIGHT/2 and \
           player.rect.centery + self.WIN_HEIGHT/2 < self.BGHEIGHT:
            offset.y = player.rect.centery - self.WIN_HEIGHT/2
            
        elif player.rect.centery >= self.WIN_HEIGHT/2 and \
             player.rect.centery + self.WIN_HEIGHT/2 >= self.BGHEIGHT:
            offset.y = self.BGHEIGHT-self.WIN_HEIGHT

        return offset

    def inScreen(self, pos):
        if pos.x <= self.WIN_WIDTH + self.slack.x and pos.x >= self.slack.x:
            if pos.y <= self.WIN_HEIGHT + self.slack.y and pos.y >= self.slack.y:
                return True
        return False

    def reset(self):
        if self.AI:
            self.pShip = ships.AutoPlayer(self.BGWIDTH/2,self.BGHEIGHT/2,64,64,
                                          None)
        else:
            self.pShip = ships.Player(self.BGWIDTH/2, self.BGHEIGHT/2, 64, 64)
        self.pShip.setBounds(0,0,self.BGWIDTH-10,self.BGHEIGHT-10)
        self.slack = self.cameraUpdate(self.pShip)
        self.score = 0
        self.upgrading = False
        self.won = False
        self.endTime = None
        self.initWaves()

    def rotateShip(self,pos,ship):
        #Get vector pointing from ship to mouse position
        v = Vector(pos[0]+self.slack.x-ship.rect.centerx,
                   ship.rect.centery-pos[1]-self.slack.y)
        #change to unit circle
        v.normalize()
        if ship.isAlive():
            #rotate ship based on angle between x axis, y axis, and mouse
            ship.rot_center(v.theta(False)-90)

    def update(self,up,down,left,right,mp):
        if self.AI:
            self.pShip.enemies = self.waves[self.currWave]
        else:
            self.pShip.calcAcc(up,down,left,right)
            self.rotateShip(mp,self.pShip)
            
        cShips = self.waves[self.currWave].cShips
        if self.AI:
            pName = "AutoPlayer"
        else:
            pName = "Player"
        #check collisions
        for s in cShips:
            for other in cShips:
                if other.name == pName or s.name == pName: 
                    for b in s.bullets:
                        #do damage for bullets
                        if other != s and other.collideEnt(b) and not b.dead\
                        and s.isAlive() and other.isAlive():
                            b.dead = True
                            if other.name == "Player" and self.currWave <= 5:
                                other.hit(int(b.damage*1.5*self.multiplier))
                            elif other.name != "Player":
                                other.hit(b.damage)
                            else:
                                other.hit(int(b.damage)*self.multiplier)

                if s.name == pName and s != other and s.collideEnt(other)\
                   and other.isAlive():
                    #triremes do more damage to player
                    if other.name == "Trireme":
                        s.hit(int(20*self.multiplier))
                        other.hit(100)
                    elif other.name == "StillShip":
                        pass
                    else:
                        s.hit(int(10*self.multiplier))
                        
                    if s.invulFrames == 0:
                        s.invulFrames = 60

        cShips.update()
        self.waves[self.currWave].update()

        #destroy dead ships
        for s in cShips:
            if s.isDead():
                if s.name != pName:
                    self.score += int(s.worth*self.multiplier)
                else:
                    self.endTime = time.time()
                cShips.remove(s)

        self.slack = self.cameraUpdate(self.pShip)


        #go to next wave
        mywave = self.waves[self.currWave]
        if self.currWave < len(self.waves)-1:
            if mywave.isDone():
                if mywave.deathtime == None:
                    mywave.deathtime = time.time()
                    self.upgrading = True
                    self.pShip.health = self.pShip.maxHealth

        #win game if you beat the last wave
        if self.currWave == len(self.waves)-1 and mywave.isDone():
            if mywave.deathtime == None:
                mywave.deathtime = time.time()
            elif time.time()-mywave.deathtime >= 2:
                self.won = True

class Wave:
    def __init__(self, enemies, maxSpawn, spawnRate, waveGroup, waveTime, parent):
        #queued enemies
        self.qEnemies = enemies
        self.maxSpawn = maxSpawn
        self.spawnRate = spawnRate
        self.startSpawn = time.time()
        self.waveTime = waveTime
        #current ships
        self.cShips = waveGroup
        self.parent = parent
        #death time used for delay between finished wave and upgrade screen
        self.deathtime = None

    def correctPositions(self):
        for e in self.cShips:
            if e.name != "Player":
                ePos = Vector(e.rect.centerx,e.rect.centery)
                while self.parent.inScreen(ePos):
                    e.pos.x = random.randint(0,self.parent.BGWIDTH)
                    e.pos.y = random.randint(0,self.parent.BGHEIGHT)
                    e.rect.topleft = (e.pos.x,e.pos.y)
                    ePos = Vector(e.rect.centerx,e.rect.centery)

    def update(self):
        #move ships from the queue into the active ships, as long as
        #the minimum amount of time has passed and there aren't too
        #many enemies already on the screen
        if len(self.qEnemies) > 0 and len(self.cShips) <= self.maxSpawn\
           and time.time() - self.startSpawn >= self.spawnRate:
            newEnemy = self.qEnemies.pop(0)
            ePos = Vector(newEnemy.rect.centerx,newEnemy.rect.centery)
            while self.parent.inScreen(ePos):
                newEnemy.pos.x = random.randint(0,self.parent.BGWIDTH)
                newEnemy.pos.y = random.randint(0,self.parent.BGHEIGHT)
                newEnemy.rect.topleft = (newEnemy.pos.x,newEnemy.pos.y)
                ePos = Vector(newEnemy.rect.centerx,newEnemy.rect.centery)

            self.cShips.add(newEnemy)
            self.startSpawn = time.time()

    def isDone(self):
        if self.numEnemies() == 0:
            return True
        else:
            return False

    def numEnemies(self):
        total = 0
        total += len(self.qEnemies)
        total += len(self.cShips)
        if not self.parent.pShip.isDead():
            total -= 1

        return total

    def getBonus(self):
        totalTime = self.deathtime-self.startSpawn
        if totalTime < self.waveTime:
            return int(self.waveTime-totalTime)*1000
