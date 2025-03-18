import pygame
from scenes.scene_manager import SceneManager, Scene
from scenes.main_menu import MainMenu
from consts import WIN_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    initial_scene: Scene = MainMenu(screen)
    manager = SceneManager(screen, initial_scene)
    manager.run()


if __name__ == "__main__":
    main()
