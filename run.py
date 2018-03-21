import pygame, sys, ships, math, random, time, environment, pickle
from pygame.locals import *
from vector import Vector
from operator import itemgetter

pygame.init()
pygame.font.init()
pygame.display.set_caption("Space Pylot")

#Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
SCREEN = pygame.display.set_mode(DISPLAY)
BUFFSCR = pygame.Surface(DISPLAY)
BG = pygame.image.load("images/tempbg.png")
#BG.fill((0,0,0))
BG.convert()
CLOCK = pygame.time.Clock()
BGWIDTH = BG.get_width()
BGHEIGHT = BG.get_height()
SCOREFONT = pygame.font.SysFont("plantagenetcherokee",20)
SCORERECT = pygame.Rect(10,10,780,22)
WAVERECT = pygame.Rect(10,40,50,22)
ENEMYRECT = pygame.Rect(10,70,50,22)
PAUSEFONT = pygame.font.SysFont("calibri",50)
PAUSERECT = pygame.Rect(335,300,100,50)
#screens, like start, pause, end, running
SCREENS = ["start","running","paused","upgrade","death","end","scoring",
           "highscore"]
currScreen = SCREENS[0]

pygame.mixer.music.load("music/!1hardcore.ogg")
pygame.mixer.music.play(-1)

#get high scores
f = file("scores.pickle","r")
HIGHSCORES = pickle.load(f)
f.close()
#game environment, use this for changing game data
game = environment.GameEnvironment(WIN_WIDTH,WIN_HEIGHT,BGWIDTH,BGHEIGHT)

class MenuItem(pygame.font.Font):
    def __init__(self, text, font=None, font_size=30,
                 font_color=WHITE, (pos_x, pos_y)=(0, 0)):
 
        pygame.font.Font.__init__(self, font, font_size)
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.label = self.render(self.text, 1, self.font_color)
        self.width = self.label.get_rect().width
        self.height = self.label.get_rect().height
        self.dimensions = (self.width, self.height)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.position = pos_x, pos_y
 
    def is_mouse_selection(self, (posx, posy)):
        if (posx >= self.pos_x and posx <= self.pos_x + self.width) and \
            (posy >= self.pos_y and posy <= self.pos_y + self.height):
                return True
        return False
 
    def set_position(self, x, y):
        self.position = (x, y)
        self.pos_x = x
        self.pos_y = y
 
    def set_font_color(self, rgb_tuple):
        self.font_color = rgb_tuple
        self.label = self.render(self.text, 1, self.font_color)
 
class GameMenu():
    def __init__(self, screen, items, funcs, bg_color=BLACK, font=None, font_size=30,
                 font_color=WHITE):
        self.screen = screen
        self.scr_width = self.screen.get_rect().width
        self.scr_height = self.screen.get_rect().height
 
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
 
        self.funcs = funcs
        self.items = []
        for index, item in enumerate(items):
            menu_item = MenuItem(item, font, font_size, font_color)
 
            # t_h: total height of text block
            t_h = len(items) * menu_item.height
            pos_x = (self.scr_width / 2) - (menu_item.width / 2)-150
            
            if index == 0:
                pos_y = (self.scr_height / 2) - (t_h / 2) + ((index*2) + index * menu_item.height)-40
            elif index == 1:
                pos_y = (self.scr_height / 2) - (t_h / 2) + ((index*2) + index * menu_item.height)
            else:
                pos_y = (self.scr_height / 2) - (t_h / 2) + ((index*2) + index * menu_item.height)+40
            menu_item.set_position(pos_x, pos_y)
            self.items.append(menu_item)
 
        self.mouse_is_visible = True
        self.cur_item = None
 
    def set_mouse_visibility(self):
        if self.mouse_is_visible:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)
 
    def set_keyboard_selection(self, key):
        """
        Marks the MenuItem chosen via up and down keys.
        """
        for item in self.items:
            # Return all to neutral
            item.set_italic(False)
            item.set_font_color(WHITE)
 
        if self.cur_item is None:
            self.cur_item = 0
        else:
            # Find the chosen item
            if key == pygame.K_UP and \
                    self.cur_item > 0:
                self.cur_item -= 1
            elif key == pygame.K_UP and \
                    self.cur_item == 0:
                self.cur_item = len(self.items) - 1
            elif key == pygame.K_DOWN and \
                    self.cur_item < len(self.items) - 1:
                self.cur_item += 1
            elif key == pygame.K_DOWN and \
                    self.cur_item == len(self.items) - 1:
                self.cur_item = 0
 
        self.items[self.cur_item].set_italic(True)
        self.items[self.cur_item].set_font_color(RED)
 
        # Finally check if Enter or Space is pressed
        if key == pygame.K_RETURN:
            text = self.items[self.cur_item].text
            self.funcs[text]()
 
    def set_mouse_selection(self, item, mpos):
        """Marks the MenuItem the mouse cursor hovers on."""
        if item.is_mouse_selection(mpos):
            item.set_font_color(RED)
            item.set_italic(True)
        else:
            item.set_font_color(WHITE)
            item.set_italic(False)

