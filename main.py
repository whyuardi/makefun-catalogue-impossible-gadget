#!/usr/bin/env python3
"""Catalogue photograph of an impossible gadget: the PERPETUA phone.

A smartphone that charges itself, forever. Its own cable leaves the
bottom port, loops around, and plugs back into the top of the same phone;
the screen reads 100% and CHARGING ITSELF. One product, one accessory
(the cable), clean studio background, soft shadow. Drawn entirely in code,
deterministic, no network.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, top, bottom):
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        d.line([(0, y), (size[0], y)], fill=lerp(top, bottom, y / max(1, size[1] - 1)))
    return img


def rounded_rect(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def bezier(points, n=120):
    """Cubic bezier through 4 control points, sampled."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * x0 + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
        y = mt**3 * y0 + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
        out.append((x, y))
    return out


def draw_tracked_text(draw, cx, y, text, fnt, fill, spacing=4):
    """Centered text with letter spacing."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing


def main():
    # ---- studio background ----
    img = vgrad((W, H), (247, 245, 242), (228, 224, 218))
    # soft radial glow behind the product
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([212, 40, 812, 900], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    warm = Image.new("RGB", (W, H), (255, 252, 246))
    img = Image.composite(warm, img, glow)

    # floor line + soft floor shadow
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(90, 872), (934, 872)], fill=(190, 184, 176, 160), width=2)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([330, 838, 694, 896], fill=(60, 55, 48, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- cable (behind phone, drawn first so phone overlaps its ends) ----
    # path: bottom port -> down -> loop right -> up -> top plug
    cable_path = (
        bezier([(512, 806), (512, 900), (640, 926), (742, 872)], 60)
        + bezier([(742, 872), (828, 824), (836, 640), (800, 470)], 60)
        + bezier([(800, 470), (770, 330), (700, 190), (606, 122)], 60)
    )
    # drop shadow of the cable
    d.line([(x + 5, y + 6) for x, y in cable_path], fill=(120, 114, 106, 90), width=18, joint="curve")
    d.line(cable_path, fill=(226, 224, 220, 255), width=17, joint="curve")
    d.line(cable_path, fill=(176, 172, 166, 255), width=17, joint="curve")
    # re-draw core white with a thin highlight offset
    d.line(cable_path, fill=(250, 249, 247, 255), width=12, joint="curve")
    d.line([(x - 2, y - 3) for x, y in cable_path], fill=(255, 255, 255, 255), width=4, joint="curve")

    # ---- phone body ----
    body = (352, 118, 672, 802)
    # outer edge highlight (titanium rim)
    rounded_rect(d, (348, 114, 676, 806), 50, fill=(88, 90, 96, 255))
    rounded_rect(d, body, 46, fill=(38, 40, 45, 255))
    # side button hints
    rounded_rect(d, (672, 300, 678, 380), 3, fill=(120, 122, 128, 255))
    rounded_rect(d, (672, 410, 678, 470), 3, fill=(120, 122, 128, 255))

    # screen
    screen = (368, 134, 656, 786)
    scr = Image.new("RGB", (screen[2] - screen[0], screen[3] - screen[1]))
    sd2 = ImageDraw.Draw(scr)
    for y in range(scr.height):
        sd2.line([(0, y), (scr.width, y)], fill=lerp((10, 16, 28), (30, 48, 78), y / scr.height))
    scr_mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], radius=34, fill=255)
    img.paste(scr, (screen[0], screen[1]), scr_mask)
    d = ImageDraw.Draw(img, "RGBA")

    # subtle screen sheen (diagonal light)
    sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sheen)
    shd.polygon([(368, 786), (560, 134), (640, 134), (448, 786)], fill=(255, 255, 255, 14))
    img = Image.alpha_composite(img, sheen)
    d = ImageDraw.Draw(img, "RGBA")

    cx = 512
    # brand
    draw_tracked_text(d, cx, 168, "PERPETUA", font(FONT_BOLD, 26), (168, 178, 196, 255), spacing=8)
    # battery ring (full = 100%)
    ring_c = (cx, 420)
    r = 108
    d.arc([ring_c[0] - r, ring_c[1] - r, ring_c[0] + r, ring_c[1] + r],
          start=-90, end=270, fill=(52, 199, 89, 255), width=15)
    # lightning bolt inside the ring, above the percent
    bolt = [(cx + 8, 340), (cx - 22, 402), (cx - 2, 402), (cx - 10, 452),
            (cx + 24, 386), (cx + 2, 386)]
    d.polygon(bolt, fill=(52, 199, 89, 255))
    # 100%
    f_big = font(FONT_BOLD, 66)
    tw = d.textlength("100%", font=f_big)
    d.text((cx - tw / 2, 448), "100%", font=f_big, fill=(245, 247, 250, 255))
    # charging itself (auto-fit inside the screen)
    _size = 27
    while _size > 14:
        _f = font(FONT_BOLD, _size)
        _w = sum(d.textlength(ch, font=_f) for ch in "CHARGING ITSELF") + 4 * 14
        if _w <= 258:
            break
        _size -= 1
    draw_tracked_text(d, cx, 552, "CHARGING ITSELF", font(FONT_BOLD, _size), (120, 220, 150, 255), spacing=4)
    # infinity line
    f_inf = font(FONT_BOLD, 40)
    tw = d.textlength("\u221e", font=f_inf)
    d.text((cx - tw / 2, 606), "\u221e", font=f_inf, fill=(168, 178, 196, 255))
    draw_tracked_text(d, cx, 668, "NO OUTLET. NO END.", font(FONT_REG, 20), (140, 150, 168, 255), spacing=3)

    # ---- cable plugs ----
    # bottom plug (into the phone's bottom port)
    rounded_rect(d, (494, 796, 530, 830), 6, fill=(238, 236, 232, 255))
    d.rectangle([500, 800, 524, 806], fill=(150, 148, 142, 255))
    # top plug (into the top edge)
    rounded_rect(d, (588, 92, 624, 122), 6, fill=(238, 236, 232, 255))
    d.rectangle([594, 116, 618, 122], fill=(150, 148, 142, 255))
    # green LED glow at both plugs: charging
    for px, py in ((512, 836), (606, 88)):
        halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(52, 199, 89, 90))
        halo = halo.filter(ImageFilter.GaussianBlur(8))
        img = Image.alpha_composite(img, halo)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(52, 199, 89, 255))

    # ---- gentle floor reflection of the phone ----
    refl = img.crop((352, 118, 672, 802)).transpose(Image.FLIP_TOP_BOTTOM).resize((320, 120))
    refl = refl.convert("RGBA")
    alpha = Image.new("L", refl.size, 0)
    ad = ImageDraw.Draw(alpha)
    for y in range(refl.height):
        ad.line([(0, y), (refl.width, y)], fill=int(30 * (1 - y / refl.height)))
    refl.putalpha(alpha)
    refl = refl.filter(ImageFilter.GaussianBlur(3))
    img.paste(refl, (352, 876), refl)

    os.makedirs("/output", exist_ok=True)
    img.convert("RGB").save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
