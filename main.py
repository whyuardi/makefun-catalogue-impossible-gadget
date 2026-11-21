"""PERPETUA: The Phone That Charges Itself.

Catalogue photograph, drawn entirely in code with Pillow.
Deterministic, no network, no randomness. Writes /output/entry.png
(1024x1024, under 1 MiB). Drawn at 2x and downscaled for smooth edges.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S
OUT = "/output/entry.png"

BG_TOP = (246, 243, 236)
BG_BOT = (228, 224, 213)
FRAME = (38, 40, 48)
FRAME_EDGE = (88, 90, 100)
SCREEN_TOP = (16, 28, 26)
SCREEN_BOT = (6, 14, 12)
GREEN = (46, 214, 130)
GREEN_DIM = (120, 220, 170)
WHITE = (245, 247, 244)
GREY = (150, 152, 148)
CABLE = (52, 54, 62)
CABLE_HI = (150, 152, 165)
PLUG = (196, 198, 202)
PLUG_DK = (120, 122, 128)


def font(name, size):
    for base in ("/usr/share/fonts/truetype/dejavu/",
                 "/usr/share/fonts/TTF/"):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_BRAND = font("DejaVuSans-Bold.ttf", 58)
F_BIG = font("DejaVuSans-Bold.ttf", 148)
F_MED = font("DejaVuSans-Bold.ttf", 48)
F_SMALL = font("DejaVuSans-Bold.ttf", 44)
F_TIME = font("DejaVuSans-Bold.ttf", 44)


def catmull_rom(points, samples=24):
    """Smooth curve through points (Catmull-Rom spline)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def spaced(draw, cx, y, text, fnt, fill, tracking=14):
    """Draw text with letter tracking, centred on cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def main():
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)

    # --- studio background: soft vertical gradient + vignette glow ---
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.18, H * 0.02, W * 0.82, H * 0.62], fill=26)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.composite(Image.new("RGB", (W, H), (255, 255, 250)), img, glow)
    d = ImageDraw.Draw(img)

    # --- floor: soft shadow under the phone ---
    shadow = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([W * 0.28, H * 0.845, W * 0.72, H * 0.885], fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    img.paste(Image.new("RGB", (W, H), (70, 66, 58)), (0, 0), shadow)
    d = ImageDraw.Draw(img)

    cx = W // 2
    # Phone geometry (2x coords)
    px0, px1 = 724, 1324          # phone left / right
    py0, py1 = 300, 1740          # phone top / bottom
    r = 78

    # --- cable: bottom port -> down -> wide loop -> up the left side -> top ---
    cable_pts = [
        (cx, py1 - 6),
        (cx + 6, 1900),
        (cx - 60, 1990),
        (cx - 320, 2010),
        (cx - 470, 1930),
        (cx - 500, 1720),
        (cx - 495, 1300),
        (cx - 490, 900),
        (cx - 470, 560),
        (cx - 360, 360),
        (cx - 150, 300),
        (cx, py0 + 6),
    ]
    curve = catmull_rom(cable_pts)
    d.line(curve, fill=CABLE, width=34, joint="curve")
    # thin highlight along the cable centre
    hi = [(x + 5, y - 5) for (x, y) in curve]
    d.line(hi, fill=CABLE_HI, width=7, joint="curve")

    # --- phone body ---
    d.rounded_rectangle([px0, py0, px1, py1], radius=r, fill=FRAME)
    d.rounded_rectangle([px0, py0, px1, py1], radius=r,
                        outline=FRAME_EDGE, width=4)
    # side buttons
    d.rounded_rectangle([px0 - 8, 640, px0 + 2, 760], radius=5, fill=FRAME_EDGE)
    d.rounded_rectangle([px1 - 2, 700, px1 + 8, 830], radius=5, fill=FRAME_EDGE)
    # screen
    sx0, sy0, sx1, sy1 = px0 + 26, py0 + 26, px1 - 26, py1 - 26
    scr = Image.new("RGB", (sx1 - sx0, sy1 - sy0), SCREEN_TOP)
    sd2 = ImageDraw.Draw(scr)
    for y in range(sy1 - sy0):
        t = y / max(1, (sy1 - sy0 - 1))
        c = tuple(int(SCREEN_TOP[i] + (SCREEN_BOT[i] - SCREEN_TOP[i]) * t)
                  for i in range(3))
        sd2.line([(0, y), (sx1 - sx0, y)], fill=c)
    img.paste(scr, (sx0, sy0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=r - 22,
                        outline=(70, 74, 82), width=3)

    scx = (sx0 + sx1) / 2
    inner_l, inner_r = sx0 + 34, sx1 - 34   # hard text margins

    # status row: time left, tiny full battery right
    d.text((sx0 + 36, sy0 + 30), "9:41", font=F_TIME, fill=WHITE)
    bx0, by0, bx1, by1 = sx1 - 108, sy0 + 38, sx1 - 40, sy0 + 66
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=7,
                        outline=WHITE, width=3)
    d.rounded_rectangle([bx0 + 5, by0 + 5, bx1 - 5, by1 - 5], radius=4,
                        fill=GREEN)
    d.rectangle([bx1 + 3, by0 + 9, bx1 + 9, by1 - 9], fill=WHITE)

    # brand
    y = sy0 + 118
    spaced(d, scx, y, "PERPETUA", F_BRAND, GREY, tracking=16)

    # green lightning bolt
    bolt = [(scx + 18, y + 190), (scx - 62, y + 330), (scx - 6, y + 330),
            (scx - 26, y + 440), (scx + 74, y + 292), (scx + 14, y + 292)]
    d.polygon(bolt, fill=GREEN)

    # big 100%
    y_big = y + 470
    centered(d, scx, y_big, "100%", F_BIG, WHITE)

    # full battery bar
    bar_y = y_big + 250
    bar_x0, bar_x1 = sx0 + 96, sx1 - 96
    d.rounded_rectangle([bar_x0, bar_y, bar_x1, bar_y + 56], radius=16,
                        outline=WHITE, width=4)
    d.rounded_rectangle([bar_x0 + 8, bar_y + 8, bar_x1 - 8, bar_y + 48],
                        radius=11, fill=GREEN)
    d.rectangle([bar_x1 + 5, bar_y + 16, bar_x1 + 15, bar_y + 40], fill=WHITE)

    # CHARGING ITSELF
    y2 = bar_y + 96
    centered(d, scx, y2, "CHARGING ITSELF", F_MED, GREEN)

    # divider
    div_y = y2 + 104
    d.line([(sx0 + 70, div_y), (sx1 - 70, div_y)], fill=(110, 116, 110),
           width=3)

    # NO OUTLET. NO END.
    centered(d, scx, div_y + 34, "NO OUTLET. NO END.", F_SMALL, GREEN_DIM)

    # --- plugs: bottom (USB-C) and top, drawn over phone + cable ends ---
    # bottom plug
    d.rounded_rectangle([cx - 52, py1 - 14, cx + 52, py1 + 66], radius=12,
                        fill=PLUG)
    d.rounded_rectangle([cx - 52, py1 - 14, cx + 52, py1 + 66], radius=12,
                        outline=PLUG_DK, width=3)
    d.rounded_rectangle([cx - 30, py1 + 66, cx + 30, py1 + 92], radius=8,
                        fill=(30, 31, 36))
    # top plug
    d.rounded_rectangle([cx - 52, py0 - 66, cx + 52, py0 + 14], radius=12,
                        fill=PLUG)
    d.rounded_rectangle([cx - 52, py0 - 66, cx + 52, py0 + 14], radius=12,
                        outline=PLUG_DK, width=3)
    d.rounded_rectangle([cx - 30, py0 - 92, cx + 30, py0 - 66], radius=8,
                        fill=(30, 31, 36))

    # --- downscale to 1024 and save ---
    img = img.resize((1024, 1024), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
