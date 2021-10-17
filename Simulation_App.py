import sys
import math
import pygame
import random
from time import sleep
from Settings import Settings
from Dot import Dot
from Goal import Goal
from Obstacle import Obstacle
from Button import Button


class SimulationApp:

    def __init__(self):

        pygame.init()
        # create file for writing logs
        self.logs_file = open('session_logs.txt', 'w')

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        self.screen_rect = self.screen.get_rect()

        pygame.display.set_caption("MY LITTLE AI")

        self.goal = Goal(self)

        self.obstacles = pygame.sprite.Group()
        self.dots = pygame.sprite.Group()
        self.inactive_dots = pygame.sprite.Group()

        self.gen_num = 0
        self.lvl = 0  # from 0 to 4
        self.current_lvl = None

        self.best_dot = None
        self.sum_gen_quality = 0

        self.x_trace = None
        self.y_trace = None
        # lock a mutation factor initial value
        self.intial_mutation_factor = self.settings.mutation_factor

        # values for calculating indexes
        self.min_steps = int((Dot(self).rect.midtop[1] - self.goal.rect.midbottom[1])/self.settings.dot_step)
        self.min_dev = 1.41421 * (self.settings.goal_size/2 - 0 * self.settings.dot_size/2)

        # buttons
        self.start_button = Button(self, 'Start')
        self.start_button.move_button(-(self.start_button.height + 10), 0)

        self.lvl_button = Button(self, 'LEVEL', height=20, font=31, outline=0,
                                 color=self.settings.bg_color)  # move to the hud (255, 245, 238)
        self.lvl_increase = Button(self, '+', width=30, height=30, font=30, outline=0, color=self.settings.bg_color)
        self.lvl_decrease = Button(self, '-', width=30, height=30, font=30, outline=0, color=self.settings.bg_color)
        self.lvl_number = Button(self, self.lvl, height=30, font=30, outline=0, color=self.settings.bg_color)

        self.gen_info = Button(self, f'Gen : {self.gen_num}', height=20, font=31, outline=0,
                               color=self.settings.bg_color)

        self.restart_button = Button(self, 'restart', width=100, height=20, font=28, outline=2, color=(250, 128, 114))
        self.back_to_main = Button(self, 'main menu', width=114, height=20, font=28, outline=2, color=(244, 164, 96))

        self.packsize_button = Button(self, 'PACK SIZE', height=20, font=31, outline=0,
                                 color=self.settings.bg_color)  # move to the hud (255, 245, 238)
        self.packsize_increase = Button(self, '+', width=30, height=30, font=30, outline=0,
                                        color=self.settings.bg_color)
        self.packsize_decrease = Button(self, '-', width=30, height=30, font=30, outline=0,
                                        color=self.settings.bg_color)
        self.packsize_number = Button(self, self.settings.dot_number, height=30, font=30, outline=0,
                                      color=self.settings.bg_color)

        # simulation running marker
        self.running = False

    def run_simulation(self):
        while True:
            # main menu idling
            self._update_screen()
            self._check_events()

            # action
            while self.running:
                self._main_loop()

    def _main_loop(self):
        # check if settings was changed
        if self.lvl != self.current_lvl:
            self._print_to_both(f'-------------------------'
                                f'\n\t LVL{self.lvl}\n'
                                f'-------------------------')
            self.settings.mutation_factor = self.intial_mutation_factor
            self.gen_num = 0
            self.best_dot = None

        # action markers
        self.restart = False
        self.to_main = False
        # lvl creation and lvl marker
        self._create_lvl(self.lvl)
        self.current_lvl = self.lvl

        # dot creation depending on best dot
        if self.best_dot:
            self._create_pack_of_dots(self.settings.dot_number, self.x_trace, self.y_trace, best=True)
            self.dots.add(self.best_dot)
        else:
            self._create_pack_of_dots(self.settings.dot_number)

        # info print
        self._print_to_both(f'\tGen №{self.gen_num}'
                            f'\nPack SIZE : {len(self.dots)}')

        # main event
        while len(self.dots) != 0:

            if self.restart or self.to_main:
                break

            self._check_events()
            self.dots.update()

            if self._check_goal():
                self._make_dead_dots_inactive()
                self._update_screen()
                # sleep(2.0)
                # pass remaining dots for calculating total quality of generation
                for dot in self.dots.sprites():
                    self.dots.remove(dot)
                    self.inactive_dots.add(dot)
                # we no longer need to watch through rest because first dot reached the goal 'obviously' is the best
                break
            else:
                self._update_screen()

            self._check_obstacle()
            self._make_dead_dots_inactive()

        # clear all dots
        self.dots.empty()

        # if simulation was interrupted don't try to evolve
        if not (self.restart or self.to_main):
            self._find_best()
            self.gen_num += 1
        elif self.restart:
            # action ifo print
            self._print_to_both('restarted')

        # clear dead dots list
        self.inactive_dots.empty()
        # sleep(1.0)

        # go back to main menu logic
        if self.to_main:
            # action info print
            self._print_to_both('to main')
            self.running = False
        else:
            # self._main_loop()
            pass

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.logs_file:
                    self.logs_file.close()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                self._change_lvl_value(mouse_pos)
                self._change_packsize_value(mouse_pos)
                if self.running:
                    self._restart_simulation(mouse_pos)
                    self._back_to_main(mouse_pos)
                else:
                    self._check_play_button(mouse_pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.logs_file:
                        self.logs_file.close()
                    sys.exit()

    def _check_play_button(self, mouse_pos):
        button_clicked = self.start_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.running:
            self.running = True

    def _create_pack_of_dots(self, num, x_trace=[], y_trace=[], best=False):
        if best:
            for dot in range(num):
                # create dot with mutated trajectories
                new_dot = Dot(self, x_trace, y_trace)
                self.dots.add(new_dot)
        else:
            for dot in range(num):
                new_dot = Dot(self)
                self.dots.add(new_dot)

    def _create_lvl(self, lvl):
        self.obstacles.empty()
        # it can be done better
        if lvl == 0:
            pass
        else:
            if lvl >= 1:
                # 1
                obstacle = Obstacle(self)
                obstacle.rect.center = (self.screen_rect.centerx, self.screen_rect.centery - 200)
                self.obstacles.add(obstacle)
                if lvl >= 2:
                    # 2
                    obstacle1 = Obstacle(self, 250, 25)
                    obstacle1.rect.midleft = (0, self.screen_rect.centery - 20)
                    self.obstacles.add(obstacle1)
                    if lvl >= 3:
                        # 3
                        obstacle2 = Obstacle(self, 300, 15)
                        obstacle2.rect.midright = (self.screen_rect.width, self.screen_rect.centery + 100)
                        self.obstacles.add(obstacle2)
                        if lvl >= 4:
                            # 4
                            obstacle3 = Obstacle(self, 150, 15)
                            obstacle3.rect.midright = (self.screen_rect.width, self.screen_rect.centery - 300)
                            self.obstacles.add(obstacle3)
            pass

    def _make_dead_dots_inactive(self):
        for dot in self.dots.sprites():
            if dot.death:
                self.dots.remove(dot)
                self.inactive_dots.add(dot)

    def _check_goal(self):
        for dot in self.dots:
            if pygame.sprite.collide_rect(self.goal, dot):
                dot.win = True
                dot.death = True
                return True

    def _check_obstacle(self):
        for dot in self.dots:
            for obstacle in self.obstacles:
                if pygame.sprite.collide_rect(obstacle, dot):
                    dot.death = True

    def _find_best(self):
        # set local variables for storing temporary info for analysis
        q = 0  # current q index
        div = 0  # current deviation
        check_win = 0  # current win index
        current_gen_quality = 0  # total quality of current generation

        for inactive_dot in self.inactive_dots.sprites():
            # calculation parameters of the dot
            # # steps
            steps_count = 1 / len(inactive_dot.x_history)
            steps_index = self.min_steps * steps_count
            # # deviation
            div_goal = math.sqrt((self.goal.rect.centerx - inactive_dot.rect.centerx) ** 2 +
                                 (self.goal.rect.centery - inactive_dot.rect.centery) ** 2)
            div_index = self.min_dev / div_goal
            # # win
            if inactive_dot.win and inactive_dot.death:
                win = 1
            elif (not inactive_dot.win) and (not inactive_dot.death):
                win = 0.5
            else:
                win = 0

            # for avoiding bugs in evolving
            if div_index > 1:
                div_index = 1
            elif steps_index > 1:
                steps_index = 1
            elif steps_index > 0.1 and win != 1:
                steps_index = 0

            # actual quality index
            quality_index = win + div_index + steps_index
            # sum
            current_gen_quality += quality_index

            # save best found parameters
            if quality_index > q:
                div = div_goal
                check_win = win
                steps = steps_index
                q = quality_index
                # main step
                best_dot = inactive_dot

        # info message
        msg = f'steps X : {len(best_dot.x_history)}' \
              f'\nsteps Y : {len(best_dot.y_history)}' \
              f'\nDEVIATION from the goal : {round(div, 2)}' \
              f'\nQuality Index : {round(q, 2)}' \
              f'\nSTEP Index : {round(steps, 2)}' \
              f'\nDIV Index : {round(self.min_dev/div, 2)}' \
              f'\nWIN Index : {check_win}' \
              f'\nTOTAL QI : {round(current_gen_quality, 2)}' \
              f'\nMUTATION factor : {round(self.settings.mutation_factor, 2)}\n' \

        # change mutation factor basing on how well the evolution was in general
        if current_gen_quality > self.sum_gen_quality:
            if self.settings.mutation_factor > 0.01 and not (self.gen_num in (range(5) or range(15, 20))):
                self.settings.mutation_factor -= 0.01
        else:
            pass
        # assign total gen q to a global for future comparison
        self.sum_gen_quality = current_gen_quality

        # print(f'\n\nX:'
        #       f'{type(best_dot.x_history)}'
        #       # f'\n{best_dot.x_history}'
        #       f'\nY:'
        #       f'{type(best_dot.y_history)}'
        #       # f'\n{best_dot.y_history}'
        #       )

        # saving trajectories for further use
        # # important to make them tuples (idk why)
        self.x_trace = tuple(best_dot.x_history)
        self.y_trace = tuple(best_dot.y_history)

        # assign best dot object to global variable
        self.best_dot = Dot(self, best_dot.x_history, best_dot.y_history, best=True)

        # info print
        self._print_to_both(msg)

    def _restart_simulation(self, mouse_pos):
        if self.restart_button.rect.collidepoint(mouse_pos):
            self.restart = True

    def _back_to_main(self, mouse_pos):
        if self.back_to_main.rect.collidepoint(mouse_pos):
            self.to_main = True

    def _change_lvl_value(self, mouse_pos):
        # increase
        if self.lvl_increase.rect.collidepoint(mouse_pos):
            if self.lvl < 4:
                self.lvl += 1
                self.lvl_number.prep_msg(str(self.lvl))

        # decrease
        if self.lvl_decrease.rect.collidepoint(mouse_pos):
            if self.lvl > 0:
                self.lvl -= 1
                self.lvl_number.prep_msg(str(self.lvl))

    def _change_packsize_value(self, mouse_pos):
        # increase
        if self.packsize_increase.rect.collidepoint(mouse_pos):
            if self.settings.dot_number < 10_000:
                self.settings.dot_number += 100
                self.packsize_number.prep_msg(str(self.settings.dot_number))

        # decrease
        if self.packsize_decrease.rect.collidepoint(mouse_pos):
            if self.settings.dot_number > 100:
                self.settings.dot_number -= 100
                self.packsize_number.prep_msg(str(self.settings.dot_number))

    # should be overwritten in the Button class but it didn't
    def _button_interactions(self):
        # # # changing colors # # #
        # lvl buttons
        # # '+'
        if self.lvl_increase.rect.collidepoint(pygame.mouse.get_pos()):
            self.lvl_increase.button_color = (255, 99, 71)
            self.lvl_increase.prep_msg('+')
        else:
            self.lvl_increase.button_color = self.settings.bg_color
            self.lvl_increase.prep_msg('+')
        # # '-'
        if self.lvl_decrease.rect.collidepoint(pygame.mouse.get_pos()):
            self.lvl_decrease.button_color = (255, 99, 71)
            self.lvl_decrease.prep_msg('-')
        else:
            self.lvl_decrease.button_color = self.settings.bg_color
            self.lvl_decrease.prep_msg('-')
        # size buttons
        # # '+'
        if self.packsize_increase.rect.collidepoint(pygame.mouse.get_pos()):
            self.packsize_increase.button_color = (255, 99, 71)
            self.packsize_increase.prep_msg('+')
        else:
            self.packsize_increase.button_color = self.settings.bg_color
            self.packsize_increase.prep_msg('+')
        # # '-'
        if self.packsize_decrease.rect.collidepoint(pygame.mouse.get_pos()):
            self.packsize_decrease.button_color = (255, 99, 71)
            self.packsize_decrease.prep_msg('-')
        else:
            self.packsize_decrease.button_color = self.settings.bg_color
            self.packsize_decrease.prep_msg('-')

        # 'restart' button
        if self.restart_button.rect.collidepoint(pygame.mouse.get_pos()):
            self.restart_button.button_color = (60, 179, 113)
            self.restart_button.prep_msg('restart'.upper())
        else:
            self.restart_button.button_color = (250, 128, 114)
            self.restart_button.prep_msg('restart'.upper())
        # 'back_to_main' button
        if self.back_to_main.rect.collidepoint(pygame.mouse.get_pos()):
            self.back_to_main.button_color = (60, 179, 113)
            self.back_to_main.prep_msg('main menu'.upper())
        else:
            self.back_to_main.button_color = (244, 164, 96)
            self.back_to_main.prep_msg('main menu'.upper())

        # 'start' button
        if self.start_button.rect.collidepoint(pygame.mouse.get_pos()):
            self.start_button.button_color = (60, 179, 113)
            self.start_button.prep_msg('start'.upper())
        else:
            self.start_button.button_color = (255, 222, 173)
            self.start_button.prep_msg('start'.upper())

    # should be overwritten in the Button class but it didn't
    def _buttons_placing(self, main_menu):  # don't even bother yourself to understand what is happening there
        if main_menu:
            self.lvl_button.outline_rect.center = self.screen_rect.center
            self.lvl_button.rect.center = self.lvl_button.msg_image_rect.center = \
                self.lvl_button.outline_rect.center

            self.packsize_button.outline_rect.center = self.screen_rect.center
            self.packsize_button.move_button(+(self.start_button.height + 20), 0)
            self.packsize_button.rect.center = self.packsize_button.msg_image_rect.center = \
                self.packsize_button.outline_rect.center

        else:
            self.lvl_button.outline_rect.topleft = self.screen_rect.topleft
            self.lvl_button.outline_rect.y += 30
            self.lvl_button.outline_rect.x += 30
            self.lvl_button.rect.center = self.lvl_button.msg_image_rect.center = \
                self.lvl_button.outline_rect.center

            self.packsize_button.outline_rect.centerx = self.lvl_button.outline_rect.centerx
            self.packsize_button.outline_rect.centery = self.lvl_button.outline_rect.centery + \
                                                        self.start_button.height + 20

            self.packsize_button.rect.center = self.packsize_button.msg_image_rect.center = \
                self.packsize_button.outline_rect.center

        # button placing
        self.lvl_increase.outline_rect.topright = self.lvl_button.outline_rect.bottomright
        self.lvl_increase.outline_rect.y += 2.5
        self.lvl_increase.rect.center = self.lvl_increase.msg_image_rect.center = \
            self.lvl_increase.outline_rect.center

        self.lvl_decrease.outline_rect.topleft = self.lvl_button.outline_rect.bottomleft
        self.lvl_decrease.outline_rect.y += 3
        self.lvl_decrease.rect.center = self.lvl_decrease.msg_image_rect.center = \
            self.lvl_decrease.outline_rect.center

        self.lvl_number.outline_rect.midtop = self.lvl_button.outline_rect.midbottom
        self.lvl_number.outline_rect.y += 3.5
        self.lvl_number.rect.center = self.lvl_number.msg_image_rect.center = \
            self.lvl_number.outline_rect.center

        self.packsize_increase.outline_rect.topright = self.packsize_button.outline_rect.bottomright
        self.packsize_increase.outline_rect.y += 2.5
        self.packsize_increase.rect.center = self.packsize_increase.msg_image_rect.center = \
            self.packsize_increase.outline_rect.center

        self.packsize_decrease.outline_rect.topleft = self.packsize_button.outline_rect.bottomleft
        self.packsize_decrease.outline_rect.y += 3
        self.packsize_decrease.rect.center = self.packsize_decrease.msg_image_rect.center = \
            self.packsize_decrease.outline_rect.center

        self.packsize_number.outline_rect.midtop = self.packsize_button.outline_rect.midbottom
        self.packsize_number.outline_rect.y += 3.5
        self.packsize_number.rect.center = self.packsize_number.msg_image_rect.center = \
            self.packsize_number.outline_rect.center

        self.gen_info.outline_rect.centery = self.lvl_button.outline_rect.centery
        self.gen_info.outline_rect.centerx = self.settings.screen_width - self.gen_info.width/2 - 30
        self.gen_info.rect.center = self.gen_info.msg_image_rect.center = \
            self.gen_info.outline_rect.center

        self.restart_button.outline_rect.bottomright = self.screen_rect.bottomright
        self.restart_button.outline_rect.y -= 30
        self.restart_button.outline_rect.x -= 30
        self.restart_button.rect.center = self.restart_button.msg_image_rect.center = \
            self.restart_button.outline_rect.center

        self.back_to_main.outline_rect.bottomleft = self.screen_rect.bottomleft
        self.back_to_main.outline_rect.y -= 30
        self.back_to_main.outline_rect.x += 30
        self.back_to_main.rect.center = self.back_to_main.msg_image_rect.center = \
            self.back_to_main.outline_rect.center

    # to be able track logs without additional libraries
    def _print_to_both(self, msg):
        print(msg)
        if self.logs_file:
            print(msg, file=self.logs_file)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)

        if not self.running:
            self._button_interactions()
            self._buttons_placing(main_menu=True)
            # drawing
            self.start_button.draw_button()

            self.lvl_button.draw_button()
            self.lvl_number.draw_button()
            self.lvl_increase.draw_button()
            self.lvl_decrease.draw_button()

            self.packsize_button.draw_button()
            self.packsize_number.draw_button()
            self.packsize_increase.draw_button()
            self.packsize_decrease.draw_button()
        else:
            self._button_interactions()
            self._buttons_placing(main_menu=False)
            self.gen_info.prep_msg(f'GEN : {self.gen_num}')

            self.restart_button.draw_button()
            self.back_to_main.draw_button()

            self.gen_info.draw_button()
            self.packsize_button.draw_button()

            self.lvl_button.draw_button()
            self.lvl_number.draw_button()
            self.lvl_increase.draw_button()
            self.lvl_decrease.draw_button()

            self.packsize_button.draw_button()
            self.packsize_number.draw_button()
            self.packsize_increase.draw_button()
            self.packsize_decrease.draw_button()

            self.goal.draw_goal()

            for obstacle in self.obstacles.sprites():
                obstacle.draw_obstacle()

            for dot in self.dots.sprites():
                dot.draw_dot()

            for inactive_dot in self.inactive_dots.sprites():
                inactive_dot.draw_dot()

        pygame.display.flip()


if __name__ == '__main__':
    simulation = SimulationApp()
    simulation.run_simulation()
