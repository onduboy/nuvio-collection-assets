#!/usr/bin/env python3
"""
Render a Nuvio backdrop directly from image URLs.

This adapter reuses the visual/compositing functions from backdrop.py,
but skips TMDB catalog discovery and Fanart lookups. It is intended for
catalogs such as A24 where AIO Metadata already provides the backdrop URL.
"""

import argparse
from pathlib import Path
import sys

import requests
from PIL import Image

import backdrop


def render_from_urls(
    image_urls,
    label,
    output,
    size="1080p",
    profile="compressed",
    quality=None,
    focus="center",
    accent_color=None,
):
    if not image_urls:
        raise ValueError("No image URLs were supplied.")

    output = Path(output)

    focus_x, focus_y = backdrop.parse_focus_value(focus)
    accent = accent_color or backdrop.default_accent_for_label(label)
    quality_settings = backdrop.resolve_quality_settings(
        profile=profile,
        quality=quality,
    )

    if size not in backdrop.SIZE_PRESETS:
        raise ValueError("size must be '1080p' or '4k'.")

    width, height, scale = backdrop.SIZE_PRESETS[size]

    print(f"\n{'-' * 50}")
    print(f"  Label   : {label}")
    print(f"  Images  : direct URLs")
    print(f"  Count   : {len(image_urls)}")
    print(f"  Focus   : x={focus_x:.2f}, y={focus_y:.2f}")
    print(f"  Size    : {size} ({width}x{height})")
    print(f"  Profile : {profile} (q={quality_settings['quality']})")
    print(f"{'-' * 50}\n")

    tile_images = []

    for index, url in enumerate(image_urls, start=1):
        print(f"  [{index:02d}/{len(image_urls)}] downloading...")
        image = backdrop.download_image_url(url)

        if image is not None:
            tile_images.append(image)

    print(f"\nDownloaded {len(tile_images)} of {len(image_urls)} images.")

    if not tile_images:
        raise RuntimeError("None of the backdrop URLs could be downloaded.")

    tile_images = backdrop.ensure_minimum_tiles(tile_images, 12)

    print(f"Compositing {size} ({width}x{height})...")

    canvas = backdrop.build_tilted_grid(
        tile_images,
        width,
        height,
        scale=scale,
        focus_x=focus_x,
        focus_y=focus_y,
    )

    canvas = backdrop.apply_gradient(canvas, accent)

    output.parent.mkdir(parents=True, exist_ok=True)

    # Save directly as WEBP. The original save_output() first writes a JPG,
    # which is useful for its original workflow but unnecessary here.
    final = canvas.convert("RGB")
    final.save(
        output,
        "WEBP",
        quality=quality_settings["quality"],
        method=6,
    )

    size_mb = output.stat().st_size / 1_048_576

    print(
        f"  Saved {output} "
        f"({final.size[0]}x{final.size[1]}, {size_mb:.1f} MB, "
        f"q={quality_settings['quality']})"
    )

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Nuvio backdrop from direct image URLs."
    )

    parser.add_argument("--label", required=True)
    parser.add_argument("--background-url", action="append", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--size",
        choices=("1080p", "4k"),
        default="1080p",
    )
    parser.add_argument(
        "--profile",
        choices=tuple(backdrop.QUALITY_PRESETS),
        default="compressed",
    )
    parser.add_argument("--quality", type=int, default=None)
    parser.add_argument(
        "--focus",
        default="center",
        help="Preset or x,y fractions.",
    )
    parser.add_argument("--accent-color", default=None)

    args = parser.parse_args()

    if args.quality is not None and not 1 <= args.quality <= 95:
        parser.error("--quality must be between 1 and 95.")

    accent = (
        backdrop.parse_accent_color(args.accent_color)
        if args.accent_color
        else None
    )

    render_from_urls(
        image_urls=args.background_url,
        label=args.label,
        output=args.output,
        size=args.size,
        profile=args.profile,
        quality=args.quality,
        focus=args.focus,
        accent_color=accent,
    )


if __name__ == "__main__":
    main()
