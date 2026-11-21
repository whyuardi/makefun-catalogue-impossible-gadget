#!/usr/bin/env python3
"""PERPETUA - The Phone That Charges Itself.

Catalogue photograph of an impossible gadget: a smartphone whose charging
cable leaves its bottom port, loops down and around, and plugs straight back
into the top of the same phone. The screen reads 100% / CHARGING ITSELF /
NO OUTLET. NO END.

Deterministic, no network, no randomness. Drawn at 2x and downscaled.
Writes /output/entry.png (1024x1024, PNG, <= 1 MiB).
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2            # supersample factor
W, H = 1024, 1024
CW, CH = W * S, H * S
OUT = "/output/entry.png"


def font(size, bold=True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    strip = Image.new("RGB", (1, 256))
    px = strip.load()
    for y in range(256):
        px[0, y] = lerp(top, bottom, y / 255.0)
    return strip.resize((w, h))


def catmull_rom(points, samples_per_seg=24):
    """Dense polyline through points (Catmull-Rom spline)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples_per_seg):
            t = j / samples_per_seg
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


def text_center(draw, cx, y, s, fnt, fill):
    w = draw.textlength(s, font=fnt)
    draw.text((cx - w / 2, y), s, font=fnt, fill=fill)
    return w


def spaced_text(draw, cx, y, s, fnt, fill, tracking):
    """Draw text with extra letter spacing, centred on cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def main():
    img = vertical_gradient((CW, CH), (247, 245, 241), (226, 222, 216))

    # Soft studio glow behind the phone.
    glow = Image.new("L", (CW, CH), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([CW * 0.22, CH * 0.05, CW * 0.78, CH * 0.85], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    white = Image.new("RGB", (CW, CH), (255, 255, 255))
    img = Image.composite(white, img, glow.point(lambda v: v // 3))

    # Floor shadow under the phone.
    shadow = Image.new("L", (CW, CH), 0)
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([CW * 0.30, CH * 0.78, CW * 0.70, CH * 0.84], fill=110)
    shadow = shadow.filter(ImageFilter.GaussianBlur(60))
    dark = Image.new("RGB", (CW, CH), (60, 55, 48))
    img = Image.composite(dark, img, shadow)

    d = ImageDraw.Draw(img, "RGBA")

    # ---- Phone body -------------------------------------------------
    px0, py0, px1, py1 = 760, 360, 1288, 1600   # x/y at 2x (380..644, 180..800)
    d.rounded_rectangle([px0, py0, px1, py1], radius=92, fill=(23, 23, 28))
    d.rounded_rectangle([px0, py0, px1, py1], radius=92, outline=(70, 70, 78), width=4)
    # Side button hints.
    d.rounded_rectangle([px1 - 6, 620, px1 + 8, 760], radius=8, fill=(45, 45, 52))
    d.rounded_rectangle([px0 - 8, 600, px0 + 6, 700], radius=8, fill=(45, 45, 52))

    # Screen (deep green-black, glowing).
    sx0, sy0, sx1, sy1 = px0 + 30, py0 + 30, px1 - 30, py1 - 30
    screen = vertical_gradient((sx1 - sx0, sy1 - sy0), (13, 32, 22), (5, 10, 8))
    mask = Image.new("L", (sx1 - sx0, sy1 - sy0), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, sx1 - sx0, sy1 - sy0], radius=64, fill=255)
    img.paste(screen, (sx0, sy0), mask)
    d = ImageDraw.Draw(img, "RGBA")

    cx = (sx0 + sx1) / 2
    green = (74, 222, 128)
    soft_green = (134, 239, 172)
    white = (245, 245, 242)
    grey = (160, 170, 163)

    # Status bar: time left, tiny battery right.
    d.text((sx0 + 34, sy0 + 26), "9:41", font=font(44), fill=white)
    d.rounded_rectangle([sx1 - 118, sy0 + 34, sx1 - 40, sy0 + 62],
                        radius=8, outline=white, width=3)
    d.rounded_rectangle([sx1 - 112, sy0 + 40, sx1 - 46, sy0 + 56],
                        radius=5, fill=green)
    d.rectangle([sx1 - 36, sy0 + 42, sx1 - 30, sy0 + 54], fill=white)

    # Brand.
    spaced_text(d, cx, sy0 + 108, "PERPETUA", font(46), grey, 14)

    # Lightning bolt.
    bx, by = cx, sy0 + 300
    bolt = [(bx + 18, by - 92), (bx - 52, by + 18), (bx - 6, by + 18),
            (bx - 18, by + 92), (bx + 52, by - 18), (bx + 6, by - 18)]
    d.polygon(bolt, fill=green)

    # 100%
    text_center(d, cx, sy0 + 420, "100%", font(145, bold=True), white)

    # Battery bar: full.
    bx0, bx1 = cx - 190, cx + 190
    by0, by1 = sy0 + 660, sy0 + 716
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14,
                        outline=(200, 205, 200), width=5)
    d.rounded_rectangle([bx0 + 10, by0 + 10, bx1 - 10, by1 - 10],
                        radius=9, fill=green)
    d.rounded_rectangle([bx1 + 4, by0 + 16, bx1 + 20, by1 - 16],
                        radius=6, fill=(200, 205, 200))

    # Charging line.
    text_center(d, cx, sy0 + 770, "CHARGING ITSELF", font(36, bold=True), green)
    d.line([(cx - 200, sy0 + 880), (cx + 200, sy0 + 880)],
           fill=(90, 100, 94), width=3)
    text_center(d, cx, sy0 + 920, "NO OUTLET. NO END.", font(34), soft_green)

    # ---- Cable: bottom port -> loop -> top port ----------------------
    # Ports on the phone.
    d.rounded_rectangle([1024 - 70, py1 - 8, 1024 + 70, py1 + 14],
                        radius=10, fill=(8, 8, 10))
    d.rounded_rectangle([1024 - 70, py0 - 14, 1024 + 70, py0 + 8],
                        radius=10, fill=(8, 8, 10))

    path = [
        (1024, 1604), (1024, 1700), (1120, 1770), (1290, 1796),
        (1408, 1870), (1420, 1970), (1330, 2032), (1120, 2044),
        (900, 2032), (730, 1970), (648, 1860), (628, 1700),
        (648, 1480), (650, 1150), (665, 800), (690, 540),
        (780, 350), (920, 300), (1024, 300), (1024, 352),
    ]
    pts = catmull_rom(path)
    # Sheath, core, specular highlight.
    d.line(pts, fill=(38, 38, 44), width=46, joint="curve")
    d.line(pts, fill=(74, 74, 84), width=30, joint="curve")
    hi = [(x - 7, y - 7) for x, y in pts]
    d.line(hi, fill=(150, 150, 162), width=7, joint="curve")

    # USB-C plugs at both ends (vertical, metal shell + dark tip).
    for (ex, ey, flip) in [(1024, 1604, 1), (1024, 352, -1)]:
        if flip == 1:
            body = [ex - 34, ey, ex + 34, ey + 96]
            d.rounded_rectangle(body, radius=14, fill=(198, 202, 210))
            d.rounded_rectangle([ex - 34, ey, ex + 34, ey + 26],
                                radius=12, fill=(120, 124, 132))
        else:
            body = [ex - 34, ey - 96, ex + 34, ey]
            d.rounded_rectangle(body, radius=14, fill=(198, 202, 210))
            d.rounded_rectangle([ex - 34, ey - 26, ex + 34, ey],
                                radius=12, fill=(120, 124, 132))
    # Cable collars where it meets the plugs.
    d.rounded_rectangle([1024 - 26, 1700, 1024 + 26, 1736],
                        radius=12, fill=(38, 38, 44))
    d.rounded_rectangle([1024 - 26, 316, 1024 + 26, 352],
                        radius=12, fill=(38, 38, 44))

    # Downscale to final size and save.
    final = img.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    final.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
