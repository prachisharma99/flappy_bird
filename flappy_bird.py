import pygame
from random import randrange
import pickle


class GameScreen():
    def __init__(self):
        self.SCREEN_HEIGHT = 500
        self.SCREEN_WIDTH = 500
        self.CAPTION = 'Flappy Bird'

    def create_screen(self):
        screen = pygame.display.set_mode((self.SCREEN_HEIGHT, self.SCREEN_WIDTH))
        pygame.display.set_caption(self.CAPTION)

        return screen

    def update(self):
        pygame.display.flip()
        pygame.time.delay(200)


class Background(GameScreen):
    def __init__(self, game_screen):
        self.gs = game_screen
        self.bg_img = "images/bg.png"
        self.fence_img = "images/fence.png"

        self.bg = pygame.image.load(self.bg_img)
        self.fence = pygame.image.load(self.fence_img)

        self.FENCE_YPOS = 455
        self.fences = []

    def display(self, screen):
        screen.blit(self.bg, (0, 0))

        for fence_rect in self.fences:
            screen.blit(self.fence, fence_rect)

    def update_background(self, screen):

        # Add Fence if there are 0 fence
        if not self.fences:
            rect = self.fence.get_rect()
            rect.topleft = (0, self.FENCE_YPOS)
            self.fences.append(rect)

        # Add fence
        if self.fences[-1].right <= self.gs.SCREEN_WIDTH:
            rect = self.fence.get_rect()
            rect.topleft = (self.fences[-1].right, self.FENCE_YPOS)
            self.fences.append(rect)

        # Remove Fence
        if self.fences[0].right <= 0:
            del self.fences[0]

        # Move the fence by changing x coord
        for fence_rect in self.fences:
            fence_rect.x -= 10

        self.display(screen)


class Bird():
    def __init__(self):

        self.bird_img = "images/bird.png"
        self.birdup_img = "images/bird_up.png"
        self.birddown_img = "images/bird_down.png"

        self.bird = pygame.image.load(self.bird_img)
        self.birdup = pygame.image.load(self.birdup_img)
        self.birddown = pygame.image.load(self.birddown_img)

        self.bird_rect = self.bird.get_rect()
        self.bird_rect.topleft = (40, 200)

        self.wing_up = True
        self.bird_in_use = None
        self.bird_angle = 0

        self.BIRD_Y = 40
        self.BIRD_CHANGE_ANGLE = 60
        self.BIRD_MAX_DOWN_ANGLE = -90
        self.BIRD_MAX_UP_ANGLE = 45
        self.FENCE_YPOS = 455

    def display(self, screen):
        screen.blit(self.bird_in_use, self.bird_rect)

    def fly(self, screen, down=False):

        # Make bird fly by toggling between bird up and bird down image
        if self.wing_up:
            self.wing_up = False
            self.bird_in_use = self.birdup
        else:
            self.wing_up = True
            self.bird_in_use = self.birddown

        # If bird is flying down, use bird image
        if down:
            self.bird_in_use = self.bird

        # Rotate the bird
        self.bird_in_use = pygame.transform.rotate(self.bird_in_use, self.bird_angle)

        self.display(screen)

    def fall_down(self, s, bg):
        self.fly_up_down(s, bg, False)

    def fly_up_down(self, s, bg, key_pressed):

        if key_pressed:
            self.bird_rect.y -= self.BIRD_Y
            self.bird_angle = self.BIRD_MAX_UP_ANGLE

        else:
            # Make the bird fly down by changing y co-ordinate
            # Bird should not fly beyond fence
            self.bird_rect.y += self.BIRD_Y
            if not self.bird_rect.bottom < self.FENCE_YPOS:
                self.bird_rect.bottom = self.FENCE_YPOS

            # Gradually change the bird angle upto BIRD_MAX_DOWN_ANGLE
            new_bird_angle = self.bird_angle - self.BIRD_CHANGE_ANGLE
            if new_bird_angle > self.BIRD_MAX_DOWN_ANGLE:
                self.bird_angle = new_bird_angle
            else:
                self.bird_angle = self.BIRD_MAX_DOWN_ANGLE

        self.fly(s, down=not key_pressed)

    def is_hit(self, bg, pipe):
        """
        If bird hit fence returns True
        If bird hits pipe returns True
        else False
        """

        if self.bird_rect.bottom == bg.FENCE_YPOS:
            return True

        if pipe.pipes:

            # hit bottom pipe tube
            if self.bird_rect.colliderect(pipe.pipes[0]['rect']):
                return True

            # hit bottom pipe cup
            if self.bird_rect.colliderect(pipe.pipes[0]['bottom_cup_rect']):
                return True

            # hit top pipe tube
            if self.bird_rect.colliderect(pipe.pipes[0]['top_pipe_rect']):
                return True

            # hit top pipe cup
            if self.bird_rect.colliderect(pipe.pipes[0]['top_cup_rect']):
                return True

        return False


