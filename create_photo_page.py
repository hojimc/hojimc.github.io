#!/usr/bin/env python3
"""
create_photo_page.py — Generate a complete photo album HTML page for hojimc.github.io.

── AUTO MODE (recommended when you have an album URL) ──────────────────────────
    python create_photo_page.py <parent_dir> <album_url> [password] [options]

    Title and filename are derived automatically from the Google Photos album name.
    e.g.  "Murales 2017"  →  title="Murales 2017", file="murales-2017.html"

    Examples:
        python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6
        python create_photo_page.py photos/europe/lille/ https://photos.app.goo.gl/J2FfnjQrz7tjE45P6 mysecretpassword

── EXPLICIT MODE (when you need full control, or no album URL yet) ──────────────
    python create_photo_page.py <output.html> <title> [album_url] [password] [options]

    Examples:
        python create_photo_page.py photos/usa/miami-key-west.html "Miami - Key West" \\
            https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 --location "Florida, USA · 2018"

        python create_photo_page.py photos/usa/new-york.html "New York" \\
            --location "New York, USA"

Options (both modes):
    --location      Location · year line shown under the title, e.g. "Florida, USA · 2018"
    --description   Optional paragraph shown under the location line
    --back-label    Breadcrumb label (auto-inferred from path if omitted)
    --back-url      Breadcrumb URL   (auto-inferred from path if omitted)

Note: --location is optional. If omitted and an album URL is given, the year is
auto-detected from the album's metadata and printed as a suggestion.
"""

import sys
import os
import re
import hashlib
import argparse

# ---------------------------------------------------------------------------
# Import generate_embed functions directly (same repo)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_embed import resolve_share_url, fetch, extract_photo_urls, make_embed, extract_album_meta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_hex(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


LABEL_MAP = {
    "usa": "USA",
    "europe": "Europe",
    "caraibes": "Caraïbes",
    "amusement-parks": "Amusement Parks",
    "sarasota": "Sarasota",
    "murales": "Murales",
    "travel": "Travel",
}


def infer_breadcrumb(output_path: str):
    """Infer breadcrumb label + URL from the output file path.

    photos/usa/miami-key-west.html      → ("USA",     "/photos/usa.html")
    photos/europe/famille.html          → ("Europe",   "/photos/europe.html")
    photos/usa/sarasota/sarasota-2014.html → ("Sarasota", "/photos/usa/sarasota.html")
    """
    parts = output_path.replace("\\", "/").split("/")
    # parts: ['photos', 'usa', 'miami-key-west.html']
    if len(parts) < 3:
        return None, None
    parent_dir = parts[-2]          # e.g. 'usa'
    label = LABEL_MAP.get(parent_dir, parent_dir.replace("-", " ").title())
    url_parts = parts[:-1]          # drop filename
    url = "/" + "/".join(url_parts) + ".html"
    return label, url


