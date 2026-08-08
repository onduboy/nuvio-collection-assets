#!/usr/bin/env python3

"""
Generate all Cine Mamador collection backdrops from AIO Metadata.

The visual rendering is delegated to backdrop_urls.py, which reuses the
original Nuvio Backdrop Generator compositing engine.

Outputs:
    collections/curated/a24/backdrop.webp
    collections/curated/criterion/backdrop.webp
    collections/curated/mubi/backdrop.webp
    collections/curated/neon/backdrop.webp
    collections/curated/arrow/backdrop.webp
    collections/curated/janus/backdrop.webp
    collections/curated/other/backdrop.webp
"""

from pathlib import Path
import sys
import time

import requests

from backdrop_urls import render_from_urls


AIO_BASE = (
    "https://aiom.elondu.com/"
    "stremio/2d8d888b-28c3-48af-862c-c13310959ec6"
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CURATED_DIR = REPO_ROOT / "collections" / "curated"

COLLECTIONS = {
    "a24": {
        "label": "A24",
        "sources": [
            ("movie", "letterboxd.L01gS"),
            ("series", "mdblist.72491"),
        ],
    },
    "criterion": {
        "label": "Criterion",
        "sources": [
            ("movie", "mdblist.75266"),
            ("movie", "letterboxd.inCB4"),
            ("movie", "letterboxd.cyImC"),
        ],
    },
    "mubi": {
        "label": "MUBI",
        "sources": [
            ("movie", "letterboxd.dxCqg"),
            ("movie", "mdblist.16904"),
            ("movie", "letterboxd.GOGNo"),
            ("movie", "letterboxd.pqL8a"),
        ],
    },
    "neon": {
        "label": "NEON",
        "sources": [
            ("movie", "letterboxd.31CQu"),
        ],
    },
    "arrow": {
        "label": "Arrow Video",
        "sources": [
            ("movie", "letterboxd.mE8GI"),
            ("movie", "letterboxd.n4Rgs"),
            ("movie", "letterboxd.rXcm6"),
            ("movie", "letterboxd.pbeFq"),
        ],
    },
    "janus": {
        "label": "Janus Films",
        "sources": [
            ("movie", "letterboxd.cXQTk"),
            ("movie", "letterboxd.dxmAk"),
            ("movie", "letterboxd.dPnYI"),
            ("movie", "letterboxd.jlJoc"),
        ],
    },
    "other": {
        "label": "Los demás",
        "sources": [
            ("movie", "letterboxd.g6zDa"),
            ("movie", "letterboxd.bDlYu"),
        ],
    },
}


def get_catalog(media_type, catalog_id):
    url = f"{AIO_BASE}/catalog/{media_type}/{catalog_id}.json"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json().get("metas", [])


def extract_items(metas):
    items = []

    for meta in metas:
        tmdb_id = meta.get("_tmdbId")
        background = meta.get("background")

        if not tmdb_id or not background:
            continue

        items.append({
            "tmdb_id": str(tmdb_id),
            "background": background,
            "title": meta.get("name", ""),
            "type": meta.get("type", ""),
            "year": meta.get("year", ""),
        })

    return items


def merge_unique(items):
    seen = set()
    result = []

    for item in items:
        if item["tmdb_id"] in seen:
            continue

        seen.add(item["tmdb_id"])
        result.append(item)

    return result


def fetch_collection(collection_id, config):
    print()
    print("=" * 60)
    print(f"{config['label']} [{collection_id}]")
    print("=" * 60)

    all_items = []

    for media_type, catalog_id in config["sources"]:
        print(f"\n  Fetching {media_type}/{catalog_id}")

        try:
            metas = get_catalog(media_type, catalog_id)
            items = extract_items(metas)

            print(
                f"  AIO items: {len(metas)} | "
                f"usable backgrounds: {len(items)}"
            )

            all_items.extend(items)

        except Exception as exc:
            print(f"  ERROR: {exc}")
            print("  Continuing with remaining sources...")

    items = merge_unique(all_items)

    print(f"\n  Unique usable items: {len(items)}")

    return items


def generate_collection(collection_id, config, count=60):
    items = fetch_collection(collection_id, config)

    if not items:
        print(f"\nERROR: {config['label']} has no usable backdrop images.")
        return False

    selected = items[:count]

    output = CURATED_DIR / collection_id / "backdrop.webp"

    print(f"  Selected: {len(selected)}")
    print(f"  Output:   {output}")

    render_from_urls(
        image_urls=[item["background"] for item in selected],
        label=config["label"],
        output=output,
        size="1080p",
        profile="compressed",
        focus="center",
    )

    return True


def main():
    print("=" * 60)
    print("CINE MAMADOR BACKDROP GENERATOR")
    print("=" * 60)
    print(f"Collections: {len(COLLECTIONS)}")
    print(f"Output root: {CURATED_DIR}")

    success = []
    failed = []

    for collection_id, config in COLLECTIONS.items():
        try:
            if generate_collection(collection_id, config):
                success.append(collection_id)
            else:
                failed.append(collection_id)
        except KeyboardInterrupt:
            print("\nInterrupted.")
            sys.exit(130)
        except Exception as exc:
            print(f"\nERROR generating {config['label']}: {exc}")
            failed.append(collection_id)

        time.sleep(0.5)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"\nSuccessful: {len(success)}")
    for collection_id in success:
        print(f"  ✓ {collection_id}")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for collection_id in failed:
            print(f"  ✗ {collection_id}")

        sys.exit(1)

    print("\nAll Cine Mamador backdrops generated successfully.")


if __name__ == "__main__":
    main()
