# ui.py — Reusable Unity-inspired UI components for Pygame
import pygame, math, random
from config import *


# ── Helpers ───────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def glow_surf(w, h, color, radius=18):
    """Return an RGBA surface with a soft glow rectangle."""
    s = pygame.Surface((w + radius*2, h + radius*2), pygame.SRCALPHA)
    for i in range(radius, 0, -2):
        alpha = int(180 * (1 - i/radius)**2)
        col   = (*color[:3], alpha)
        pygame.draw.rect(s, col,
                         (radius-i, radius-i, w+i*2, h+i*2),
                         border_radius=radius//2+3)
    return s

def draw_panel(surf, rect, color=BG_PANEL, border=CYAN_DIM, radius=10, alpha=220):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius)
    surf.blit(s, rect.topleft)
    pygame.draw.rect(surf, border, rect, width=1, border_radius=radius)

def draw_text(surf, text, font, color, x, y, anchor="topleft", shadow=True):
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        r  = sh.get_rect(**{anchor: (x+2, y+2)})
        surf.blit(sh, r)
    img = font.render(text, True, color)
    r   = img.get_rect(**{anchor: (x, y)})
    surf.blit(img, r)
    return r

def draw_glow_text(surf, text, font, color, x, y, anchor="center"):
    # glow pass
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            if dx or dy:
                img = font.render(text, True, (*color[:3],))
                gs  = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                gs.fill((0, 0, 0, 0))
                gs.blit(img, (0, 0))
                gs.set_alpha(60)
                r   = img.get_rect(**{anchor: (x+dx, y+dy)})
                surf.blit(gs, r)
    img = font.render(text, True, color)
    r   = img.get_rect(**{anchor: (x, y)})
    surf.blit(img, r)
    return r


# ── Fonts (loaded lazily) ─────────────────────────────────────────────────────

_fonts: dict[str, pygame.font.Font] = {}

def font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _fonts:
        try:
            name = pygame.font.match_font(
                "bahnschrift,consolas,robotomono,monospace,courier")
            _fonts[key] = pygame.font.Font(name, size)
        except Exception:
            _fonts[key] = pygame.font.SysFont("monospace", size, bold=bold)
    return _fonts[key]


# ── Button ────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, label,
                 color=CYAN, text_color=BG, radius=8):
        self.rect       = pygame.Rect(x, y, w, h)
        self.label      = label
        self.color      = color
        self.text_color = text_color
        self.radius     = radius
        self._hover     = False
        self._scale     = 1.0
        self.enabled    = True

    def handle(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surf):
        target = 1.05 if self._hover else 1.0
        self._scale = lerp(self._scale, target, 0.2)
        w  = int(self.rect.width  * self._scale)
        h  = int(self.rect.height * self._scale)
        cx = self.rect.centerx
        cy = self.rect.centery
        r  = pygame.Rect(cx - w//2, cy - h//2, w, h)

        col = lerp_color(self.color, WHITE, 0.2) if self._hover else self.color
        alpha = 255 if self.enabled else 100

        gs = glow_surf(r.width, r.height, col, radius=12)
        surf.blit(gs, (r.x-12, r.y-12), special_flags=pygame.BLEND_RGBA_ADD)

        s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), s.get_rect(), border_radius=self.radius)
        surf.blit(s, r.topleft)

        pygame.draw.rect(surf, col, r, width=2, border_radius=self.radius)
        f = font(18, bold=True)
        draw_text(surf, self.label, f, self.text_color,
                  r.centerx, r.centery, anchor="center", shadow=False)


# ── TextInput ─────────────────────────────────────────────────────────────────

class TextInput:
    def __init__(self, x, y, w, h, placeholder="", max_len=30):
        self.rect        = pygame.Rect(x, y, w, h)
        self.placeholder = placeholder
        self.max_len     = max_len
        self.text        = ""
        self.active      = False
        self._cursor_t   = 0.0

    def handle(self, event):
        # activate on mouse or finger tap
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                try:
                    pygame.key.start_text_input()
                except Exception:
                    pass
        if event.type == pygame.FINGERDOWN:
            # In Kivy mode there is no pygame display; coordinates are
            # already mapped to the surface size before dispatch.
            px = int(getattr(event, 'x', 0))
            py = int(getattr(event, 'y', 0))
            self.active = self.rect.collidepoint(px, py)
        # TEXTINPUT handles ALL printable characters (no double-input)
        if self.active and event.type == pygame.TEXTINPUT:
            for ch in event.text:
                if len(self.text) < self.max_len and ch.isprintable():
                    self.text += ch
        # KEYDOWN handles special keys only
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.active = False
            # Do NOT handle printable chars here — TEXTINPUT does that

    def draw(self, surf, dt=0.016):
        self._cursor_t = (self._cursor_t + dt) % 1.0
        border = CYAN if self.active else GRAY
        draw_panel(surf, self.rect, BG_INPUT, border, radius=6)
        f = font(20)
        txt = self.text or self.placeholder
        col = OFF_WHITE if self.text else GRAY
        tx  = self.rect.x + 12
        ty  = self.rect.centery
        draw_text(surf, txt, f, col, tx, ty, anchor="midleft")
        if self.active and self._cursor_t < 0.5:
            cw = f.size(self.text)[0]
            cx = tx + cw + 2
            pygame.draw.line(surf, CURSOR_COL,
                             (cx, ty - 10), (cx, ty + 10), 2)