def slug_from_title(title: str) -> str:
    """Convert title to a URL/file slug."""
    s = title.lower()
    s = re.sub(r"[àâä]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[îï]", "i", s)
    s = re.sub(r"[ôö]", "o", s)
    s = re.sub(r"[ùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def og_url(output_path: str) -> str:
    path = output_path.replace("\\", "/").lstrip("./")
    return f"https://hojimc.github.io/{path}"


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------

CAROUSEL_PLACEHOLDER = """\
      <!-- ── Google Photos Carousel (not yet linked) ──────────────────────
           Run:  python generate_embed.py <google_photos_url> "{title}"
           Then replace this comment with the generated <div> block.
      -->
      <div class="coming-soon">
        <p>📷 Album coming soon.</p>
      </div>"""


def build_page(
    title: str,
    output_path: str,
    embed_html: str | None,
    password_hash: str | None,
    location: str | None,
    description: str | None,
    back_label: str | None,
    back_url: str | None,
) -> str:

    protected = password_hash is not None

    # ── <head> extras ────────────────────────────────────────────────────
    auth_script = (
        f'\n  <script src="/js/auth.js" data-hash="{password_hash}" defer></script>'
        if protected else ""
    )

    og_block = "" if protected else f"""\
  <meta property="og:title"       content="{title} — Claude Ho-Jim">
  <meta property="og:description" content="Photos: {title} by Claude Ho-Jim.">
  <meta property="og:image"       content="https://hojimc.github.io/assets/og-image.jpg">
  <meta property="og:url"         content="{og_url(output_path)}">
  <meta property="og:type"        content="website">

"""

    publicalbum_css = (
        '\n  <!-- publicalbum embed stylesheet -->\n'
        '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/publicalbum@latest/embed-ui.min.css">'
        if embed_html else ""
    )

    # ── breadcrumb ───────────────────────────────────────────────────────
    breadcrumb = ""
    if back_label and back_url:
        breadcrumb = f'\n        <a href="{back_url}" class="page-header__back">{back_label}</a>'

    # ── location line ────────────────────────────────────────────────────
    location_line = (
        f'\n        <p class="page-header__meta">{location}</p>'
        if location else ""
    )

    # ── description line ─────────────────────────────────────────────────
    desc_line = (
        f'\n        <p class="page-header__desc">{description}</p>'
        if description else ""
    )

    # ── carousel block ───────────────────────────────────────────────────
    carousel_block = (
        f"\n      {embed_html}"
        if embed_html
        else "\n" + CAROUSEL_PLACEHOLDER.format(title=title)
    )

    # ── publicalbum script ───────────────────────────────────────────────
    publicalbum_js = (
        '\n  <!-- publicalbum embed script — loads the carousel above -->\n'
        '  <script src="https://cdn.jsdelivr.net/npm/publicalbum@latest/embed-ui.min.js" async></script>'
        if embed_html else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Claude Ho-Jim</title>
  <meta name="description" content="Photos: {title} by Claude Ho-Jim.">{auth_script}

  {og_block}<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/css/style.css">{publicalbum_css}
</head>
<body>

  <nav class="nav" aria-label="Main navigation">
    <div class="nav__inner">
      <a href="/" class="nav__logo">Claude Ho-Jim</a>
      <button class="nav__toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav__links" id="nav-links" role="list">
        <li><a href="/"            class="nav__link nav__link--active">My Photos</a></li>
        <li><a href="/videos.html" class="nav__link">My Videos</a></li>
        <li><a href="/blog.html"   class="nav__link">My Blog</a></li>
      </ul>
    </div>
  </nav>

  <main id="main">
    <div class="container">

      <!-- ── Page header ── -->
      <header class="page-header">{breadcrumb}
        <h1 class="page-header__title">{title}</h1>{location_line}{desc_line}
      </header>
{carousel_block}

    </div>
  </main>

  <footer class="footer">
    <div class="container">
      <p>&copy; 2026 Claude Ho-Jim &nbsp;&middot;&nbsp; <a href="mailto:hojimc@hotmail.com">Contact</a></p>
    </div>
  </footer>
{publicalbum_js}
  <script src="/js/nav.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a photo album HTML page for hojimc.github.io.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("output_path", help=(
        "AUTO MODE:     parent directory, e.g. photos/murales/  "
        "(title + filename derived from album name)\n"
        "EXPLICIT MODE: full .html path, e.g. photos/usa/miami-key-west.html"
    ))
    parser.add_argument("rest", nargs="*", help=(
        "AUTO MODE:     album_url [password]\n"
        "EXPLICIT MODE: title [album_url] [password]"
    ))
    parser.add_argument("--location",    default=None, help='Location · year, e.g. "Florida, USA · 2018"')
    parser.add_argument("--description", default=None, help="Optional description paragraph")
    parser.add_argument("--back-label",  default=None, dest="back_label", help="Breadcrumb label (auto-inferred if omitted)")
    parser.add_argument("--back-url",    default=None, dest="back_url",   help="Breadcrumb URL (auto-inferred if omitted)")
    args = parser.parse_args()

    # ── Detect mode ─────────────────────────────────────────────────────
    # Auto mode:     output_path does NOT end in .html  →  it's a parent directory
    # Explicit mode: output_path ends in .html          →  it's the full output path
    out_norm  = args.output_path.replace("\\", "/")
    auto_mode = not out_norm.endswith(".html")
    rest      = args.rest

    if auto_mode:
        # rest = [album_url, password?]
        album_url = rest[0] if len(rest) > 0 else None
        password  = rest[1] if len(rest) > 1 else None
        title     = None   # resolved from album metadata below
        output_path = None  # resolved from album name below
        if not album_url:
            parser.error(
                "Auto mode requires an album URL as the second argument.\n"
                "  e.g.  python create_photo_page.py photos/murales/ https://photos.app.goo.gl/..."
            )
    else:
        # rest = [title, album_url?, password?]
        title       = rest[0] if len(rest) > 0 else None
        album_url   = rest[1] if len(rest) > 1 else None
        password    = rest[2] if len(rest) > 2 else None
        output_path = out_norm
        if not title:
            parser.error(
                "Explicit mode requires a title as the second argument.\n"
                "  e.g.  python create_photo_page.py photos/usa/new-york.html \"New York\""
            )

    # ── Password hash ───────────────────────────────────────────────────
    password_hash = None
    if password:
        password_hash = sha256_hex(password)
        print(f"→ Password hash (SHA-256): {password_hash}", file=sys.stderr)

    # ── Fetch album (resolve URL, extract metadata + photos) ─────────────
    embed_html = None
    if album_url:
        print(f"→ Resolving share URL...", file=sys.stderr)
        try:
            share_url = resolve_share_url(album_url)
        except Exception as e:
            print(f"  Error resolving URL: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"  {share_url}", file=sys.stderr)

        print(f"→ Fetching album page...", file=sys.stderr)
        try:
            html, _ = fetch(share_url)
        except Exception as e:
            print(f"  Error fetching album: {e}", file=sys.stderr)
            sys.exit(1)

        # ── Album metadata ───────────────────────────────────────────────
        album_name, date_str, year = extract_album_meta(html)

        if auto_mode:
            if not album_name:
                print(
                    "  Error: could not read album name from Google Photos.\n"
                    "  The album may be private, or try explicit mode instead:\n"
                    "    python create_photo_page.py <output.html> \"Title\" <album_url>",
                    file=sys.stderr,
                )
                sys.exit(1)
            title = album_name
            slug  = slug_from_title(title)
            output_path = out_norm.rstrip("/") + "/" + slug + ".html"
            print(f"  Album name: {title!r}", file=sys.stderr)
            print(f"  Output:     {output_path}", file=sys.stderr)

        if date_str:
            print(f"  Detected date:  {date_str}", file=sys.stderr)
        if not args.location:
            if year:
                print(f"  ℹ️  --location not set. Detected year: {year}", file=sys.stderr)
                print(f"      Tip: re-run with --location \"Place · {year}\"", file=sys.stderr)
            else:
                print(f"  ℹ️  --location not set. Pass --location \"Place · Year\" to label the page.", file=sys.stderr)

        print(f"→ Extracting photo URLs...", file=sys.stderr)
        photo_urls = extract_photo_urls(html)
        print(f"  Found {len(photo_urls)} photos.", file=sys.stderr)

        if not photo_urls:
            print("  No photos found — album may be private. Page will be created without carousel.", file=sys.stderr)
        else:
            embed_html = make_embed(share_url, title, photo_urls)

    # ── Breadcrumb ───────────────────────────────────────────────────────
    back_label = args.back_label
    back_url   = args.back_url
    if not back_label or not back_url:
        inf_label, inf_url = infer_breadcrumb(output_path)
        back_label = back_label or inf_label
        back_url   = back_url   or inf_url

    # ── Build page ───────────────────────────────────────────────────────
    page = build_page(
        title=title,
        output_path=output_path,
        embed_html=embed_html,
        password_hash=password_hash,
        location=args.location,
        description=args.description,
        back_label=back_label,
        back_url=back_url,
    )

    # ── Write file ───────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"→ Saved: {output_path}", file=sys.stderr)
    if password:
        print(f"  ⚠️  Page is password-protected. Share the password separately.", file=sys.stderr)
    if not album_url:
        print(f"  ℹ️  No album URL provided — carousel placeholder inserted.", file=sys.stderr)
        print(f"      Add later: python generate_embed.py <url> \"{title}\"", file=sys.stderr)


if __name__ == "__main__":
    main()
