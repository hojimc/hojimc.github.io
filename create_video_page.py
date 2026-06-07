#!/usr/bin/env python3
"""
create_video_page.py — Generate a video page for hojimc.github.io.

AUTO MODE — title fetched from YouTube, filename derived from title:
    python create_video_page.py <parent_dir/> <youtube_id> [options]

    Examples:
        python create_video_page.py videos/travel/ p6-uRjfggyk
        python create_video_page.py videos/drone/ abc123XYZ --location "Sarasota, Florida · 2022"

EXPLICIT MODE — full control:
    python create_video_page.py <output.html> <title> [youtube_id] [options]

    Examples:
        python create_video_page.py videos/travel/fraser-island.html "Fraser Island" \\
            p6-uRjfggyk --location "Australia · 1995"
        python create_video_page.py videos/travel/new-video.html "New Video"   # no YouTube ID yet

Options:
    --location      "Place · Year" shown under the title (prompted interactively if omitted)
    --description   Optional paragraph under the title
    --back-label    Breadcrumb label (auto-inferred from path if omitted)
    --back-url      Breadcrumb URL   (auto-inferred from path if omitted)
    --no-parent     Skip updating the parent collection page

After creation the script:
  1. Prompts for missing --location interactively
  2. Injects a card into the parent collection (creating it if needed)
  3. Registers new collection pages in js/breadcrumb.js automatically

TODO: once the site and scripts are finalized, add create_delete_page.py to
      remove a page and its card from the parent collection automatically.
"""

import sys
import os
import json
import argparse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from _page_builder import (
    slug_from_title, infer_breadcrumb, sha256_hex,
    build_video_page, make_video_card, ensure_parent, write_page,
    prompt_required, prompt_optional, propagate_counts_up,
)


def fetch_youtube_title(youtube_id: str) -> str | None:
    """Fetch video title via YouTube oEmbed API (no API key required)."""
    try:
        url = (
            f"https://www.youtube.com/oembed"
            f"?url=https://www.youtube.com/watch?v={youtube_id}&format=json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("title")
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate a video page for hojimc.github.io.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("output_path", help=(
        "AUTO: parent directory (e.g. videos/travel/)  |  "
        "EXPLICIT: full .html path (e.g. videos/travel/fraser-island.html)"
    ))
    parser.add_argument("rest", nargs="*", help=(
        "AUTO: [youtube_id]  |  EXPLICIT: <title> [youtube_id]"
    ))
    parser.add_argument("--location",    default=None,
                        help='"Place · Year" shown under the title')
    parser.add_argument("--description", default=None,
                        help="Optional paragraph under the title")
    parser.add_argument("--back-label",  default=None, dest="back_label")
    parser.add_argument("--back-url",    default=None, dest="back_url")
    parser.add_argument("--no-parent",   action="store_true", dest="no_parent",
                        help="Skip updating the parent collection page")
    parser.add_argument("--password",    default=None,
                        help="Password to protect the page (e.g. Claude)")
    args = parser.parse_args()

    out_norm  = args.output_path.replace("\\", "/")
    auto_mode = not out_norm.endswith(".html")
    rest      = args.rest

    if auto_mode:
        youtube_id  = rest[0] if rest else None
        title       = None
        output_path = None
    else:
        title       = rest[0] if rest else None
        youtube_id  = rest[1] if len(rest) > 1 else None
        output_path = out_norm

    # ── Resolve title ────────────────────────────────────────────────────────
    if not title:
        if youtube_id:
            print(f"→ Fetching title from YouTube ({youtube_id})...", file=sys.stderr)
            title = fetch_youtube_title(youtube_id)
            if title:
                print(f"  Title: {title!r}", file=sys.stderr)
            else:
                print("  Could not fetch title from YouTube.", file=sys.stderr)
        if not title:
            print()
            title = prompt_required("Video title", hint="Fraser Island")

    # ── Resolve output path ──────────────────────────────────────────────────
    if output_path is None:
        output_path = out_norm.rstrip("/") + "/" + slug_from_title(title) + ".html"
        print(f"  Output: {output_path}", file=sys.stderr)

    # ── Interactive: location ────────────────────────────────────────────────
    location = args.location
    if location is None:
        print()
        location = prompt_optional("Location", hint="Australia · 1995")

    # ── Breadcrumb ───────────────────────────────────────────────────────────
    back_label = args.back_label
    back_url   = args.back_url
    if not back_label or not back_url:
        inf_label, inf_url = infer_breadcrumb(output_path)
        back_label = back_label or inf_label
        back_url   = back_url   or inf_url

    # ── Build & write page ───────────────────────────────────────────────────
    password_hash = sha256_hex(args.password) if args.password else None
    print()
    page = build_video_page(
        title=title,
        output_path=output_path,
        youtube_id=youtube_id,
        location=location,
        description=args.description,
        back_label=back_label,
        back_url=back_url,
        password_hash=password_hash,
    )
    write_page(output_path, page)

    if not youtube_id:
        print("  ℹ️  No YouTube ID — embed placeholder inserted.", file=sys.stderr)

    # ── Update parent collection ─────────────────────────────────────────────
    if not args.no_parent:
        href = "/" + output_path.replace("\\", "/")
        card = make_video_card(
            href=href,
            title=title,
            meta=location,
            youtube_id=youtube_id,
        )
        print("\n→ Checking parent collection...", file=sys.stderr)
        ensure_parent(output_path, card)
        propagate_counts_up(output_path)

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
