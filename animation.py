# animation.py — Animated Race Track for Spelling Sprint League
"""
AnimatedRaceTrack renders one lane per player/racer with:
  - Pixel-art car that moves with progress
  - Car bounce rate scales with WPM
  - Road dash-lines scroll at WPM-dependent speed
  - Exhaust puffs: more smoke = faster typing
  - Ghost car is semi-transparent with purple tint
  - Finish-line chequered flag
  - Works for solo, ghost race, local multi, wifi multi
"""

import pygame, math, random
from config import (
    BG, BG_PANEL, BG_CARD, CYAN, CYAN_DIM, PURPLE, PURPLE_DIM,
    ORANGE, GREEN, RED, YELLOW, PINK, WHITE, GRAY, OFF_WHITE, LIGHT_GRAY
)
import ui

# ── Pixel car shapes (44×22 blit surface) ─────────────────────────────────────

def _make_car_surface(body_col: tuple, roof_col: tuple,
                      wheel_col: tuple = (30, 30, 50),
                      alpha: int = 255) -> pygame.Surface:
    """Draw a tiny pixel-art car facing right."""
    W, H = 44, 22
    s = pygame.Surface((W, H), pygame.SRCALPHA)

    # body
    pygame.draw.rect(s, (*body_col, alpha), (2, 8, 40, 11), border_radius=3)
    # roof
    pygame.draw.rect(s, (*roof_col, alpha), (8, 3, 24, 9), border_radius=2)
    # windows
    win = (*ui.lerp_color(roof_col, (180, 220, 255), 0.4), min(alpha, 160))
    pygame.draw.rect(s, win, (10, 4, 10, 7), border_radius=1)
    pygame.draw.rect(s, win, (22, 4, 8,  7), border_radius=1)
    # headlight
    pygame.draw.rect(s, (255, 230, 80, alpha), (38, 11, 5, 3), border_radius=1)
    # tail-light
    pygame.draw.rect(s, (220, 50, 50, alpha), (1, 11, 4, 3), border_radius=1)
    # wheels
    for cx in (10, 34):
        pygame.draw.circle(s, (*wheel_col, alpha), (cx, 19), 4)
        pygame.draw.circle(s, (80, 80, 100, alpha), (cx, 19), 2)
    return s


# Pre-built car surfaces for common colours
_CAR_CACHE: dict[tuple, pygame.Surface] = {}

def get_car(body_col: tuple, is_ghost: bool = False) -> pygame.Surface:
    key = (body_col, is_ghost)
    if key not in _CAR_CACHE:
        roof = ui.lerp_color(body_col, (0, 0, 0), 0.55)
        alpha = 130 if is_ghost else 255
        _CAR_CACHE[key] = _make_car_surface(body_col, roof, alpha=alpha)
    return _CAR_CACHE[key]


# ── Exhaust particle ──────────────────────────────────────────────────────────

class ExhaustPuff:
    """A single smoke puff that drifts left and fades."""

    def __init__(self, x: float, y: float, color: tuple):
        self.x     = x
        self.y     = y + random.randint(-4, 4)
        self.color = color
        self.r     = random.uniform(2.5, 5.0)
        self.vx    = random.uniform(-1.8, -0.6)
        self.vy    = random.uniform(-0.4, 0.4)
        self.alpha = random.randint(140, 200)
        self.life  = 1.0  # 0→dead

    def update(self, dt: float):
        self.x     += self.vx
        self.y     += self.vy
        self.r     += 0.8 * dt
        self.alpha -= 260 * dt
        self.life  -= dt * 1.8

    @property
    def alive(self) -> bool:
        return self.life > 0 and self.alpha > 0

    def draw(self, surf: pygame.Surface):
        a = max(0, min(255, int(self.alpha)))
        s = pygame.Surface((int(self.r*2+2), int(self.r*2+2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], a),
                           (int(self.r)+1, int(self.r)+1), max(1, int(self.r)))
        surf.blit(s, (int(self.x - self.r), int(self.y - self.r)))


