import pygame
from pygame.sprite import Sprite
import random


class Dot(Sprite):

    def __init__(self, env, x_trajectory=[], y_trajectory=[], death=False, win=False, best=False):

        super().__init__()

        self.settings = env.settings

        self.screen = env.screen
        self.screen_rect = env.screen.get_rect()

        self.x_pos = float(self.settings.screen_width/2)
        self.y_pos = float(self.settings.screen_height - 50 * self.settings.dot_size)

        self.rect = pygame.Rect(0, 0, self.settings.dot_size, self.settings.dot_size,)
        self.rect.center = (self.x_pos, self.y_pos)

        if not best:
            self.x_moves, self.y_moves = self._mutation(list(x_trajectory), list(y_trajectory))
        else:
            self.x_moves = list(x_trajectory)
            self.y_moves = list(y_trajectory)

        self.x_history = []
        self.y_history = []

        self.death = death
        self.win = win
        self.best = best

    def update(self):
        if not self.death:
            x_step = self._move_dot_x()
            y_step = self._move_dot_y()

            if x_step == 0 and y_step == 0:
                self.update()
            else:
                self.x_pos += x_step
                self.x_history.append(x_step)

                self.y_pos += y_step
                self.y_history.append(y_step)

                self.rect.center = (self.x_pos, self.y_pos)

            self._check_edges()

    def _move_dot_x(self):
        # if there is a calculated trajectory then it follows it
        # if it exceeds it then next steps will be generated randomly and appended to move history
        if len(self.x_moves) != 0:
            x_step = self.x_moves.pop(0)
        else:
            x_step = random.choice(self.settings.move_options) * self.settings.dot_step
        return x_step

    def _move_dot_y(self):
        # if there is a calculated trajectory then it follows it
        # if it exceeds it then next steps will be generated randomly and appended to move history
        if len(self.y_moves) != 0:
            y_step = self.y_moves.pop(0)
        else:
            y_step = random.choice(self.settings.move_options) * self.settings.dot_step
        return y_step

    def _check_edges(self):
        if (self.rect.left <= 0) or (self.rect.right >= self.settings.screen_width)\
                or (self.rect.top <= 0) or (self.rect.bottom >= self.settings.screen_height):
            self.death = True

    def _mutation(self, x_trace, y_trace):
        # !!! there is a bug!!! (it actually not much important)
        # # bug in the possibility to overwrite the same step twice, but it doesn't make any noticeable changes

        # mutation process
        x_steps = int(self.settings.mutation_factor * len(x_trace))
        y_steps = int(self.settings.mutation_factor * len(y_trace))

        for x_step in range(x_steps):
            x_trace[random.choice(range(len(x_trace)))] = random.choice(self.settings.move_options) \
                                                          * self.settings.dot_step
        for y_step in range(y_steps):
            y_trace[random.choice(range(len(y_trace)))] = random.choice(self.settings.move_options) \
                                                          * self.settings.dot_step
        return x_trace, y_trace

    def draw_dot(self):
        if self.death:
            if not self.win:
                pygame.draw.rect(self.screen, self.settings.dead_dot_color, self.rect)
            else:
                pygame.draw.rect(self.screen, self.settings.win_dot_color, self.rect)
        elif self.best:
            pygame.draw.rect(self.screen, self.settings.best_dot_color, self.rect)
        else:
            pygame.draw.rect(self.screen, self.settings.dot_color, self.rect)

