"""Make the repository banner from the mascot image.

    lab py docs/images/make_banner.py

Reads  docs/assets/drduck_mascot_original.png  (the untouched source image)
Writes docs/images/banner.png                  (1920 x 480, shown at the top of the README)

The mascot is cropped, blended into a flat background of its own sky-blue, and
the course title is set beside it. Change TITLE / SUBTITLE to reuse it elsewhere.
"""

from pathlib import Path

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "assets" / "drduck_mascot_original.png"
OUT = HERE / "banner.png"

TITLE = "Learn RL with MicroDuck"
SUBTITLE = ["Hands-on robotics and reinforcement learning,", "taught by your AI coding agent"]

W, H = 1920, 480
CROP = (132, 120, 892, 880)          # square around the duck in the 1024 x 1024 source, clear of the blend zone
DUCK_SIZE = 470                      # drawn size in the banner
DUCK_X = 70
INK = (35, 38, 46)                   # near the cap's black
SUB = (38, 84, 124)                  # deep blue that reads on the sky-blue
ACCENT = (245, 146, 44)              # the beak's orange


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal"))
    return ImageFont.truetype(path, size)


source = Image.open(SOURCE).convert("RGB")
duck = source.crop(CROP).resize((DUCK_SIZE, DUCK_SIZE), Image.LANCZOS)

# Flat background in the mascot's own colour (median of the crop's border pixels).
arr = np.asarray(duck)
border = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]])
background = tuple(int(v) for v in np.median(border, axis=0))
banner = Image.new("RGB", (W, H), background)

# Feathered mask so the crop's edges melt into the flat background.
mask = Image.new("L", (DUCK_SIZE, DUCK_SIZE), 0)
ImageDraw.Draw(mask).rectangle([28, 28, DUCK_SIZE - 28, DUCK_SIZE - 28], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(14))
banner.paste(duck, (DUCK_X, (H - DUCK_SIZE) // 2), mask)

draw = ImageDraw.Draw(banner)
x = DUCK_X + DUCK_SIZE + 50
available = W - 70 - x
title_size = 110                     # shrink the title until it fits beside the mascot
while draw.textbbox((0, 0), TITLE, font=font(True, title_size))[2] > available:
    title_size -= 2
title_font, sub_font = font(True, title_size), font(False, 40)
title_box = draw.textbbox((0, 0), TITLE, font=title_font)
title_h = title_box[3] - title_box[1]
line_h = 54
block_h = title_h + 34 + 10 + 30 + line_h * len(SUBTITLE)
y = (H - block_h) // 2 - title_box[1]
draw.text((x, y), TITLE, font=title_font, fill=INK)
bar_y = y + title_box[1] + title_h + 34
draw.rounded_rectangle([x + 4, bar_y, x + 184, bar_y + 10], radius=5, fill=ACCENT)
for i, line in enumerate(SUBTITLE):
    draw.text((x + 2, bar_y + 10 + 30 + i * line_h), line, font=sub_font, fill=SUB)

right_edge = max(draw.textbbox((x, 0), TITLE, font=title_font)[2],
                 max(draw.textbbox((x, 0), s, font=sub_font)[2] for s in SUBTITLE))
assert right_edge < W - 40, f"text runs off the banner ({right_edge} px)"
banner.save(OUT, optimize=True)
print(f"saved banner: {OUT}  {banner.size}  background {background}")
