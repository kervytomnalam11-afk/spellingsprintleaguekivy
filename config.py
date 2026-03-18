# config.py — Spelling Sprint League
# Global constants, colors, and game settings

WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Spelling Sprint League"

# ── Unity-inspired dark neon palette ──────────────────────────────────────────
BG           = (8,   8,  22)
BG_PANEL     = (16,  16, 38)
BG_CARD      = (22,  22, 52)
BG_INPUT     = (12,  12, 30)

WHITE        = (255, 255, 255)
OFF_WHITE    = (210, 210, 240)
GRAY         = ( 90,  90, 120)
LIGHT_GRAY   = (160, 160, 200)

CYAN         = (  0, 210, 255)
CYAN_DIM     = (  0, 100, 140)
PURPLE       = (170,  60, 255)
PURPLE_DIM   = ( 80,  30, 140)
ORANGE       = (255, 140,   0)
GREEN        = ( 50, 230,  90)
RED          = (255,  60,  60)
YELLOW       = (255, 220,   0)
PINK         = (255,  80, 180)

CORRECT_COL  = GREEN
WRONG_COL    = RED
PENDING_COL  = LIGHT_GRAY
CURSOR_COL   = CYAN

# ── Game Modes ────────────────────────────────────────────────────────────────
GAME_MODES = {
    "Burst":          {"time":  30, "desc": "30s sprint",          "color": ORANGE,  "sentences": False},
    "Sprint":         {"time":  60, "desc": "60s classic",         "color": CYAN,    "sentences": False},
    "Marathon":       {"time":  90, "desc": "90s endurance",       "color": PURPLE,  "sentences": False},
    "Century":        {"time": 120, "desc": "120s challenge",      "color": PINK,    "sentences": False},
    "Endless":        {"time":   0, "desc": "No time limit",       "color": GREEN,   "sentences": False},
    "Sentence Race":  {"time":  60, "desc": "Type full sentences", "color": YELLOW,  "sentences": True},
}

DIFFICULTIES = {
    "Easy":   {"desc": "Common words",         "color": GREEN},
    "Medium": {"desc": "Mixed vocabulary",     "color": YELLOW},
    "Hard":   {"desc": "Advanced words",       "color": RED},
    "Mixed":  {"desc": "Surprise me!",         "color": PURPLE},
}

# ── League System ─────────────────────────────────────────────────────────────
LEAGUES = [
    ("Bronze",   0,   (180, 100,  40)),
    ("Silver",  30,   (180, 180, 200)),
    ("Gold",    50,   (255, 200,   0)),
    ("Platinum",70,   (100, 220, 220)),
    ("Diamond", 90,   (120, 160, 255)),
]

def get_league(wpm):
    result = LEAGUES[0]
    for name, threshold, color in LEAGUES:
        if wpm >= threshold:
            result = (name, threshold, color)
    return result

# ── Network ───────────────────────────────────────────────────────────────────
NET_PORT    = 54321
NET_TIMEOUT = 5.0
