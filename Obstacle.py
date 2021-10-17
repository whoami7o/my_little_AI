import pygame
from pygame.sprite import Sprite


class Obstacle(Sprite):
    def __init__(self, env, length=None, width=None):

        super().__init__()

        self.settings = env.settings

        self.screen = env.screen
        self.screen_rect = env.screen.get_rect()

        self.color = self.settings.obstacle_color

        if length:
            self.length = length
        else:
            self.length = self.settings.obstacle_length

        if width:
            self.width = width
        else:
            self.width = self.settings.obstacle_width

        self.rect = pygame.Rect(0, 0, self.length, self.width)

        # self.rect.center = (self.screen_rect.centerx, self.screen_rect.centery - 200)

    def draw_obstacle(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
