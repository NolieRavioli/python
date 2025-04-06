import pygame
import random

pygame.init()

#Change these things
fps = 60
screen_width = 700
screen_height = 400
falling_speed_divider = 3
Fire_rate = 60
lives = 10


#Defining some stuff here
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 204, 255)
P_Color = GREEN
running = True
quitting = False
counter = 0
bullet_timer = Fire_rate
font = pygame.font.SysFont(None, 36)
pygame.display.set_caption('Python game thing.')

#basic classes (text)
def draw_text(display_string, font, surface, x, y, text_color):
    text_display = font.render(display_string, True, (text_color))
    text_rect = text_display.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_display, text_rect)

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
        pos = pygame.mouse.get_pos()
        if pos[0] > screen_width-20:
            self.rect.x = screen_width-20
        else:
            self.rect.x = pos[0]

        self.rect.y = 380

class Bullet(Block):
    def update(self):
        self.rect.y -= 3
        if self.rect.y < -15:
            self.remove(bullet_list)


#Rainbow text thing
def randomColor():
    rand_r = random.randint(0,255)
    rand_g = random.randint(0,255)
    rand_b = random.randint(0,255)
    return (rand_r,rand_g,rand_b)

screen = pygame.display.set_mode([screen_width, screen_height])

score = 0

block_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
all_sprites_list = pygame.sprite.Group()

for i in range(10):
    block = Block(WHITE, 20, 15)
    block.rect.x = random.randrange(screen_width-20)
    block.rect.y = random.randrange(screen_height-(screen_height/2))
    block_list.add(block)
    all_sprites_list.add(block)

##bullet = Bullet(RED, 3, 15)
player = Player(P_Color, 20, 15)
all_sprites_list.add(player)
##all_sprites_list.add(bullet)
clock = pygame.time.Clock()
while running:
    #defining stuff
    player = Player(P_Color, 20, 15)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            quitting = True

    screen.fill(BLACK)

    #see if mouse is being pressed
    m_pressed = pygame.mouse.get_pressed()
    mb1_pressed = m_pressed[0]
    mb2_pressed = m_pressed[1]
    #fire
    if bullet_timer < Fire_rate:
        bullet_timer += 1
    elif bullet_timer == Fire_rate and mb1_pressed == True:
        bullet = Bullet(RED, 3, 15)
        bullet.rect.x = pygame.mouse.get_pos() [0] + 7
        bullet.rect.y = 380
        bullet_list.add(bullet)
        all_sprites_list.add(bullet)
        bullet_timer = 0
##    #shields
##    if mb2_pressed == True:
##        P_Color = BLUE
##    elif mb2_pressed == False:
##        P_Color == GREEN
##    if pygame.sprite.spritecollideany(player, block_list) == True:
##        print(player_collide_test)
##        if mb2_pressed == True:
##            blocks_hit_list = pygame.sprite.spritecollide(player, block_list, False)
##        if mb2_pressed == False:
##            blocks_hit_list = pygame.sprite.spritecollide(player, block_list, False)
##            lives -= 1
##            print("lives: " + lives)

    #collisions
    blocks_bullets_list = pygame.sprite.groupcollide(bullet_list, block_list, True, True)
    blocks_player_list = pygame.sprite.spritecollide(player, block_list, True)
    #adding blocks
    for block in blocks_bullets_list:
        score += 1
        block.reset_pos()

    for block in blocks_player_list:
        score_check = score
        score += 1
        print(score)
        block.reset_pos()
        block
        block.rect.x = random.randrange(screen_width)
        block.rect.y = random.randrange(screen_height)
        block_list.add(block)
        all_sprites_list.add(block)

    #update/draw stuff
    draw_text('Score: %s' % (score), font, screen, 5, 5, WHITE)
    draw_text('Lives: %s' % (lives), font, screen, 550, 5, WHITE)
    all_sprites_list.update()
    all_sprites_list.draw(screen)
    clock.tick(fps)
    pygame.display.flip()

    #Losing
    if lives < 0:
        running = False


while not running:
    randomColor()
    draw_text('Game Over', font, screen, 255, 5, WHITE)
    draw_text('You killed: ', font, screen, 255, 40, WHITE)
    draw_text(str(score), font, screen, 380, 40, randomColor())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitting = True
    pygame.display.update()
    if quitting == True and running == False:
        pygame.quit()
        quit()
        exit()