HIDE_CURSOR = "\033[?25l"
BORDER_CHARS = {
    "single": {
        "topLeft": "┏",
        "topRight": "┓",
        "botLeft": "┗",
        "botRight": "┛",
        "horizontal": "━",
        "vertical": "┃",
    },
    "double": {
        "topLeft": "╔",
        "topRight": "╗",
        "botLeft": "╚",
        "botRight": "╝",
        "horizontal": "═",
        "vertical": "║",
    },
}
TILE_CHARS = {"upper": {0: "┌─┐", 1: "▗▄▖"}, "lower": {0: "└─┘", 1: "▝▀▘"}}
MOVES = {"UP": [-1, 0], "LEFT": [0, -1], "DOWN": [1, 0], "RIGHT": [0, 1]}
