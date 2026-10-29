"""Download FRC AprilTag (tag36h11, IDs 1-32) and render PNGs with a 1 inch ID strip below the tag.

Scale: the 8x8 tag pattern is 6.5 in wide, so 64 px = 1 in (cell = 52 px). A 1-cell white
border surrounds the tag; the 1 in strip (white, with centered "ID <n>") sits under the pattern.
Run from the repo root: python assets/AprilTags/make_pngs.py
"""
import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CELL = 52
PX_PER_IN = 64
GRID = 8
STRIP = PX_PER_IN
LABEL_MARGIN = round(0.05 * PX_PER_IN)  # gap between label baseline and plate bottom edge
HERE = Path(__file__).parent


def main() -> None:
    font = ImageFont.truetype("arial.ttf", int(PX_PER_IN * 0.5))
    for i in range(1, 33):
        url = f"https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_{i:05d}.png"
        src = Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("L")
        tag = src.resize((src.width * CELL, src.height * CELL), Image.NEAREST)  # includes border
        w, h = tag.size
        img = Image.new("L", (w, h + STRIP), 255)
        img.paste(tag, (0, 0))
        # strip occupies the 1 in directly under the pattern, i.e. just above the bottom border
        top = h - CELL
        img.paste(255, (0, top, w, h + STRIP))
        ImageDraw.Draw(img).text((w / 2, top + STRIP - LABEL_MARGIN), f"ID {i}", fill=0, font=font, anchor="ms")
        img.save(HERE / f"tag36h11_{i:02d}.png")
    print("done")


if __name__ == "__main__":
    main()