class UpgradeItem:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def add(self,value):
        self.value += value

    def sub(self,value):
        self.value -= value

class UpgradeMenu:
    def __init__(self):
        self.health = UpgradeItem("Health",0)
        self.fireRate = UpgradeItem("Fire Rate",0)
        self.damage = UpgradeItem("Damage",0)
        self.newHealth = 0
        self.newFR = 0
        self.newDmg = 0
        self.points = 2
        self.finished = False

        self.arrowSheet = pygame.image.load("images/arrows.png").convert_alpha()

        self.leftImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.leftImg.blit(self.arrowSheet, (0,0), (77,39,25,25))
        self.leftNullImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.leftNullImg.blit(self.arrowSheet, (0,0), (112,40,25,25))
        self.rightImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.rightImg.blit(self.arrowSheet,(0,0),(77,109,25,25))
        self.rightNullImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.rightNullImg.blit(self.arrowSheet,(0,0),(112,109,25,25))

        self.box = pygame.Rect(250,100,300,400)
        self.titleFont = pygame.font.SysFont("calibri",55)
        self.title = self.titleFont.render("Upgrades",True,WHITE)
        self.titleRect = pygame.Rect(315,110,150,60)

        self.pTitleFont = pygame.font.SysFont("plantagenetcherokee",20)
        self.pointText = self.pTitleFont.render("Points: " + str(self.points),
                                             True,WHITE)
        self.pointRect = pygame.Rect(360,155,50,40)

        self.allFont = pygame.font.SysFont("plantagenetcherokee",30)
        self.pointFont = pygame.font.SysFont("plantagenetcherokee",25)

        self.healthText = self.allFont.render("Health",True,WHITE)
        self.healthRect = pygame.Rect(353,190,50,40)
        self.hpText = self.pointFont.render(str(self.health.value+self.newHealth),
                                            True,WHITE)
        self.hpRect = pygame.Rect(390,220,25,25)
        self.healthLeft = pygame.Rect(350,220,25,25)
        self.healthRight = pygame.Rect(425,220,25,25)

        self.firerateText = self.allFont.render("Fire Rate",True,WHITE)
        self.firerateRect = pygame.Rect(341,265,50,40)
        self.frText = self.pointFont.render(str(self.fireRate.value+self.newFR),
                                            True,WHITE)
        self.frRect = pygame.Rect(390,295,25,25)
        self.firerateLeft = pygame.Rect(350,295,25,25)
        self.firerateRight = pygame.Rect(425,295,25,25)

        self.damageText = self.allFont.render("Damage",True,WHITE)
        self.damageRect = pygame.Rect(343,340,50,40)
        self.dmgText = self.pointFont.render(str(self.damage.value+self.newDmg),
                                            True,WHITE)
        self.dmgRect = pygame.Rect(390,370,25,25)
        self.damageLeft = pygame.Rect(350,370,25,25)
        self.damageRight = pygame.Rect(425,370,25,25)

        self.okFont = pygame.font.SysFont("calibri",65)
        self.okText = self.okFont.render("Ok",True,BLACK)
        self.okTextRect = pygame.Rect(363,433,60,60)
        self.okRect = pygame.Rect(350,420,95,70)

    def draw(self):
        self.updateText()
        #draw upgrade box
        pygame.draw.rect(BUFFSCR,BLACK,self.box)
        pygame.draw.rect(BUFFSCR,(150,150,150),self.box,5)

        #draw points and title
        BUFFSCR.blit(self.pointText,self.pointRect)
        BUFFSCR.blit(self.title,self.titleRect)

        #draw health graphics
        BUFFSCR.blit(self.healthText,self.healthRect)
        BUFFSCR.blit(self.hpText,self.hpRect)
        if self.newHealth > 0:
            BUFFSCR.blit(self.leftImg,self.healthLeft)
        else:
            BUFFSCR.blit(self.leftNullImg,self.healthLeft)

        if self.points > 0:
            BUFFSCR.blit(self.rightImg,self.healthRight)
        else:
            BUFFSCR.blit(self.rightNullImg,self.healthRight)

        #draw firerate graphics
        BUFFSCR.blit(self.firerateText,self.firerateRect)
        BUFFSCR.blit(self.frText,self.frRect)
        if self.newFR > 0:
            BUFFSCR.blit(self.leftImg,self.firerateLeft)
        else:
            BUFFSCR.blit(self.leftNullImg,self.firerateLeft)
        if self.points > 0 and game.pShip.upFR < 15:
            BUFFSCR.blit(self.rightImg,self.firerateRight)
        else:
            BUFFSCR.blit(self.rightNullImg,self.firerateRight)

        #draw damage graphics
        BUFFSCR.blit(self.damageText,self.damageRect)
        BUFFSCR.blit(self.dmgText,self.dmgRect)
        if self.newDmg > 0:
            BUFFSCR.blit(self.leftImg,self.damageLeft)
        else:
            BUFFSCR.blit(self.leftNullImg,self.damageLeft)
        if self.points > 0:
            BUFFSCR.blit(self.rightImg,self.damageRight)
        else:
            BUFFSCR.blit(self.rightNullImg,self.damageRight)

        #draw ok button
        pygame.draw.rect(BUFFSCR,(200,200,200),self.okRect)
        pygame.draw.rect(BUFFSCR,(150,150,150),self.okRect,5)
        BUFFSCR.blit(self.okText,self.okTextRect)

    def updateText(self):
        self.pointText = self.pTitleFont.render("Points: " + str(self.points),
                                             True,WHITE)
        self.hpText = self.pointFont.render(str(self.health.value+self.newHealth),
                                            True,WHITE)
        self.frText = self.pointFont.render(str(self.fireRate.value+self.newFR),
                                            True,WHITE)
        self.dmgText = self.pointFont.render(str(self.damage.value+self.newDmg),
                                            True,WHITE)

    def inRect(self, pos, rect):
        x1 = rect.left
        x2 = rect.right
        y1 = rect.top
        y2 = rect.bottom
        x,y = pos

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def process(self,mp):
        if not self.finished:
            if self.inRect(mp,self.healthLeft):
                if self.newHealth > 0:
                    self.newHealth -= 1
                    self.points += 1

            if self.inRect(mp,self.healthRight):
                if self.points > 0:
                    self.newHealth += 1
                    self.points -= 1

            if self.inRect(mp, self.firerateLeft):
                if self.newFR > 0:
                    self.newFR -= 1
                    self.points += 1

            if self.inRect(mp, self.firerateRight) and game.pShip.upFR < 15:
                if self.points > 0:
                    self.newFR += 1
                    self.points -= 1

            if self.inRect(mp,self.damageLeft):
                if self.newDmg > 0:
                    self.newDmg -= 1
                    self.points += 1

            if self.inRect(mp,self.damageRight):
                if self.points > 0:
                    self.newDmg += 1
                    self.points -= 1

            if self.inRect(mp,self.okRect):
                if self.points == 0:
                    self.upgrade()

    def upgrade(self):
        self.health.add(self.newHealth)
        self.fireRate.add(self.newFR)
        self.damage.add(self.newDmg)
        self.newHealth = 0
        self.newFR = 0
        self.newDmg = 0
        self.points = 2
        self.finished = True

