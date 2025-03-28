import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BG_COLOR = "#192333"
TRANSPARENT_COLOR = BG_COLOR
TRANSPARENT_HOVER_COLOR = "#303947"
FONT_COLOR = WHITE

PROJECT_PATH = "softbody_simulation"
FONTS_PATH = "fonts"
FONT = os.path.join(PROJECT_PATH, FONTS_PATH, "minecraft.ttf")

FPS = 60
WIN_SIZE = 800, 600

GRAVITY = -9.81 * 20
