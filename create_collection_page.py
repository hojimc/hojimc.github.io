#!/usr/bin/env python3
"""
create_collection_page.py — Generate a photo or video collection page for hojimc.github.io.

A collection page shows a grid of cards linking to sub-albums or sub-collections.
This script handles both photo collections and video collections (same HTML structure).

Usage:
    python create_collection_page.py <output.html OR parent_dir/> <title> [options]

    Photo examples:
        python create_collection_page.py photos/usa/sarasota.html "Sarasota" \\
            --meta "Florida, USA · 3 albums"

        python create_collection_page.py photos/europe/ "Nouvelle Région"

    Video examples:
        python create_collection_page.py videos/drone.html "Drone Videos" \\
            --meta "13 videos · Sarasota, Florida"

        python create_collection_page.py videos/ "New Category"

Options:
    --meta          Subtitle line shown under the title (prompted interactively if omitted)
    --description   Optional longer description paragraph
    --back-label    Breadcrumb label (auto-inferred from path if omitted)
    --back-url      Breadcrumb URL   (auto-inferred from path if omitted)
    --no-parent     Skip updating the parent collection page

After creation the script:
  1. Registers the new collection in js/breadcrumb.js automatically
  2. Injects a card--category entry into the parent collection (creating it if needed)

To add cards to the new collection, run create_photo_page.py or create_video_page.py
pointing at the new directory — each will inject its card automatically.

TODO: once the site and scripts are finalized, add create_delete_page.py to
      remove a page and its card from the parent collection automatically.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from _page_builder import (
    slug_from_title, infer_breadcrumb,
    build_collection_page, make_category_card, ensure_parent, write_page,
    update_breadcrumb_js, key_from_path, BREADCRUMB_JS,
    prompt_optional,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a collection page for hojimc.github.io.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("output_path", help=(
        "Full .html path (e.g. photos/usa/sarasota.html) or "
        "parent directory (e.g. photos/usa/) — filename derived from title"
    ))
    parser.add_argument("title", help="Collection title (e.g. 'Sarasota' or 'Drone Videos')")
    parser.add_argument("--meta",        default=None,
                        help='Subtitle, e.g. "Florida, USA · 3 albums" or "13 videos"')
    parser.add_argument("--description", default=None,
                        help="Optional longer description paragraph")
    parser.add_argument("--back-label",  default=None, dest="back_label")
    parser.add_argument("--back-url",    default=None, dest="back_url")
    parser.add_argument("--no-parent",   action="store_true", dest="no_parent",
                        help="Skip updating the parent collection page")
    args = parser.parse_args()

    out_norm = args.output_path.replace("\\", "/")
    if out_norm.endswith(".html"):
        output_path = out_norm
    else:
        slug        = slug_from_title(args.title)
        output_path = out_norm.rstrip("/") + "/" + slug + ".html"
        print(f"  Output: {output_path}", file=sys.stderr)

    # ── Interactive: meta ────────────────────────────────────────────────────
    meta = args.meta
    if meta is None:
        print()
        meta = prompt_optional("Meta / subtitle", hint="Florida, USA · 3 albums")

    # ── Breadcrumb ───────────────────────────────────────────────────────────
    back_label = args.back_label
    back_url   = args.back_url
    if not back_label or not back_url:
        inf_label, inf_url = infer_breadcrumb(output_path)
        back_label = back_label or inf_label
        back_url   = back_url   or inf_url

    # ── Build & write page ───────────────────────────────────────────────────
    print()
    page = build_collection_page(
        title=args.title,
        output_path=output_path,
        back_label=back_label,
        back_url=back_url,
        meta=meta,
        description=args.description,
    )
    write_page(output_path, page)

    # ── Register in breadcrumb.js ────────────────────────────────────────────
    key    = key_from_path(output_path)
    bc_url = "/" + output_path.replace("\\", "/")
    if update_breadcrumb_js(BREADCRUMB_JS, key, args.title, bc_url):
        print(f"  → breadcrumb.js: registered '{key}'", file=sys.stderr)
    else:
        print(f"  ℹ️  breadcrumb.js: '{key}' already registered.", file=sys.stderr)

    # ── Update parent collection ─────────────────────────────────────────────
    if not args.no_parent:
        card = make_category_card(
            href=bc_url,
            title=args.title,
            meta=meta,
        )
        print("\n→ Checking parent collection...", file=sys.stderr)
        ensure_parent(output_path, card)

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