class DeathScreen:
    def __init__(self):
        self.highscore = game.score
        self.fadeFrame = 0

        self.box = pygame.Rect(250,100,300,400)

        self.scorefont = pygame.font.SysFont("arial",30)
        self.myfont = pygame.font.SysFont("couriernew",24)
        self.titleText = self.scorefont.render("Final Score: ",True,WHITE)
        self.titleRect = pygame.Rect(320,120,100,50)
        self.scoreText = self.scorefont.render(str(self.highscore),True,
                                               WHITE)
        self.scoreRect = pygame.Rect(370,160,100,50)

        self.wonText = self.scorefont.render("You won!",True,WHITE)
        self.wonRect = pygame.Rect(337,420,100,50)

        self.retryColor = WHITE
        self.retryText = self.myfont.render("Retry", True, self.retryColor)
        self.retryRect = pygame.Rect(360,250,80,30)

        self.menuColor = WHITE
        self.menuText = self.myfont.render("Menu",True,self.menuColor)
        self.menuRect = pygame.Rect(366,300,80,30)

        self.quitColor = WHITE
        self.quitText = self.myfont.render("Quit",True,self.quitColor)
        self.quitRect = pygame.Rect(366,350,80,30)

    def inRect(self, pos, rect):
        x1 = rect.left
        x2 = rect.right
        y1 = rect.top
        y2 = rect.bottom
        x,y = pos

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def process(self, mp):
        if self.inRect(mp, self.retryRect):
            self.retryColor = (255,0,0)
        else:
            self.retryColor = (255,255,255)

        if self.inRect(mp,self.menuRect):
            self.menuColor = (255,0,0)
        else:
            self.menuColor = WHITE

        if self.inRect(mp,self.quitRect):
            self.quitColor = (255,0,0)
        else:
            self.quitColor = WHITE

    def click(self,mp):
        global currScreen, upMenu, deathScreen, enteredScore
        if self.inRect(mp, self.retryRect):
            game.reset()
            upMenu = UpgradeMenu()
            deathScreen = DeathScreen()
            enteredScore = False
            currScreen = "running"
            pygame.mixer.music.stop()
            pygame.mixer.music.load("music/DiscoCentury.ogg")
            pygame.mixer.music.play(-1)

        if self.inRect(mp,self.menuRect):
            game.reset()
            upMenu = UpgradeMenu()
            deathScreen = DeathScreen()
            enteredScore = False
            currScreen = "start"
            pygame.mixer.music.stop()
            pygame.mixer.music.load("music/!1hardcore.ogg")
            pygame.mixer.music.play(-1)

        if self.inRect(mp,self.quitRect):
            pygame.quit()
            sys.exit()

    def draw(self, won=False):
        self.highscore = game.score
        self.titleText = self.scorefont.render("Final Score:",True,WHITE)
        self.scoreText = self.scorefont.render(str(self.highscore),True,WHITE)
        self.retryText = self.myfont.render("Retry",True,self.retryColor)
        self.menuText = self.myfont.render("Menu",True,self.menuColor)
        self.quitText = self.myfont.render("Quit",True,self.quitColor)
        if won:
            self.wonText = self.scorefont.render("You won!",True,WHITE)
        else:
            self.wonText = self.scorefont.render("You lost!",True,WHITE)
        self.fadeFrame += 2
        if self.fadeFrame % 3 == 0 and self.fadeFrame < 128:
            #update camera
            BUFFSCR.fill((0,0,0))
            #draw background and sprites to screen
            BUFFSCR.blit(BG,(0,0),(game.slack.x,game.slack.y,WIN_WIDTH,WIN_HEIGHT))
            drawInfo()
            drawSprites(game)
            transparent = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))
            transparent.set_alpha(self.fadeFrame)
            transparent.fill((0,0,0))
            BUFFSCR.blit(transparent,(0,0))

        if self.fadeFrame > 250:
            pygame.draw.rect(BUFFSCR, (0,0,0), self.box)
            pygame.draw.rect(BUFFSCR, (150,150,150), self.box, 5)
            BUFFSCR.blit(self.titleText,self.titleRect)
            BUFFSCR.blit(self.scoreText,self.scoreRect)
            BUFFSCR.blit(self.wonText,self.wonRect)
            BUFFSCR.blit(self.retryText,self.retryRect)
            BUFFSCR.blit(self.menuText,self.menuRect)
            BUFFSCR.blit(self.quitText,self.quitRect)

