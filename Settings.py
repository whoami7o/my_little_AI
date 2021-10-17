class Settings:
    def __init__(self):
        # screen settings
        self.screen_width = 700  # pixels
        self.screen_height = 800  # pixels
        self.bg_color = (192, 192, 192)  # grey

        # dots
        self.dot_color = (0, 0, 0)  # black
        self.dead_dot_color = (255, 140, 0)  # orange
        self.win_dot_color = (0, 128, 0)  # green
        self.best_dot_color = (255, 0, 255)  # purple
        self.dot_step = 2.7
        self.dot_size = 3  # optimal size = 5
        self.dot_number = 500
        self.mutation_factor = 0.2  # optimal 0.1

        # move options
        self.move_options = (-1, 0, 1)

        # goal
        self.goal_color = (200, 0, 0)
        self.goal_size = 30  # optimal size = 50

        # obstacle
        self.obstacle_length = 200
        self.obstacle_width = 35
        self.obstacle_color = (65, 105, 225)  # blue
