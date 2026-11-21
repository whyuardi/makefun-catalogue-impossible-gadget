# PERPETUA — The Phone That Charges Itself

[![make.fun](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)
[![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/whyuardi/makefun-catalogue-impossible-gadget/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)
[![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/whyuardi/makefun-catalogue-impossible-gadget/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)

A clean catalogue photograph of an impossible gadget: the PERPETUA phone.
Its only accessory is its own charging cable — it leaves the USB-C port at
the bottom, sweeps down into one smooth loop, and plugs straight back into
the top of the same phone. No outlet, no wall, no end: the phone charges
itself, forever, at 100%.

The screen says it plainly: PERPETUA, a green lightning bolt, a big 100%
over a full green battery bar, CHARGING ITSELF, and underneath — NO OUTLET.
NO END.

Entry for [The Catalogue Photo of an Impossible Gadget](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341) on make.fun.

## Run

```sh
python3 main.py   # writes /output/entry.png (1024x1024, < 1 MiB)
```

The image is drawn entirely in code with Pillow: a light studio gradient
with a soft floor shadow, a titanium-framed phone with a dark screen, and
the looping cable drawn as a smooth spline. Deterministic, no network, no
randomness — the same command always produces the same picture.
