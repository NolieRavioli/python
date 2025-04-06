import pygame
from pygame.locals import *
import random

#screen size
screen_width = 700
screen_height = 700
init_blocks = 30                #how many block should spawn at first
fps = 60                        #frames per second
falling_speed_divider = 3       #how slowly the blocks will fall
Fire_rate = 30                  #how many frames in between each shot
lives = 10                      #starting lives


# Define stuff
    #colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

cooldown = Fire_rate
counter = 0
running = True
quitting = False
score = 0
shielding = Fire_rate * 10
shield_cd = Fire_rate * 10


#Basic functions
def draw_text(display_string, font, surface, x, y, text_color):
    text_display = font.render(display_string, True, (text_color))
    text_rect = text_display.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_display, text_rect)

def randomColor():
    rand_r = random.randint(40,255)
    rand_g = random.randint(40,255)
    rand_b = random.randint(40,255)
    return (rand_r,rand_g,rand_b)

def mouseCheck():
    m_pressed = pygame.mouse.get_pressed()
    return m_pressed

def canFire():
    global Fire_rate
    global cooldown
    if Fire_rate < cooldown:
        Fire_rate += 1
    elif Fire_rate == cooldown and mouseCheck()[0] == True and mouseCheck()[2] == False:
        spawnBullet()
        Fire_rate = 0
"""
def isShield():
    global shielding
    global shield_cd
    if shielding > 0 and shielding <= shield_cd and mouseCheck()[2] == True:
        shielding -= 1
    elif shielding == 0:
        shield_timeout = 0
        shield_timer = fps * 3
        if shield_timeout < shield_timer:
            sheild_timeout += 1
        elif shield_timeout == shield_timer:
            shielding += 1
    if shielding < shield_cd and shielding > 0 and mouseCheck[2] == False:
        shield_timeout = 0
        shield_timer = fps
        if shield_timeout < shield_timer:
            sheild_timeout += 1
        elif shield_timeout == shield_timer:
            shielding += 1
"""

#Sprite Classes
class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
    def reset_pos(self):
        self.rect.y = random.randrange(-(screen_height/2), -20)
        self.rect.x = random.randrange(screen_width-20)
    def update(self):
        global counter
        global lives
        counter += 1
        if counter == falling_speed_divider:
            self.rect.y += 1
            counter = 0
        if self.rect.y > screen_height+20:
            self.reset_pos()
            lives -= 1

class Player(Block):
    def update(self):
        pos = pygame.mouse.get_pos() [0]
        self.rect.x = pos
        if pos > screen_width - 20:
            self.rect.x = screen_width - 20
        self.rect.y = screen_height - 20

class Bullet(Block):
    def update(self):
        self.rect.y -= 5
        if self.rect.y < -15:
            all_sprites_list.remove(self)
            bullet_list.remove(self)

#sprite spawning fuctions
def spawnBlock(onScreen):
    block = Block(randomColor(), 20, 15)
    if onScreen == True:
        block.rect.x = random.randrange(screen_width-20)
        block.rect.y = random.randrange(screen_height/2)
    elif onScreen == False:
        block.rect.y = random.randrange(-(screen_height/2), -20)
        block.rect.x = random.randrange(screen_width-20)
    block_list.add(block)
    all_sprites_list.add(block)

def spawnBullet():
    bullet = Bullet(RED, 3, 15)
    bullet.rect.x = pygame.mouse.get_pos() [0] + 7
    bullet.rect.y = screen_height - 20
    bullet_list.add(bullet)
    all_sprites_list.add(bullet)

#defining sprite grouping
block_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()

#initiate player
player = Player(GREEN, 20, 15)
all_sprites_list.add(player)

#inital block spawns
for i in range(init_blocks):
    spawnBlock(True)

#-###-###-START PYGAME-###-###-#
pygame.init()

#defining some pygame stuff
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
pygame.display.set_caption('Python game thing.')

#initializing screen
screen = pygame.display.set_mode([screen_width, screen_height])

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitting = True
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
                quitting = True

    canFire()
    #check for lives
    if lives <= 0:
        lives = 0
        running = False

    # Clear the screen
    screen.fill(BLACK)

    # Block collisions
    blocks_player_col = pygame.sprite.spritecollide(player, block_list, False)
    for block in blocks_player_col:
        score += 1
        if mouseCheck()[2] == False:
            lives -= 1
        print(score)
        block.reset_pos()
        spawnBlock(False)

    blocks_bullet_col = pygame.sprite.groupcollide(block_list, bullet_list, False, True)
    for block in blocks_bullet_col:
        score += 1
        print(score)
        block.reset_pos()
        spawnBlock(False)

    # Update screen/Draw Text
    all_sprites_list.update()
    all_sprites_list.draw(screen)
    draw_text('Score: %s' % (score), font, screen, 5, 5, WHITE)
    draw_text('Lives: %s' % (lives), font, screen, screen_width - 110, 5, WHITE)
    pygame.display.flip()

    clock.tick(fps)

while not running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitting = True
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                quitting = True
    randomColor()
    draw_text('Game Over', font, screen, (screen_width/2) - 64, 5, GREEN)
    draw_text('You killed: ', font, screen, (screen_width/2) - 64, 40, GREEN)
    draw_text(str(score), font, screen, (screen_width/2) + 64, 40, randomColor())
    pygame.display.update()
    if quitting == True:
        pygame.quit()
        exit()