def quitGame():
    pygame.quit()
    sys.exit()

def startGame():
    global currScreen, gameScreen, dMenu, game
    pygame.mixer.music.stop()
    pygame.mixer.music.load("music/DiscoCentury.ogg")
    pygame.mixer.music.play(-1)
    gameScreen.reset()
    if dMenu.index == 0:
        game.multiplier = 0.5
    elif dMenu.index == 1:
        game.multiplier = 1.0
    elif dMenu.index == 2:
        game.multiplier = 1.5
    currScreen = SCREENS[1]

def cycleScreen():
    global currScreen
    index = SCREENS.index(currScreen)
    index += 1
    if index >= len(SCREENS):
        index = 0

    currScreen = SCREENS[index]

def drawSprites(g):
    shipSprites = g.waves[g.currWave].cShips
    for s in shipSprites:
        for b in s.bullets:
            newRect = pygame.Rect(b.rect.left-g.slack.x,
                                  b.rect.top-g.slack.y,
                              b.rect.width,b.rect.height)
            BUFFSCR.blit(b.image,newRect)
    for s in shipSprites:
        #draw ship
        newRect = pygame.Rect(s.pos.x-g.slack.x,
                              s.pos.y-g.slack.y,
                          s.rect.width,s.rect.height)
        BUFFSCR.blit(s.image,newRect)
        #draw ship's health bar
        grnLen = int(s.width*(float(s.health)/s.maxHealth))
        if grnLen == 0 and s.health > 0:
            grnLen = 1
        if grnLen < 0:
            grnLen = 0
        redLen = s.width-grnLen
        grnRect = pygame.Rect(s.rect.left-g.slack.x,
                              s.rect.bottom-g.slack.y+5,
                              grnLen,5)
        redRect = pygame.Rect(s.rect.left-g.slack.x+grnLen,
                              s.rect.bottom-g.slack.y+5,
                              redLen,5)
        if grnLen > 0:
            pygame.draw.rect(BUFFSCR, (0,255,0), grnRect)
        if redLen > 0:
            pygame.draw.rect(BUFFSCR, (255,0,0), redRect)

