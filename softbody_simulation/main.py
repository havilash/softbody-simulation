import pygame
from softbody_simulation.scenes.scene import Scene
from scenes.main_menu import MainMenuScene
from consts import WIN_SIZE
from softbody_simulation.scenes.scene_manager import SceneManager


def main():
    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    initial_scene: Scene = MainMenuScene(screen)
    manager = SceneManager(screen, initial_scene)
    manager.run()


if __name__ == "__main__":
    main()
