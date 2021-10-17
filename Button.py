# class for creating buttons to press
import pygame.font


class Button:

    # set the button attributes
    def __init__(self, env, msg, width=130, height=45, font=36, outline=2, color=(255, 222, 173)):

        self.screen = env.screen
        self.screen_rect = env.screen.get_rect()

        # set sizes of the button
        self.width, self.height = width, height
        self.outline_width = outline

        # set colouring of the background and text
        self.button_color = color
        self.tex_color = (0, 0, 0)

        # set the font
        self.font = pygame.font.SysFont(None, font)  # None = default font, 48 = size

        # set the position of the button
        self.outline_rect = pygame.Rect(0, 0, self.width + self.outline_width, self.height + self.outline_width)
        self.rect = pygame.Rect(0, 0, self.width, self.height)  # make rect object of the button with set sizes
        self.rect.center = self.screen_rect.center
        self.outline_rect.center = self.rect.center

        # set button message
        self.prep_msg(str(msg).upper())

    # function to make str(msg) a image for treating as a rect object
    def prep_msg(self, msg):
        # to render txt to img
        self.msg_image = self.font.render(msg, True, self.tex_color, self.button_color)  # 'True' to smoother the text
        # get rectangle of the created img
        self.msg_image_rect = self.msg_image.get_rect()
        # center text to the button
        self.msg_image_rect.center = self.rect.center

    def move_button(self, offsety, offsetx):
        # y
        self.rect.centery += offsety
        self.outline_rect.centery += offsety
        self.msg_image_rect.centery += offsety
        # x
        self.rect.centerx += offsetx
        self.outline_rect.centerx += offsetx
        self.msg_image_rect.centerx += offsetx

    # for actually draw a button with txt
    def draw_button(self):
        self.screen.fill((0, 0, 0), self.outline_rect)
        self.screen.fill(self.button_color, self.rect)  # fill a button-size rectangle with button color
        self.screen.blit(self.msg_image, self.msg_image_rect)  # idk, blit means draw