# ── Road stripe ───────────────────────────────────────────────────────────────

class RoadStripe:
    """Animated dashed centre-line that scrolls at WPM-dependent speed."""

    DASH_W  = 22
    GAP_W   = 18
    PERIOD  = DASH_W + GAP_W

    def __init__(self, lane_rect: pygame.Rect):
        self.rect   = lane_rect
        self.offset = 0.0

    def update(self, dt: float, wpm: float):
        speed = max(20, wpm * 3.5)
        self.offset = (self.offset + speed * dt) % self.PERIOD

    def draw(self, surf: pygame.Surface):
        y  = self.rect.centery
        x  = self.rect.x - self.offset
        col = (40, 40, 70)
        while x < self.rect.right:
            x1 = max(x, self.rect.x)
            x2 = min(x + self.DASH_W, self.rect.right)
            if x2 > x1:
                pygame.draw.line(surf, col, (int(x1), y), (int(x2), y), 2)
            x += self.PERIOD


# ── Lane ──────────────────────────────────────────────────────────────────────

class RaceLane:
    """One horizontal lane: road + car + exhaust + label."""

    CAR_W, CAR_H = 44, 22
    MAX_PUFFS    = 25
    PUFF_INTERVAL_BASE = 0.22   # seconds between puffs at 0 wpm

    def __init__(self, rect: pygame.Rect, name: str, color: tuple,
                 is_ghost: bool = False):
        self.rect        = rect
        self.name        = name
        self.color       = color
        self.is_ghost    = is_ghost
        self.progress    = 0.0   # 0–1
        self.wpm         = 0.0
        self._bounce_t   = 0.0
        self._puff_t     = 0.0
        self._puffs: list[ExhaustPuff] = []
        self._stripe     = RoadStripe(rect)
        self._car_surf   = get_car(color, is_ghost)
        self._finished   = False

    def set(self, progress: float, wpm: float):
        self.progress = min(1.0, max(0.0, progress))
        self.wpm      = max(0.0, wpm)
        if progress >= 1.0:
            self._finished = True

    def update(self, dt: float):
        self._bounce_t += dt
        self._stripe.update(dt, self.wpm)

        # Exhaust puffs — interval shrinks as WPM rises
        interval = max(0.06, self.PUFF_INTERVAL_BASE - self.wpm * 0.001)
        self._puff_t += dt
        if self.wpm > 2 and self._puff_t >= interval:
            self._puff_t = 0.0
            cx, cy = self._car_pos()
            dim = ui.lerp_color(self.color, (0, 0, 0), 0.5)
            count = 1 if self.wpm < 40 else 2 if self.wpm < 70 else 3
            for _ in range(count):
                if len(self._puffs) < self.MAX_PUFFS:
                    self._puffs.append(ExhaustPuff(cx, cy, dim))

        self._puffs = [p for p in self._puffs if p.alive]
        for p in self._puffs:
            p.update(dt)

    def _car_pos(self) -> tuple[int, int]:
        """Return (cx, cy) — left edge x of the car, centre y of the lane."""
        pad   = 4
        track = self.rect.width - self.CAR_W - pad * 2
        cx    = self.rect.x + pad + int(self.progress * track)
        # Bounce: amplitude scales with WPM
        amp   = min(3.5, self.wpm * 0.04)
        speed = 4 + self.wpm * 0.06
        cy    = self.rect.centery - self.CAR_H // 2 - int(amp * abs(math.sin(self._bounce_t * speed)))
        return cx, cy

    def draw(self, surf: pygame.Surface, f_label: pygame.font.Font):
        r = self.rect

        # Road background
        road_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        road_surf.fill((*BG_PANEL, 200))
        surf.blit(road_surf, r.topleft)
        pygame.draw.rect(surf, CYAN_DIM if not self.is_ghost else PURPLE_DIM,
                         r, width=1, border_radius=5)

        # Progress fill
        if self.progress > 0:
            fill_w = max(0, int(r.width * self.progress))
            fill_s = pygame.Surface((fill_w, r.h), pygame.SRCALPHA)
            fill_s.fill((*self.color, 30))
            surf.blit(fill_s, r.topleft)

        # Road stripe
        self._stripe.draw(surf)

        # Chequered finish flag (last 4px)
        tile = 4
        for row in range(r.h // tile):
            for col in range(2):
                fx = r.right - tile * 2 + col * tile
                fy = r.top + row * tile
                c  = WHITE if (row + col) % 2 == 0 else (20, 20, 40)
                pygame.draw.rect(surf, c, (fx, fy, tile, tile))

        # Exhaust puffs (behind car)
        for p in self._puffs:
            p.draw(surf)

        # Car
        cx, cy = self._car_pos()
        surf.blit(self._car_surf, (cx, cy))

        # Ghost shimmer overlay
        if self.is_ghost:
            ghost_s = pygame.Surface((self.CAR_W, self.CAR_H), pygame.SRCALPHA)
            ghost_s.fill((180, 100, 255, 20))
            surf.blit(ghost_s, (cx, cy))

        # Name label (right of track)
        lbl_col = self.color if not self.is_ghost else PURPLE
        name_s  = f_label.render(self.name, True, lbl_col)
        surf.blit(name_s, (r.x + 6, r.y + 2))

        # WPM badge (top-right)
        wpm_str = f"{self.wpm:.0f} wpm"
        wpm_s   = f_label.render(wpm_str, True, lbl_col)
        surf.blit(wpm_s, (r.right - wpm_s.get_width() - 24, r.y + 2))

        # Finish indicator
        if self._finished:
            fin_s = f_label.render("DONE", True, GREEN)
            surf.blit(fin_s, (r.right - fin_s.get_width() - 6, r.centery - fin_s.get_height() // 2))


# ── AnimatedRaceTrack (the full multi-lane widget) ────────────────────────────

class AnimatedRaceTrack:
    """
    Drop-in animated race track for any game screen.

    Usage
    -----
    In screen.__init__:
        self._track = AnimatedRaceTrack(x, y, width)

    Add lanes once (or after a mode change):
        self._track.add_lane("You",     CYAN,   is_ghost=False)
        self._track.add_lane("Ghost",   PURPLE, is_ghost=True)

    Each frame:
        self._track.update(dt)
        self._track.set_lane(0, progress=0.45, wpm=52.3)
        self._track.draw(surface)
    """

    LANE_H   = 52
    LANE_GAP = 8

    def __init__(self, x: int, y: int, width: int):
        self.x      = x
        self.y      = y
        self.width  = width
        self._lanes: list[RaceLane] = []
        self._f     = ui.font(11)

    @property
    def total_height(self) -> int:
        n = len(self._lanes)
        return n * self.LANE_H + max(0, n - 1) * self.LANE_GAP

    def clear(self):
        self._lanes = []

    def add_lane(self, name: str, color: tuple, is_ghost: bool = False) -> int:
        idx  = len(self._lanes)
        rect = pygame.Rect(
            self.x,
            self.y + idx * (self.LANE_H + self.LANE_GAP),
            self.width,
            self.LANE_H,
        )
        self._lanes.append(RaceLane(rect, name, color, is_ghost))
        return idx

    def set_lane(self, idx: int, progress: float, wpm: float):
        if 0 <= idx < len(self._lanes):
            self._lanes[idx].set(progress, wpm)

    def update(self, dt: float):
        for lane in self._lanes:
            lane.update(dt)

    def draw(self, surf: pygame.Surface):
        for lane in self._lanes:
            lane.draw(surf, self._f)

    def leader(self) -> int:
        """Return index of the lane currently in the lead."""
        if not self._lanes:
            return 0
        return max(range(len(self._lanes)), key=lambda i: self._lanes[i].progress)