def drawInfo():
    #draw score
    scrSurf = SCOREFONT.render("Score: " + str(game.score),True,WHITE)

    #draw wave number
    waveSurf = SCOREFONT.render("Wave: "+ str(game.currWave),True,WHITE)

    #draw remaining enemies
    w = game.waves[game.currWave]
    enemies = w.numEnemies()
    enemySurf = SCOREFONT.render("Enemies: "+ str(enemies),True,WHITE)

    BUFFSCR.blit(scrSurf, SCORERECT)
    BUFFSCR.blit(waveSurf, WAVERECT)
    BUFFSCR.blit(enemySurf,ENEMYRECT)

def drawPause():
    transparent = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))
    transparent.set_alpha(128)
    transparent.fill((0,0,0))
    bgPause = pygame.Rect(325,291,160,50)
    pygame.draw.rect(BUFFSCR,(0,0,0),bgPause)
    pygame.draw.rect(BUFFSCR,(150,150,150),bgPause,5)
    pauseSurf = PAUSEFONT.render("PAUSED",True,WHITE)
    BUFFSCR.blit(transparent,(0,0))
    BUFFSCR.blit(pauseSurf, PAUSERECT)

def drawWave():
    waveText = PAUSEFONT.render("Wave Complete!",True,WHITE)
    waveRect = pygame.Rect(270,50,100,50)
    BUFFSCR.blit(waveText,waveRect)

def drawTutorial():
    titlefont = pygame.font.SysFont("calibri",40)
    tutfont = pygame.font.SysFont("calibri",30)
    line1 = titlefont.render("Welcome to Space Pylot!",True,WHITE)
    line2 = tutfont.render("Use the W, A, S, and D keys to move your ship!",
                           True,WHITE)
    line3 = tutfont.render("Move the mouse to aim your ship, click and hold to shoot!",
                           True,WHITE)
    line1Rect = pygame.Rect(220,50,100,50)
    line2Rect = pygame.Rect(170,85,100,50)
    line3Rect = pygame.Rect(120,110,110,50)

    BUFFSCR.blit(line1,line1Rect)
    BUFFSCR.blit(line2,line2Rect)
    BUFFSCR.blit(line3,line3Rect)

def scrToTxt(score):
    return score[0]+" - "+str(score[1])

def isSorted(scores):
    old = scores[0][1]
    for i in scores:
        if i[1] <= old:
            old = i[1]
        else:
            return False
    return True

def drawScores():
    global HIGHSCORES
    if len(HIGHSCORES) > 0 and not isSorted(HIGHSCORES):
        HIGHSCORES = sorted(HIGHSCORES,key=itemgetter(1))
        HIGHSCORES.reverse()
    scrfont = pygame.font.SysFont("couriernew",20)
    myscores = {}
    if len(HIGHSCORES) < 5:
        i = len(HIGHSCORES)
    else:
        i = 5

    if len(HIGHSCORES) > 0:
        for x in range(i):
            newText = scrfont.render(str(x+1) + ":" + scrToTxt(HIGHSCORES[x]),
                                     True,WHITE)
            newRect = pygame.Rect(510,180+(x*50),100,50)
            myscores[newText] = newRect
        
    box = pygame.Rect(480,100,300,360)

    titlefont = pygame.font.SysFont("calibri",40)
    titleText = titlefont.render("High Scores",True,WHITE)
    titleRect = pygame.Rect(550,120,100,50)

    pygame.draw.rect(BUFFSCR,BLACK,box)
    pygame.draw.rect(BUFFSCR,(150,150,150),box,3)
    BUFFSCR.blit(titleText,titleRect)
    if len(myscores) > 0:
        for score in myscores:
            BUFFSCR.blit(score,myscores[score])