# ── WPM / Accuracy Bar ────────────────────────────────────────────────────────

class StatBar:
    """Thin animated progress bar."""
    def __init__(self, x, y, w, h, color=CYAN, max_val=100.0):
        self.rect    = pygame.Rect(x, y, w, h)
        self.color   = color
        self.max_val = max_val
        self._val    = 0.0
        self._drawn  = 0.0

    def set(self, val):
        self._val = max(0, min(val, self.max_val))

    def draw(self, surf):
        self._drawn = lerp(self._drawn, self._val, 0.1)
        pygame.draw.rect(surf, BG_PANEL, self.rect, border_radius=4)
        frac = self._drawn / self.max_val if self.max_val else 0
        fw   = max(0, int(self.rect.width * frac))
        if fw:
            fr = pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.height)
            pygame.draw.rect(surf, self.color, fr, border_radius=4)
        pygame.draw.rect(surf, GRAY, self.rect, width=1, border_radius=4)


# ── Particle Background ───────────────────────────────────────────────────────

class Particle:
    CHARS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*+-=<>?/\\|")

    def __init__(self):
        self._reset(spawn_top=False)

    def _reset(self, spawn_top=True):
        self.x     = random.randint(0, WIDTH)
        self.y     = -10 if spawn_top else random.randint(0, HEIGHT)
        self.speed = random.uniform(0.3, 1.2)
        self.alpha = random.randint(15, 60)
        self.size  = random.randint(10, 18)
        self.char  = random.choice(self.CHARS)
        self.color = random.choice([CYAN_DIM, PURPLE_DIM, (30, 60, 80)])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + 20:
            self._reset(spawn_top=True)

    def draw(self, surf):
        f   = font(self.size)
        img = f.render(self.char, True, self.color)
        img.set_alpha(self.alpha)
        surf.blit(img, (int(self.x), int(self.y)))


class ParticleField:
    def __init__(self, count=60):
        self.particles = [Particle() for _ in range(count)]

    def update(self):
        for p in self.particles:
            p.update()

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)


# ── Timer Ring ────────────────────────────────────────────────────────────────

def draw_timer_ring(surf, cx, cy, radius, frac, color=CYAN, thick=6):
    """Draw a circular countdown arc (frac = 0→1 remaining)."""
    bg_rect = pygame.Rect(cx-radius, cy-radius, radius*2, radius*2)
    pygame.draw.arc(surf, BG_PANEL, bg_rect, 0, math.tau, thick)
    if frac > 0:
        start = math.pi/2
        end   = start + math.tau * frac
        col   = lerp_color(RED, color, frac)
        pygame.draw.arc(surf, col, bg_rect, start, end + math.tau, thick)
        # re-draw from pi/2 going clockwise
        angle  = math.pi/2 - math.tau * frac
        pygame.draw.arc(surf, col, bg_rect, angle, math.pi/2, thick)


# ── Race Track widget ─────────────────────────────────────────────────────────

def draw_race_track(surf, rect, player_progress, ghost_progress,
                    player_name="You", ghost_wpm=0):
    draw_panel(surf, rect, border=PURPLE_DIM)
    f   = font(14)
    pad = 24
    tw  = rect.width - pad*2

    for label, prog, col in [
        (player_name, player_progress, CYAN),
        (f"👻 Ghost ({ghost_wpm:.0f} WPM)", ghost_progress, PURPLE),
    ]:
        y_off = 20 if label == player_name else 55
        bar_y = rect.y + y_off + 18
        # track bg
        trk = pygame.Rect(rect.x+pad, bar_y, tw, 14)
        pygame.draw.rect(surf, BG, trk, border_radius=7)
        # filled
        fw = max(0, int(tw * min(prog, 1.0)))
        if fw:
            fr = pygame.Rect(trk.x, trk.y, fw, trk.height)
            pygame.draw.rect(surf, col, fr, border_radius=7)
        pygame.draw.rect(surf, col, trk, width=1, border_radius=7)
        # car icon
        if fw > 0:
            pygame.draw.circle(surf, col, (trk.x + fw, trk.centery), 8)
        draw_text(surf, label, f, col, rect.x+pad, rect.y+y_off, anchor="topleft")
        draw_text(surf, f"{prog*100:.0f}%", f, col,
                  rect.right-pad, rect.y+y_off, anchor="topright")