class Score(GameScreen):
    def __init__(self, game_screen):
        self.gs = game_screen

        self.SCORE_COLOR = (255, 255, 0)
        self.SCORE_POS = (self.gs.SCREEN_WIDTH//2, 100)
        self.score = 0

        self.consider_pipe = False
        self.pipe_index = None

        pygame.font.init()
        self.impact_font = pygame.font.SysFont("impact", 40)

    def display(self, screen, text):
        label = self.impact_font.render(text, 1, self.SCORE_COLOR)
        screen.blit(label, self.SCORE_POS)

    def multi_line_display(self, screen, text):
        lines = text.splitlines()
        label_rect = None

        for line in lines:
            label = self.impact_font.render(line, 1, self.SCORE_COLOR)
            if not label_rect:
                label_rect = label.get_rect()
                label_rect.center = (250, 100)
            else:
                label_rect.top = label_rect.bottom

            screen.blit(label, label_rect)


    def final_board(self, screen):

        # calculating best score
        try:
            fp = open('.best_score.pickle', 'rb')
        except FileNotFoundError:
            best_score = self.score
        else:
            best_score = pickle.load(fp)
            if self.score > best_score:
                best_score = self.score
            fp.close()

        # save best score
        with open('.best_score.pickle', 'wb') as fp:
            pickle.dump(best_score, fp)


        board_text = 'SCORE\n' + str(self.score) + '\nBEST\n' + str(best_score) + '\nSPACE to RESTART'
        self.multi_line_display(screen, text=board_text)

    def update(self, screen, bird, pipe):

        # find pipe index for which pipe to be considered next
        for index, p in enumerate(pipe.pipes):
            if bird.bird_rect.right <= p['top_cup_rect'].left or bird.bird_rect.left <= (p['top_cup_rect'].right + pipe.CHANGE_X):
                self.pipe_index = index
                break

        # increase score if a pipe is passed
        if bird.bird_rect.left > pipe.pipes[self.pipe_index]['top_cup_rect'].right:
            self.score += 1

        self.display(screen, text=str(self.score))


class Pipe():
    def __init__(self, game_screen):
        self.gs = game_screen
        self.PIPE_IMG = 'images/pipe.png'
        self.PIPE_CUP_IMG = 'images/pipe_cup.png'
        self.FENCE_YPOS = 455
        self.DISTANCE = 200
        self.GAP = 300
        self.CHANGE_X = 10

        self.pipe = pygame.image.load(self.PIPE_IMG)
        self.pipe_cup = pygame.image.load(self.PIPE_CUP_IMG)

        self.pipes = []

    def display(self, screen):
        for pipe in self.pipes:
            screen.blit(pipe['img'], pipe['rect'])
            screen.blit(self.pipe_cup, pipe['bottom_cup_rect'])

            screen.blit(pipe['top_pipe'], pipe['top_pipe_rect'])
            screen.blit(self.pipe_cup, pipe['top_cup_rect'])

    def add_pipe(self):
        # generate random heights
        height = randrange(80, 100)
        pipe = pygame.transform.scale(self.pipe, (self.pipe.get_width(), height))
        pipe_rect = pipe.get_rect()
        pipe_rect.bottomleft = (self.gs.SCREEN_WIDTH, self.FENCE_YPOS)

        height = pipe_rect.top - self.GAP
        top_pipe = pygame.transform.scale(self.pipe, (self.pipe.get_width(), height))
        top_pipe_rect = top_pipe.get_rect()
        top_pipe_rect.topleft = (self.gs.SCREEN_WIDTH, 0)

        # bottom cup
        bottom_cup_rect = self.pipe_cup.get_rect()
        bottom_cup_rect.midbottom = pipe_rect.midtop

        # top cup
        top_cup_rect = self.pipe_cup.get_rect()
        top_cup_rect.midtop = top_pipe_rect.midbottom

        self.pipes.append(
                        {
                            'img': pipe,
                            'rect': pipe_rect,
                            'bottom_cup_rect': bottom_cup_rect,
                            'top_pipe': top_pipe,
                            'top_pipe_rect': top_pipe_rect,
                            'top_cup_rect': top_cup_rect
                        }
                        )

    def update_pipe(self, screen):

        # Add pipe if 0 pipes
        if not self.pipes:
            self.add_pipe()

        # Add more pipes
        if self.gs.SCREEN_WIDTH - self.pipes[-1]['rect'].right >= self.DISTANCE:
            self.add_pipe()

        # Remove pipe if it is not in game window
        if self.pipes[0]['rect'].right < 0:
            del self.pipes[0]

        # change the pipe rect left x position
        for index, pipe in enumerate(self.pipes):
            self.pipes[index]['rect'].left = pipe['rect'].left - self.CHANGE_X
            self.pipes[index]['top_pipe_rect'].left = pipe['top_pipe_rect'].left - self.CHANGE_X

            self.pipes[index]['bottom_cup_rect'].midbottom = pipe['rect'].midtop
            self.pipes[index]['top_cup_rect'].midtop = pipe['top_pipe_rect'].midbottom

        self.display(screen)


class Game():
    def __init__(self):
        self.gs = GameScreen()
        self.s = self.gs.create_screen()
        self.bg = Background(self.gs)
        self.bird = Bird()
        self.pipe = Pipe(self.gs)
        self.score = Score(self.gs)

        """
        There are three states for the game
        1. Game not started (initial screen), game_on = False
        2. Game started, game_on = True
        3. Game over, game_over = True
        """
        self.game_on = False
        self.game_over = False

        self.key_pressed = False

    def play(self):

        if not self.game_over and self.bird.is_hit(self.bg, self.pipe):
            self.game_over = True

        self.bg.update_background(self.s)
        self.pipe.update_pipe(self.s)
        self.bird.fly_up_down(self.s, self.bg, self.key_pressed)
        self.score.update(self.s, self.bird, self.pipe)
        self.gs.update()

    def game_not_started(self):
        self.bg.update_background(self.s)
        self.bird.fly(self.s)
        self.gs.update()

    def end_game(self):
        self.bg.display(self.s)
        self.pipe.display(self.s)
        self.bird.fall_down(self.s, self.bg)
        self.score.final_board(self.s)
        self.gs.update()
