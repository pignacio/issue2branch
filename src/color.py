_COLOR_CODE = '\033[{}m'


def _color_code(code):
    return _COLOR_CODE.format(code)


BLACK = _color_code(30)
RED = _color_code(31)
GREEN = _color_code(32)
YELLOW = _color_code(33)
BLUE = _color_code(34)
MAGENTA = _color_code(35)
CYAN = _color_code(36)
WHITE = _color_code(37)
RESET = _color_code(39)

BRIGHT = _color_code(1)
RESET_ALL = _color_code(0)


def _color_func(color):
    def func(string):
        return "{}{}{}".format(color, string, RESET_ALL)
    return func


def _color_func_pair(color):
    return _color_func(color), _color_func(color + BRIGHT)


black, bright_black = _color_func_pair(BLACK)
red, bright_red = _color_func_pair(RED)
green, bright_green = _color_func_pair(GREEN)
yellow, bright_yellow = _color_func_pair(YELLOW)
blue, bright_blue = _color_func_pair(BLUE)
magenta, bright_magenta = _color_func_pair(MAGENTA)
cyan, bright_cyan = _color_func_pair(CYAN)
white, bright_white = _color_func_pair(WHITE)
