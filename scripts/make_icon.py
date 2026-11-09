"""Render the app icon (a usage gauge) to claude_meter/resources/AppIcon.icns.

    uv run python scripts/make_icon.py

Only needs PyObjC (already a dependency via rumps) plus the system `sips` and
`iconutil` tools. The result is checked in; re-run this after changing the drawing.
"""

import math
import subprocess
import sys
import tempfile
from pathlib import Path

from AppKit import (
    NSBezierPath,
    NSBitmapImageRep,
    NSCalibratedRGBColorSpace,
    NSColor,
    NSGradient,
    NSGraphicsContext,
    NSLineCapStyleRound,
    NSMakePoint,
    NSMakeRect,
    NSPNGFileType,
)

OUT = Path(__file__).resolve().parent.parent / "claude_meter" / "resources" / "AppIcon.icns"
CANVAS = 1024
# Apple's icon grid: the rounded square fills 824pt of a 1024pt canvas.
TILE = 824
TILE_RADIUS = 185
GAUGE_SWEEP = 270
GAUGE_FILL = 0.65
ICONSET_SIZES = (16, 32, 128, 256, 512)


def _rgb(hex_color: str, alpha: float = 1.0) -> NSColor:
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, alpha)


def _arc(center, radius: float, start: float, end: float, width: float) -> NSBezierPath:
    path = NSBezierPath.bezierPath()
    path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        center, radius, start, end, True
    )
    path.setLineWidth_(width)
    path.setLineCapStyle_(NSLineCapStyleRound)
    return path


def draw(size: int) -> NSBitmapImageRep:
    rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, size, size, 8, 4, True, False, NSCalibratedRGBColorSpace, 0, 0
    )
    ctx = NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.setCurrentContext_(ctx)
    scale = size / CANVAS

    inset = (CANVAS - TILE) / 2 * scale
    tile = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        NSMakeRect(inset, inset, TILE * scale, TILE * scale), TILE_RADIUS * scale, TILE_RADIUS * scale
    )
    NSGradient.alloc().initWithStartingColor_endingColor_(_rgb("#2A3240"), _rgb("#171C26")).drawInBezierPath_angle_(
        tile, -90
    )

    center = NSMakePoint(CANVAS / 2 * scale, 470 * scale)
    radius = 290 * scale
    width = 82 * scale
    start = 225.0
    # The gauge opens downwards: 225° round to -45° is a 270° sweep.
    _rgb("#FFFFFF", 0.16).setStroke()
    _arc(center, radius, start, start - GAUGE_SWEEP, width).stroke()
    _rgb("#D97757").setStroke()
    _arc(center, radius, start, start - GAUGE_SWEEP * GAUGE_FILL, width).stroke()

    # Needle pointing at the current fill level, with a hub.
    angle = math.radians(start - GAUGE_SWEEP * GAUGE_FILL)
    needle = NSBezierPath.bezierPath()
    needle.moveToPoint_(center)
    needle.lineToPoint_(
        NSMakePoint(center.x + math.cos(angle) * 215 * scale, center.y + math.sin(angle) * 215 * scale)
    )
    needle.setLineWidth_(40 * scale)
    needle.setLineCapStyle_(NSLineCapStyleRound)
    _rgb("#F4F1EA").setStroke()
    needle.stroke()
    hub = 58 * scale
    _rgb("#F4F1EA").setFill()
    NSBezierPath.bezierPathWithOvalInRect_(NSMakeRect(center.x - hub, center.y - hub, hub * 2, hub * 2)).fill()
    _rgb("#171C26").setFill()
    hub = 24 * scale
    NSBezierPath.bezierPathWithOvalInRect_(NSMakeRect(center.x - hub, center.y - hub, hub * 2, hub * 2)).fill()

    NSGraphicsContext.restoreGraphicsState()
    return rep


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "AppIcon.iconset"
        iconset.mkdir()
        for base in ICONSET_SIZES:
            for scale, suffix in ((1, ""), (2, "@2x")):
                png = draw(base * scale).representationUsingType_properties_(NSPNGFileType, None)
                png.writeToFile_atomically_(str(iconset / f"icon_{base}x{base}{suffix}.png"), True)
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(OUT)], check=True)
    print(f"wrote {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
