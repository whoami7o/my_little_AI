import pygame
from pygame.sprite import Sprite


class Goal(Sprite):
    def __init__(self, env):

        super().__init__()

        self.settings = env.settings

        self.screen = env.screen
        self.screen_rect = env.screen.get_rect()

        self.color = self.settings.goal_color

        self.radius = self.settings.goal_size

        self.x_pos = int(self.settings.screen_width / 2)
        self.y_pos = 0 + 2 * self.radius

        self.rect = pygame.Rect(0, 0, self.radius, self.radius)

        self.rect.center = (self.x_pos, self.y_pos)

    def draw_goal(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
