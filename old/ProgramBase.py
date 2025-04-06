import pygame
import random
import math
import sys
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((640, 460))
font = pygame.font.SysFont(None, 36)

def draw_text(display_string, font, surface, x_pos, y_pos):
    text_display = font.render(display_string, 1, (0, 0, 0))
    surface.blit(text_display, (x_pos, y_pos))

main_clock = pygame.time.Clock()

while True:
    # check for events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    main_clock.tick(50)
    screen.fill((255, 255, 255))
    pygame.display.update()