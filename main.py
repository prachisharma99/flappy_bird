import pygame
from flappy_bird import *


def main():
    g = Game()

    running = True
    while running:
        g.key_pressed = False

        # get all events
        for event in pygame.event.get():
            # if event is quit, then close the game window
            if event.type == pygame.QUIT:
                running = False

            # if event is a key press, check if SPACE, UP key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    g.key_pressed = True
            # if event is a mouse click
            if event.type == pygame.MOUSEBUTTONUP:
                g.key_pressed = True

        # if key_pressed and game_on = False, switch to state 2
        if not g.game_on and g.key_pressed:
            g.game_on = True

        # calling functions based on state 1, 2, 3
        if g.game_over:
            g.end_game()
        elif not g.game_on:
            g.game_not_started()
        elif g.game_on:
            g.play()


if __name__ == '__main__':
    main()
