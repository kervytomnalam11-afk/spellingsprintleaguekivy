"""
make_icon.py
Run once to generate icon.png and presplash.png for the APK.
Called automatically by the GitHub Actions workflow.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

def make_icon(size=512):
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded background
    def rr(d, xy, r, fill):
        d.rounded_rectangle(xy, radius=r, fill=fill)

    rr(draw, [0, 0, size-1, size-1], size//8, (8, 8, 26, 255))

    # Race track strip
    track_y = int(size * 0.60)
    track_h = int(size * 0.22)
    rr(draw, [int(size*0.06), track_y, int(size*0.94), track_y+track_h],
       8, (16, 16, 40, 255))

    # Road dashes
    dash_y = track_y + track_h // 2 - 3
    x = int(size * 0.10)
    while x < int(size * 0.88):
        draw.rectangle([x, dash_y, x+int(size*0.04), dash_y+5], fill=(30, 30, 70, 255))
        x += int(size * 0.065)

    # Progress fill (cyan tint under car)
    prog_w = int((size * 0.88 - size * 0.06) * 0.65)
    fill_s = Image.new("RGBA", (prog_w, track_h), (0, 210, 255, 20))
    img.paste(fill_s, (int(size*0.06), track_y), fill_s)

    # Cyan car
    cx = int(size * 0.58)
    cy = track_y + track_h // 2 - int(size * 0.055)
    cw = int(size * 0.13)
    ch = int(size * 0.075)
    rr(draw, [cx, cy + ch//3, cx+cw, cy + ch], 4, (0, 210, 255, 255))       # body
    rr(draw, [cx+int(cw*0.15), cy, cx+int(cw*0.75), cy+int(ch*0.65)], 3,
       (0, 140, 200, 255))                                                      # roof
    # headlight
    draw.rectangle([cx+cw-int(cw*0.1), cy+int(ch*0.45),
                    cx+cw, cy+int(ch*0.65)], fill=(255, 230, 80, 255))
    # wheels
    wr = int(size * 0.025)
    for wx in [cx+int(cw*0.22), cx+int(cw*0.75)]:
        draw.ellipse([wx-wr, cy+ch-wr, wx+wr, cy+ch+wr], fill=(20, 20, 50, 255))

    # Ghost car (purple, behind)
    gx = int(size * 0.22)
    gy = cy + int(ch * 0.1)
    gw = int(cw * 0.85)
    gh = int(ch * 0.85)
    ghost_body = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost_body)
    gd.rounded_rectangle([0, gh//3, gw, gh], radius=4, fill=(170, 60, 255, 140))
    gd.rounded_rectangle([int(gw*0.15), 0, int(gw*0.75), int(gh*0.65)], radius=3,
                          fill=(110, 30, 200, 120))
    img.paste(ghost_body, (gx, gy), ghost_body)

    # Finish flag
    fx = int(size * 0.88)
    tile = track_h // 8
    for row in range(8):
        for col in range(2):
            c = (255,255,255,255) if (row+col)%2==0 else (8,8,26,255)
            draw.rectangle([fx+col*tile, track_y+row*tile,
                             fx+(col+1)*tile-1, track_y+(row+1)*tile-1], fill=c)

    # Title letters "SSL"
    s2 = size // 2
    colors = [(0,210,255), (170,60,255), (255,140,0)]
    letters = "SSL"
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                  int(size * 0.22))
    except Exception:
        fnt = ImageFont.load_default()

    total_w = sum(draw.textlength(l, font=fnt) for l in letters)
    x = s2 - total_w // 2
    for letter, col in zip(letters, colors):
        draw.text((x, int(size*0.10)), letter, font=fnt, fill=(*col, 255))
        x += int(draw.textlength(letter, font=fnt))

    # "SPELLING SPRINT" subtitle
    try:
        fnt2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                   int(size * 0.055))
    except Exception:
        fnt2 = ImageFont.load_default()

    sub1 = "SPELLING"
    sub2 = "SPRINT LEAGUE"
    w1 = draw.textlength(sub1, font=fnt2)
    w2 = draw.textlength(sub2, font=fnt2)
    draw.text((s2 - w1//2, int(size*0.35)), sub1, font=fnt2, fill=(0,210,255,220))
    draw.text((s2 - w2//2, int(size*0.42)), sub2, font=fnt2, fill=(170,60,255,220))

    # League dots
    dot_colors = [(180,100,40), (180,180,200), (255,200,0), (100,220,220), (120,160,255)]
    dot_y_c = int(size * 0.56)
    dot_r   = int(size * 0.018)
    dot_gap = int(size * 0.048)
    total_dot_w = len(dot_colors) * dot_gap
    for i, dc in enumerate(dot_colors):
        dx = s2 - total_dot_w//2 + i * dot_gap
        draw.ellipse([dx-dot_r, dot_y_c-dot_r, dx+dot_r, dot_y_c+dot_r],
                     fill=(*dc, 255))

    return img


def make_presplash(w=1280, h=720):
    img  = Image.new("RGB", (w, h), (8, 8, 26))
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        fnt2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except Exception:
        fnt = fnt2 = ImageFont.load_default()

    t1 = "SPELLING SPRINT"
    t2 = "L E A G U E"
    w1 = draw.textlength(t1, font=fnt)
    w2 = draw.textlength(t2, font=fnt2)
    draw.text((w//2 - w1//2, h//2 - 80), t1, font=fnt, fill=(0, 210, 255))
    draw.text((w//2 - w2//2, h//2 + 10), t2, font=fnt2, fill=(210, 210, 240))
    return img


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    icon = make_icon(512)
    icon.save(os.path.join(out_dir, "icon.png"))
    print("icon.png written")
    splash = make_presplash()
    splash.save(os.path.join(out_dir, "presplash.png"))
    print("presplash.png written")
