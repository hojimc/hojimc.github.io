#!/usr/bin/env python3
"""
create_photo_page.py — Generate a photo album page for hojimc.github.io.

AUTO MODE — title + filename inferred from the Google Photos album name:
    python create_photo_page.py <parent_dir/> <album_url> [options]

    Examples:
        python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6
        python create_photo_page.py photos/europe/lille/ https://photos.app.goo.gl/J2FfnjQrz7tjE45P6 --password secret

EXPLICIT MODE — full control over path and title:
    python create_photo_page.py <output.html> <title> [album_url] [options]

    Examples:
        python create_photo_page.py photos/usa/miami-key-west.html "Miami - Key West" \\
            https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 --location "Florida, USA · 2018"
        python create_photo_page.py photos/usa/new-york.html "New York"   # no album yet

Options:
    --location      "Place · Year" shown under the title (prompted interactively if omitted)
    --description   Optional paragraph under the location line
    --password      Protect the page with a password (SHA-256 hashed)
    --thumbnail     Card thumbnail URL override (default: first photo in album)
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
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_embed import (
    resolve_share_url, fetch, extract_photo_urls, make_embed, extract_album_meta,
)
from _page_builder import (
    sha256_hex, slug_from_title, infer_breadcrumb,
    build_photo_page, make_photo_card, ensure_parent, write_page,
    prompt_optional,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a photo album page for hojimc.github.io.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("output_path", help=(
        "AUTO: parent directory (e.g. photos/murales/)  |  "
        "EXPLICIT: full .html path (e.g. photos/usa/miami-key-west.html)"
    ))
    parser.add_argument("rest", nargs="*", help=(
        "AUTO: [album_url]  |  EXPLICIT: <title> [album_url]"
    ))
    parser.add_argument("--location",    default=None,
                        help='"Place · Year" shown under the title')
    parser.add_argument("--description", default=None,
                        help="Optional paragraph under the location line")
    parser.add_argument("--password",    default=None,
                        help="Password-protect the page")
    parser.add_argument("--thumbnail",   default=None,
                        help="Card thumbnail URL (default: first album photo)")
    parser.add_argument("--back-label",  default=None, dest="back_label")
    parser.add_argument("--back-url",    default=None, dest="back_url")
    parser.add_argument("--no-parent",   action="store_true", dest="no_parent",
                        help="Skip updating the parent collection page")
    args = parser.parse_args()

    out_norm  = args.output_path.replace("\\", "/")
    auto_mode = not out_norm.endswith(".html")
    rest      = args.rest

    if auto_mode:
        album_url   = rest[0] if rest else None
        title       = None
        output_path = None
        if not album_url:
            parser.error(
                "Auto mode requires an album URL.\n"
                "  e.g.  python create_photo_page.py photos/murales/ https://photos.app.goo.gl/..."
            )
    else:
        title       = rest[0] if rest else None
        album_url   = rest[1] if len(rest) > 1 else None
        output_path = out_norm
        if not title:
            parser.error(
                "Explicit mode requires a title.\n"
                "  e.g.  python create_photo_page.py photos/usa/new-york.html \"New York\""
            )

    password_hash = sha256_hex(args.password) if args.password else None

    # ── Fetch album ──────────────────────────────────────────────────────────
    embed_html  = None
    first_photo = None
    year        = None

    if album_url:
        print("→ Resolving album URL...", file=sys.stderr)
        try:
            share_url = resolve_share_url(album_url)
        except Exception as e:
            sys.exit(f"Error resolving URL: {e}")
        print(f"  {share_url}", file=sys.stderr)

        print("→ Fetching album page...", file=sys.stderr)
        try:
            html_content, _ = fetch(share_url)
        except Exception as e:
            sys.exit(f"Error fetching album: {e}")

        album_name, date_str, year = extract_album_meta(html_content)

        if auto_mode:
            if not album_name:
                sys.exit(
                    "Error: could not read album name from Google Photos.\n"
                    "The album may be private. Try explicit mode:\n"
                    "  python create_photo_page.py <output.html> 'Title' <album_url>"
                )
            title       = album_name
            output_path = out_norm.rstrip("/") + "/" + slug_from_title(title) + ".html"
            print(f"  Album:  {title!r}", file=sys.stderr)
            print(f"  Output: {output_path}", file=sys.stderr)

        if date_str:
            print(f"  Date detected: {date_str}", file=sys.stderr)

        print("→ Extracting photos...", file=sys.stderr)
        photo_urls = extract_photo_urls(html_content)
        print(f"  Found {len(photo_urls)} photos.", file=sys.stderr)

        if photo_urls:
            embed_html  = make_embed(share_url, title, photo_urls)
            first_photo = photo_urls[0]
        else:
            print("  No photos found — album may be private. Creating placeholder.",
                  file=sys.stderr)

    # ── Interactive: location ────────────────────────────────────────────────
    location = args.location
    if location is None:
        hint = f"Florida, USA · {year}" if year else "Florida, USA · 2018"
        print()
        location = prompt_optional("Location", hint=hint)

    # ── Breadcrumb ───────────────────────────────────────────────────────────
    back_label = args.back_label
    back_url   = args.back_url
    if not back_label or not back_url:
        inf_label, inf_url = infer_breadcrumb(output_path)
        back_label = back_label or inf_label
        back_url   = back_url   or inf_url

    # ── Build & write page ───────────────────────────────────────────────────
    print()
    page = build_photo_page(
        title=title,
        output_path=output_path,
        embed_html=embed_html,
        password_hash=password_hash,
        location=location,
        description=args.description,
        back_label=back_label,
        back_url=back_url,
    )
    write_page(output_path, page)

    if args.password:
        print("  ⚠️  Password-protected. Share the password separately.", file=sys.stderr)
    if not album_url:
        print(f'  ℹ️  No album URL — carousel placeholder inserted.', file=sys.stderr)
        print(f'      Later: python generate_embed.py <url> "{title}"', file=sys.stderr)

    # ── Update parent collection ─────────────────────────────────────────────
    if not args.no_parent:
        thumbnail = args.thumbnail or first_photo
        href      = "/" + output_path.replace("\\", "/")
        card      = make_photo_card(
            href=href,
            title=title,
            meta=location,
            thumbnail_url=thumbnail,
        )
        print("\n→ Checking parent collection...", file=sys.stderr)
        ensure_parent(output_path, card)

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
