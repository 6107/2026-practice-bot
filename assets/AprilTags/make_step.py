"""Build a single STEP assembly with all FRC AprilTags as 6.5 x 7.5 in x 0.01 in plates.

Each plate is the 6.5 in tag plus a 1 in white strip below it with "ID <n>" text. Each tag is two
bodies (white, black) that tile the plate, so total depth is 0.01 in.
STEP units are millimetres. Run from the repo root: python assets/AprilTags/make_step.py
"""
from pathlib import Path

import cadquery as cq
from PIL import Image

IN = 25.4
TAG_SIZE = 6.5 * IN
THICKNESS = 0.01 * IN
GRID = 8  # tag36h11 pattern is 8x8 cells (outer ring black)
CELL = TAG_SIZE / GRID
STRIP = 1.0 * IN
TEXT_HEIGHT = 0.5 * IN
LABEL_MARGIN = 0.05 * IN  # gap between label bottom and plate bottom edge
PITCH_Y = 8.0 * IN  # spacing between tag origins along +Y (leftward as seen from the front)
PITCH_Z = 9.0 * IN  # spacing between rows along +Z (rows stack upward)
COLUMNS = 8

HERE = Path(__file__).parent
# FRC-style axes, viewed from the front of the tag: +Z up, +Y right-to-left, +X away from the viewer
# (depth). Each tag's origin is the center of the black tag square (intersection of its diagonals)
# on the back face (x = 0); the tag face is at x = -0.01 in and the 1 in ID strip hangs below.
# The bodies are modelled about that same center with the front face at local z = +0.01 in, so
# only the axes need rotating.
TAG_FRAME = cq.Location(cq.Plane(origin=(0, 0, 0), xDir=(0, -1, 0), normal=(-1, 0, 0)))


def read_cells(png: Path) -> list[list[bool]]:
    """Return GRID x GRID booleans (True = black), dropping the 1-cell white border."""
    img = Image.open(png).convert("L")
    px = img.width // (GRID + 2)
    return [[img.getpixel(((c + 1) * px + px // 2, (r + 1) * px + px // 2)) < 128
             for c in range(GRID)] for r in range(GRID)]


def body(cells: list[list[bool]], black: bool, tag_id: int) -> cq.Workplane:
    pts = [((c + 0.5) * CELL - TAG_SIZE / 2, TAG_SIZE / 2 - (r + 0.5) * CELL)
           for r in range(GRID) for c in range(GRID) if cells[r][c] == black]
    solid = cq.Workplane("XY").pushPoints(pts).rect(CELL, CELL).extrude(THICKNESS)
    strip_center = (0, -TAG_SIZE / 2 - STRIP / 2)
    text_pos = (0, -TAG_SIZE / 2 - STRIP + LABEL_MARGIN)  # label sits at the plate's bottom edge
    text = (cq.Workplane("XY").center(*text_pos)
            .text(f"ID {tag_id}", TEXT_HEIGHT, THICKNESS, halign="center", valign="bottom"))
    if black:
        solid = solid.union(text)
    else:
        strip = cq.Workplane("XY").center(*strip_center).rect(TAG_SIZE, STRIP).extrude(THICKNESS)
        solid = solid.union(strip.cut(text))
    return solid.clean()


def main() -> None:
    root = cq.Assembly(name="FRC_2026_AprilTags")
    pngs = sorted(HERE.glob("tag36h11_*.png"))
    for n, png in enumerate(pngs):
        tag_id = int(png.stem.split("_")[1])
        cells = read_cells(png)
        tag = cq.Assembly(name=f"AprilTag_{tag_id:02d}")
        tag.add(body(cells, False, tag_id), name=f"Tag{tag_id:02d}_White", color=cq.Color(1, 1, 1), loc=TAG_FRAME)
        tag.add(body(cells, True, tag_id), name=f"Tag{tag_id:02d}_Black", color=cq.Color(0, 0, 0), loc=TAG_FRAME)
        loc = cq.Location(cq.Vector(0, (n % COLUMNS) * PITCH_Y, (n // COLUMNS) * PITCH_Z))
        root.add(tag, name=f"AprilTag_{tag_id:02d}", loc=loc)
    out = HERE / "FRC_2026_AprilTags.step"
    root.export(str(out))
    print(f"wrote {out} ({len(pngs)} tags)")


if __name__ == "__main__":
    main()