class EnterScore:
    def __init__(self):
        self.myfont = pygame.font.SysFont("calibri",25)
        self.scorefont = pygame.font.SysFont("calibri",35)
        self.boxRect = pygame.Rect(260,190,278,150)
        self.enterText = self.myfont.render("New highscore! Enter name: ",
                                  True,WHITE)
        self.enterRect = pygame.Rect(280,200,100,50)

        self.nameText = self.scorefont.render(">",True,WHITE)
        self.nameTextRect = pygame.Rect(288,232,230,30)
        self.nameRect = pygame.Rect(285,230,230,30)
        self.okFont = pygame.font.SysFont("calibri",45)
        self.okText = self.okFont.render("Ok",True,BLACK)
        self.okTextRect = pygame.Rect(378,285,40,40)
        self.okRect = pygame.Rect(363,275,75,50)

    def drawEnterScore(self, mytext=""):
        self.nameText = self.scorefont.render(">"+mytext,True,WHITE)
        
        pygame.draw.rect(BUFFSCR,BLACK,self.boxRect)
        pygame.draw.rect(BUFFSCR,(150,150,150),self.boxRect,5)
        pygame.draw.rect(BUFFSCR,WHITE,self.nameRect,5)
        pygame.draw.rect(BUFFSCR,(200,200,200),self.okRect)
        pygame.draw.rect(BUFFSCR,(150,150,150),self.okRect,5)
        BUFFSCR.blit(self.enterText,self.enterRect)
        BUFFSCR.blit(self.nameText,self.nameTextRect)
        BUFFSCR.blit(self.okText,self.okTextRect)

    def inRect(self, pos):
        rect = self.okRect
        x1 = rect.left
        x2 = rect.right
        y1 = rect.top
        y2 = rect.bottom
        x,y = pos

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def enterScore(self, name):
        global HIGHSCORES
        HIGHSCORES.append([name,game.score])
        f = file("scores.pickle","w")
        pickle.dump(HIGHSCORES,f)
        f.close()

class DiffMenu:
    def __init__(self):
        self.index = 0
        self.arrowSheet = pygame.image.load("images/arrows.png").convert_alpha()

        self.leftImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.leftImg.blit(self.arrowSheet, (0,0), (77,39,25,25))
        self.leftNullImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.leftNullImg.blit(self.arrowSheet, (0,0), (112,40,25,25))
        self.rightImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.rightImg.blit(self.arrowSheet,(0,0),(77,109,25,25))
        self.rightNullImg = pygame.Surface((25,25),flags=pygame.SRCALPHA)
        self.rightNullImg.blit(self.arrowSheet,(0,0),(112,109,25,25))

        self.titlefont = pygame.font.SysFont("calibri",25,True)
        self.myfont = pygame.font.SysFont("calibri",22)
        self.texts = [self.myfont.render("Easy",True,WHITE),
                      self.myfont.render("Normal",True,WHITE),
                      self.myfont.render("Hard",True,WHITE)]

        self.diffTitle = self.titlefont.render("Difficulty",True,WHITE)
        self.diffTitleRect = pygame.Rect(355,550,100,50)

        self.leftRect = pygame.Rect(320,580,25,25)
        self.rightRect = pygame.Rect(455,580,25,25)

        self.easyRect = pygame.Rect(380,585,100,50)
        self.normalRect = pygame.Rect(370,585,100,50)
        self.hardRect = pygame.Rect(381,585,100,50)

    def draw(self):
        BUFFSCR.blit(self.diffTitle,self.diffTitleRect)
        if self.index == 0:
            BUFFSCR.blit(self.leftNullImg,self.leftRect)
            BUFFSCR.blit(self.rightImg,self.rightRect)
            BUFFSCR.blit(self.texts[0],self.easyRect)
        elif self.index == 1:
            BUFFSCR.blit(self.leftImg,self.leftRect)
            BUFFSCR.blit(self.rightImg,self.rightRect)
            BUFFSCR.blit(self.texts[1],self.normalRect)
        elif self.index == 2:
            BUFFSCR.blit(self.leftImg,self.leftRect)
            BUFFSCR.blit(self.rightNullImg,self.rightRect)
            BUFFSCR.blit(self.texts[2],self.hardRect)

    def inRect(self, pos, rect):
        x1 = rect.left
        x2 = rect.right
        y1 = rect.top
        y2 = rect.bottom
        x,y = pos

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def click(self,mp):
        if self.inRect(mp,self.leftRect) and self.index != 0:
            self.index -= 1
        if self.inRect(mp,self.rightRect) and self.index != 2:
            self.index += 1

def constrainMouse(mp):
    if mp[0] < 20:
        pygame.mouse.set_pos(20,mp[1])
    elif mp[0] > WIN_WIDTH-20:
        pygame.mouse.set_pos(WIN_WIDTH-20,mp[1])

    if mp[1] < 20:
        pygame.mouse.set_pos(mp[0],20)
    elif mp[1] > WIN_HEIGHT-20:
        pygame.mouse.set_pos(mp[0],WIN_HEIGHT-20)

def needsScoring():
    global HIGHSCORES
    if len(HIGHSCORES) > 0:
        if not isSorted(HIGHSCORES):
            HIGHSCORES = sorted(HIGHSCORES,key=itemgetter(1))
            HIGHSCORES.reverse()
        if len(HIGHSCORES) < 5:
            i = len(HIGHSCORES)-1
        else:
            i = 4
        if i < 0 or game.score > HIGHSCORES[i][1] or len(HIGHSCORES) < 5:
            return True
        else:
            return False
    else:
        return True

def toggleScores():
    global showScores
    showScores = not showScores

#initialize menus
start_menu_items = ('Start', 'High Scores', 'Quit')
funcs = {'Start': startGame,
         'High Scores':toggleScores,
     'Quit': quitGame}

#upgrade menu
upMenu = UpgradeMenu()
#start screen
startScreen = GameMenu(BUFFSCR, funcs.keys(), funcs)
gameScreen = environment.GameEnvironment(WIN_WIDTH,WIN_HEIGHT,BGWIDTH,BGHEIGHT,True)
#death screen
deathScreen = DeathScreen()
#high score board
enterScore = EnterScore()
#difficulty menu
dMenu = DiffMenu()

up = down = left = right = False
mouseDown = False
scoreStr = ""
enteredScore = False
showScores = False
#after you've entered high score
changeScreens = True
#---Main game loop----
while True:
    mp = pygame.mouse.get_pos()
    #print mp
    for event in pygame.event.get():
        if event.type == QUIT:
            quitGame()
        if event.type == KEYDOWN and currScreen == "start":
            startScreen.mouse_is_visible = False
            startScreen.set_keyboard_selection(event.key)
        if event.type == MOUSEBUTTONDOWN and currScreen == "start":
            for item in startScreen.items:
                if item.is_mouse_selection(mp):
                    startScreen.funcs[item.text]()

            dMenu.click(mp)
        if event.type == MOUSEBUTTONDOWN and enterScore.inRect(mp) and currScreen == "scoring":
            enterScore.enterScore(scoreStr)
            scoreStr = ""
            enteredScore = True
            if game.pShip.isDead():
                currScreen = "death"
            if game.won:
                currScreen = "end"
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            quitGame()
        if event.type == KEYDOWN and event.key == K_SPACE:
            if currScreen == "running":
                currScreen = SCREENS[2]
                drawPause()
            elif currScreen == "paused":
                currScreen = SCREENS[1]
        if event.type == KEYDOWN and event.key == ord("p")\
           and currScreen == "running":
            game.reset()
            upMenu = UpgradeMenu()
            deathScreen = DeathScreen()
            currScreen = SCREENS[0]
            pygame.mixer.music.stop()
            pygame.mixer.music.load("music/!1hardcore.ogg")
            pygame.mixer.music.play(-1)

        if event.type == KEYDOWN and (event.key == K_UP or event.key == 119):
            up = True
        if event.type == KEYDOWN and (event.key == K_DOWN or event.key == 115):
            down = True
        if event.type == KEYDOWN and (event.key == K_LEFT or event.key == 97):
            left = True
        if event.type == KEYDOWN and (event.key == K_RIGHT or event.key == 100):
            right = True

        if event.type == KEYUP and (event.key == K_UP or event.key == 119):
            up = False
        if event.type == KEYUP and (event.key == K_DOWN or event.key == 115):
            down = False
        if event.type == KEYUP and (event.key == K_LEFT or event.key == 97):
            left = False
        if event.type == KEYUP and (event.key == K_RIGHT or event.key == 100):
            right = False
        if event.type == KEYDOWN and currScreen == "scoring":
            mods = bin(pygame.key.get_mods())[2:].zfill(14)
            if event.key == K_BACKSPACE:
                if scoreStr != "":
                    scoreStr = scoreStr[:len(scoreStr)-1]
            elif event.key == K_RETURN:
                enterScore.enterScore(scoreStr)
                scoreStr = ""
                enteredScore = True
                if game.pShip.isDead():
                    currScreen = "death"
                if game.won:
                    currScreen = "end"
            elif len(scoreStr) < 8:
                if event.key < 256 and len(scoreStr) < 56:
                    if mods[len(mods)-1] == "1" or mods[len(mods)-2] == "1":
                        if event.key == 96:
                            mykey = 126
                        elif event.key == 48:
                            mykey = 41
                        elif event.key == 49:
                            mykey = 33
                        elif event.key == 50:
                            mykey = 64
                        elif event.key == 51:
                            mykey = 35
                        elif event.key == 52:
                            mykey = 36
                        elif event.key == 53:
                            mykey = 37
                        elif event.key == 54:
                            mykey = 94
                        elif event.key == 55:
                            mykey = 38
                        elif event.key == 56:
                            mykey = 42
                        elif event.key == 57:
                            mykey = 40
                        elif event.key == 45:
                            mykey = 95
                        elif event.key == 61:
                            mykey = 43
                        elif event.key == 91:
                            mykey = 123
                        elif event.key == 93:
                            mykey = 125
                        elif event.key == 92:
                            mykey = 124
                        elif event.key == 59:
                            mykey = 58
                        elif event.key == 39:
                            mykey = 34
                        elif event.key == 44:
                            mykey = 60
                        elif event.key == 46:
                            mykey = 62
                        elif event.key == 47:
                            mykey = 63
                        else:
                            mykey = event.key-32
                    else:
                        mykey = event.key

                    scoreStr += chr(mykey)

        if event.type == MOUSEBUTTONUP:
            mouseDown = False
        if event.type == MOUSEBUTTONUP and not changeScreens:
            changeScreens = True
        if event.type == MOUSEBUTTONDOWN and currScreen == "running":
            mouseDown = True
        if event.type == MOUSEBUTTONDOWN and currScreen == "upgrade":
            upMenu.process(mp)
        if event.type == MOUSEBUTTONDOWN and \
           (currScreen == "death" or currScreen == "end") and changeScreens:
            deathScreen.click(mp)

    if mouseDown and currScreen == "running":
        game.pShip.addBullet(mp,game.slack)
        
    if currScreen == "start":
        transparent = pygame.Surface((WIN_WIDTH,WIN_HEIGHT))
        transparent.set_alpha(128)
        transparent.fill((50,50,50))
        if pygame.mouse.get_rel() != (0,0):
            startScreen.mouse_is_visible = True
            startScreen.cur_item = None

        startScreen.set_mouse_visibility()
        
        BUFFSCR.fill((0,0,0))
        BUFFSCR.blit(BG,(0,0),(gameScreen.slack.x,
                               gameScreen.slack.y,WIN_WIDTH,WIN_HEIGHT))
        gameScreen.update(up,down,left,right,mp)
        drawSprites(gameScreen)
        BUFFSCR.blit(transparent, (0,0))
        for item in startScreen.items:
            if startScreen.mouse_is_visible:
                startScreen.set_mouse_selection(item,mp)
            BUFFSCR.blit(item.label, item.position)

        if showScores:
            drawScores()

        dMenu.draw()
        mytitlefont = pygame.font.SysFont("arial",50,True)
        mytitletext = mytitlefont.render("Space Pylot",True,WHITE)
        mytitlerect= pygame.Rect(260,15,100,60)
        BUFFSCR.blit(mytitletext,mytitlerect)

        #do wave checks
        if gameScreen.upgrading:
            gameScreen.upgrading = False
            gameScreen.currWave += 1

        if gameScreen.endTime != None:
            if time.time()-gameScreen.endTime >= 2:
                gameScreen.reset()

    elif currScreen == "running":
        #keep mouse inside window
        constrainMouse(mp)

        #update camera
        BUFFSCR.fill((0,0,0))
        #draw background and sprites to screen
        BUFFSCR.blit(BG,(0,0),(game.slack.x,game.slack.y,WIN_WIDTH,WIN_HEIGHT))
        game.update(up,down,left,right,mp)
        drawSprites(game)
        drawInfo()
        if not game.upgrading and game.currWave == 0:
            drawTutorial()

    elif currScreen == "upgrade":
        if upMenu.finished:
            h = upMenu.health.value
            fr = upMenu.fireRate.value
            dmg = upMenu.damage.value
            game.pShip.applyUpgrades(h,fr,dmg)
            game.currWave += 1
            game.upgrading = False
            upMenu.finished = False
            game.waves[game.currWave].correctPositions()
            currScreen = "running"
        else:
            upMenu.draw()

    elif currScreen == "death":
        deathScreen.process(mp)
        deathScreen.draw()

    elif currScreen == "end":
        deathScreen.process(mp)
        deathScreen.draw(True)

    elif currScreen == "scoring":
        enterScore.drawEnterScore(scoreStr)

    if game.upgrading:
        drawWave()
        mywave = game.waves[game.currWave]
        if time.time()-mywave.deathtime >= 2:
            if game.currWave == 0:
                game.currWave = 1
                game.upgrading = False
            else:
                currScreen = "upgrade"
        
    if game.pShip.isDead() and changeScreens:
        currScreen = "death"
    if game.won and changeScreens:
        currScreen = "end"
    if (game.won or game.pShip.isDead()) and enteredScore == False and needsScoring():
        changeScreens = False
        currScreen = "scoring"

    SCREEN.blit(BUFFSCR,(0,0))
    pygame.display.flip()
    CLOCK.tick(60)
