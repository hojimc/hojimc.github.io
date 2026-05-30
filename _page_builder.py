#!/usr/bin/env python3
"""
_page_builder.py — Shared HTML utilities for hojimc.github.io page generators.

Imported by: create_photo_page.py, create_video_page.py, create_collection_page.py
Do not run directly.

TODO: once the site and scripts are finalized, add create_delete_page.py to remove
a page and its card from the parent collection automatically.
"""

import os
import re
import sys
import hashlib

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SITE_OWNER   = "Claude Ho-Jim"
SITE_EMAIL   = "hojimc@hotmail.com"
SITE_URL     = "https://hojimc.github.io"
FONT_URL     = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
    "&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap"
)
BREADCRUMB_JS = "js/breadcrumb.js"

LABEL_MAP = {
    "usa":              "USA",
    "europe":           "Europe",
    "caraibes":         "Caraïbes",
    "amusement-parks":  "Amusement Parks",
    "sarasota":         "Sarasota",
    "murales":          "Murales",
    "travel":           "Travel Videos",
    "drone":            "Drone Videos",
    "felix-et-anais":   "Félix et Anaïs",
    "other":            "Other",
    "videos-de-felix":  "Vidéos de Félix",
    "olivier":          "Olivier",
    "california":       "California",
    "vacances":         "Vacances",
    "vacances-2015":    "Vacances 2015",
    "vacances-2009":    "Vacances 2009",
    "espagne-2018":     "Espagne 2018",
    "europe-2013":      "Europe 2013",
    "lille-2014":       "Lille",
    "portfolio":        "Portfolio",
    "best-photos":      "Best Photos",
    "night-shots":      "Night Shots",
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def sha256_hex(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def slug_from_title(title: str) -> str:
    s = title.lower()
    for src, dst in [
        ("à","a"),("â","a"),("ä","a"),("é","e"),("è","e"),("ê","e"),("ë","e"),
        ("î","i"),("ï","i"),("ô","o"),("ö","o"),("ù","u"),("û","u"),("ü","u"),
        ("ç","c"),("ñ","n"),("æ","ae"),("œ","oe"),
    ]:
        s = s.replace(src, dst)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def og_url_from_path(output_path: str) -> str:
    path = output_path.replace("\\", "/").lstrip("./")
    return f"{SITE_URL}/{path}"


def infer_section(output_path: str) -> str:
    """Return 'videos' if path starts with videos/, else 'photos'."""
    return "videos" if output_path.replace("\\", "/").startswith("videos/") else "photos"


def infer_breadcrumb(output_path: str):
    """Return (label, url) for the immediate parent, or (None, None) at root."""
    parts = output_path.replace("\\", "/").split("/")
    if len(parts) < 2:
        return None, None
    parent_slug = parts[-2]
    label = LABEL_MAP.get(parent_slug, parent_slug.replace("-", " ").title())
    url   = "/" + "/".join(parts[:-1]) + ".html"
    return label, url


def infer_parent_path(output_path: str) -> str | None:
    """Return the expected parent collection .html path, or None at root level.

    photos/usa/sarasota/birds.html  →  photos/usa/sarasota.html
    photos/usa/sarasota.html        →  photos/usa.html
    photos/usa.html                 →  None  (parent is index.html — not a collection)
    """
    parts = output_path.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return None
    parent_parts = parts[:-1]                          # drop filename
    return "/".join(parent_parts[:-1]) + "/" + parent_parts[-1] + ".html"


def key_from_path(output_path: str) -> str:
    return os.path.splitext(os.path.basename(output_path.replace("\\", "/")))[0]


def label_from_path(output_path: str) -> str:
    key = key_from_path(output_path)
    return LABEL_MAP.get(key, key.replace("-", " ").title())


# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------

def prompt_required(label: str, hint: str = None) -> str:
    hint_str = f" (e.g. {hint})" if hint else ""
    while True:
        val = input(f"  {label}{hint_str}: ").strip()
        if val:
            return val
        print("  (required — please enter a value)")


def prompt_optional(label: str, hint: str = None) -> str | None:
    hint_str = f" (e.g. {hint})" if hint else ""
    val = input(f"  {label}{hint_str} [Enter to skip]: ").strip()
    return val or None


def prompt_yes(question: str, default_yes: bool = True) -> bool:
    suffix = "[Y/n]" if default_yes else "[y/N]"
    val = input(f"  {question} {suffix}: ").strip().lower()
    if not val:
        return default_yes
    return val in ("y", "yes")


# ---------------------------------------------------------------------------
# HTML fragment builders
# ---------------------------------------------------------------------------

def _head(title: str, description: str, og_url: str,
          password_hash: str = None, has_carousel: bool = False) -> str:
    protected = password_hash is not None

    if protected:
        og_title = f"Private Album — {SITE_OWNER}"
        og_desc  = f"Private photo album by {SITE_OWNER}."
    else:
        og_title = f"{title} — {SITE_OWNER}"
        og_desc  = description

    carousel_css = (
        "\n  <!-- publicalbum embed stylesheet -->\n"
        "  <link rel=\"stylesheet\""
        " href=\"https://cdn.jsdelivr.net/npm/publicalbum@latest/embed-ui.min.css\">"
        if has_carousel else ""
    )

    auth_script = (
        f"\n  <script src=\"/js/auth.js\" data-hash=\"{password_hash}\" defer></script>"
        if protected else ""
    )

    return f"""\
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {SITE_OWNER}</title>
  <meta name="description" content="{description}">

  <meta property="og:title"       content="{og_title}">
  <meta property="og:description" content="{og_desc}">
  <meta property="og:image"       content="{SITE_URL}/assets/og-image.jpg">
  <meta property="og:url"         content="{og_url}">
  <meta property="og:type"        content="website">

  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONT_URL}" rel="stylesheet">

  <link rel="stylesheet" href="/css/style.css">{carousel_css}{auth_script}
</head>"""


def _nav(section: str) -> str:
    pa = " nav__link--active" if section == "photos" else ""
    va = " nav__link--active" if section == "videos" else ""
    return f"""\
  <nav class="nav" aria-label="Main navigation">
    <div class="nav__inner">
      <a href="/" class="nav__logo">{SITE_OWNER}</a>
      <button class="nav__toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav__links" id="nav-links" role="list">
        <li><a href="/"            class="nav__link{pa}">My Photos</a></li>
        <li><a href="/videos.html" class="nav__link{va}">My Videos</a></li>
        <li><a href="/blog.html"   class="nav__link">My Blog</a></li>
      </ul>
    </div>
  </nav>"""


def _footer() -> str:
    return (
        f'  <footer class="footer">\n'
        f'    <div class="container">\n'
        f'      <p>&copy; 2026 {SITE_OWNER} &nbsp;&middot;&nbsp;'
        f' <a href="mailto:{SITE_EMAIL}">Contact</a></p>\n'
        f'    </div>\n'
        f'  </footer>'
    )


def _page_header(title: str, back_label: str = None, back_url: str = None,
                 meta: str = None, description: str = None) -> str:
    back = (
        f'\n        <a href="{back_url}" class="page-header__back">{back_label}</a>'
        if back_label and back_url else ""
    )
    meta_line = f'\n        <p class="page-header__meta">{meta}</p>' if meta else ""
    desc_line = f'\n        <p class="page-header__desc">{description}</p>' if description else ""
    return (
        f'      <!-- ── Page header ── -->\n'
        f'      <header class="page-header">{back}\n'
        f'        <h1 class="page-header__title">{title}</h1>{meta_line}{desc_line}\n'
        f'      </header>'
    )


# ---------------------------------------------------------------------------
# Card builders
# ---------------------------------------------------------------------------

def _img_wrap(thumbnail_url: str, alt: str) -> str:
    if thumbnail_url:
        return (
            f'          <div class="card__img-wrap">\n'
            f'            <img\n'
            f'              class="card__img"\n'
            f'              src="{thumbnail_url}"\n'
            f'              alt="{alt}"\n'
            f'              loading="lazy"\n'
            f'            >\n'
            f'          </div>'
        )
    return '          <div class="card__img-wrap">\n            <div class="card__img-placeholder"></div>\n          </div>'


def make_photo_card(href: str, title: str, meta: str = None, thumbnail_url: str = None) -> str:
    meta_line = f'\n            <p class="card__meta">{meta}</p>' if meta else ""
    return (
        f'        <a href="{href}" class="card">\n'
        f'{_img_wrap(thumbnail_url, title)}\n'
        f'          <div class="card__body">\n'
        f'            <h3 class="card__title">{title}</h3>{meta_line}\n'
        f'          </div>\n'
        f'        </a>'
    )


def make_video_card(href: str, title: str, meta: str = None, youtube_id: str = None) -> str:
    thumb = f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg" if youtube_id else None
    meta_line = f'\n            <p class="card__meta">{meta}</p>' if meta else ""
    return (
        f'        <a href="{href}" class="card">\n'
        f'{_img_wrap(thumb, title)}\n'
        f'          <div class="card__body">\n'
        f'            <h3 class="card__title">{title}</h3>{meta_line}\n'
        f'          </div>\n'
        f'        </a>'
    )


def make_category_card(href: str, title: str, meta: str = None, thumbnail_url: str = None) -> str:
    """card--category renders a 'COLLECTION' label via CSS ::before."""
    meta_line = f'\n            <p class="card__meta">{meta}</p>' if meta else ""
    return (
        f'        <a href="{href}" class="card card--category">\n'
        f'{_img_wrap(thumbnail_url, title)}\n'
        f'          <div class="card__body">\n'
        f'            <h3 class="card__title">{title}</h3>{meta_line}\n'
        f'          </div>\n'
        f'        </a>'
    )


# ---------------------------------------------------------------------------
# Full page builders
# ---------------------------------------------------------------------------

_CAROUSEL_PLACEHOLDER = '''\
      <!-- ── Google Photos Carousel ──────────────────────────────────
           Run:  python generate_embed.py <google_photos_url> "{title}"
           Then paste the output <div> block here in place of this comment.
      -->
      <div class="coming-soon">
        <p>Album coming soon.</p>
      </div>'''

_VIDEO_PLACEHOLDER = '''\
      <!-- ── YouTube Embed ──────────────────────────────────────────
           Replace YOUTUBE_VIDEO_ID_HERE with the actual video ID.
           (YouTube → Share → Embed → copy the ID from the iframe src)
      -->
      <div class="video-wrapper">
        <iframe
          src="https://www.youtube.com/embed/YOUTUBE_VIDEO_ID_HERE"
          title="{title}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen>
        </iframe>
      </div>'''


def build_photo_page(title: str, output_path: str, embed_html: str = None,
                     password_hash: str = None, location: str = None,
                     description: str = None, back_label: str = None,
                     back_url: str = None) -> str:
    section      = infer_section(output_path)
    has_carousel = embed_html is not None
    desc         = f"Photos: {title} — {SITE_OWNER}."

    carousel_block = (
        f"      {embed_html}"
        if embed_html
        else _CAROUSEL_PLACEHOLDER.format(title=title)
    )

    carousel_js = (
        '  <script src="/js/gallery.js"></script>\n'
        '  <!-- publicalbum embed script — loads the carousel above -->\n'
        '  <script src="https://cdn.jsdelivr.net/npm/publicalbum@latest/embed-ui.min.js" async></script>\n'
        if has_carousel else ""
    )

    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'{_head(title, desc, og_url_from_path(output_path), password_hash, has_carousel)}\n'
        f'<body>\n\n'
        f'  {_nav(section)}\n\n'
        f'  <main id="main">\n'
        f'    <div class="container">\n\n'
        f'      {_page_header(title, back_label, back_url, location, description)}\n\n'
        f'{carousel_block}\n\n'
        f'    </div>\n'
        f'  </main>\n\n'
        f'  {_footer()}\n'
        f'  {carousel_js}'
        f'  <script src="/js/breadcrumb.js" defer></script>\n'
        f'  <script src="/js/nav.js" defer></script>\n'
        f'</body>\n'
        f'</html>\n'
    )


def build_video_page(title: str, output_path: str, youtube_id: str = None,
                     location: str = None, description: str = None,
                     back_label: str = None, back_url: str = None) -> str:
    section = infer_section(output_path)
    desc    = f"Video: {title} — {SITE_OWNER}."

    if youtube_id:
        embed_block = (
            f'      <div class="video-wrapper">\n'
            f'        <iframe\n'
            f'          src="https://www.youtube.com/embed/{youtube_id}"\n'
            f'          title="{title}"\n'
            f'          allow="accelerometer; autoplay; clipboard-write;'
            f' encrypted-media; gyroscope; picture-in-picture; web-share"\n'
            f'          allowfullscreen>\n'
            f'        </iframe>\n'
            f'      </div>'
        )
    else:
        embed_block = _VIDEO_PLACEHOLDER.format(title=title)

    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'{_head(title, desc, og_url_from_path(output_path))}\n'
        f'<body>\n\n'
        f'  {_nav(section)}\n\n'
        f'  <main id="main">\n'
        f'    <div class="container">\n\n'
        f'      {_page_header(title, back_label, back_url, location, description)}\n\n'
        f'{embed_block}\n\n'
        f'    </div>\n'
        f'  </main>\n\n'
        f'  {_footer()}\n'
        f'  <script src="/js/breadcrumb.js" defer></script>\n'
        f'  <script src="/js/nav.js" defer></script>\n'
        f'</body>\n'
        f'</html>\n'
    )


def build_collection_page(title: str, output_path: str, back_label: str = None,
                           back_url: str = None, meta: str = None,
                           description: str = None) -> str:
    section = infer_section(output_path)
    if section == "videos":
        desc = f"Videos: {title} — {SITE_OWNER}."
    else:
        desc = f"Photo albums: {title} — {SITE_OWNER}."

    return (
        f'<!DOCTYPE html>\n'
        f'<html lang="en">\n'
        f'{_head(title, desc, og_url_from_path(output_path))}\n'
        f'<body>\n\n'
        f'  {_nav(section)}\n\n'
        f'  <main id="main">\n'
        f'    <div class="container">\n\n'
        f'      {_page_header(title, back_label, back_url, meta, description)}\n\n'
        f'      <div class="grid">\n\n'
        f'        <!-- /grid -->\n'
        f'      </div>\n\n'
        f'    </div>\n'
        f'  </main>\n\n'
        f'  {_footer()}\n'
        f'  <script src="/js/breadcrumb.js" defer></script>\n'
        f'  <script src="/js/nav.js" defer></script>\n'
        f'</body>\n'
        f'</html>\n'
    )


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def _find_grid_close(html: str) -> int:
    """Return the index of the </div> closing <div class="grid">."""
    m = re.search(r'<div[^>]*class="grid"', html)
    if not m:
        return -1
    depth = 0
    i = m.start()
    n = len(html)
    while i < n:
        if html[i] == '<':
            if (html[i:i+4] == '<div' and
                    (i + 4 >= n or html[i + 4] in ' \t\n\r>/')):
                depth += 1
                i += 4
            elif html[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    return i
                i += 6
            else:
                i += 1
        else:
            i += 1
    return -1


def inject_card_into_collection(html_path: str, card_html: str) -> bool:
    """Insert card_html into the .grid of an existing collection page.

    Strategy 1: look for <!-- /grid --> marker (pages created by these scripts).
    Strategy 2: find the closing </div> of .grid by counting depth.
    Writes in-place. Returns True on success.
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    MARKER = "        <!-- /grid -->"
    if MARKER in html:
        html = html.replace(MARKER, f"{card_html}\n\n{MARKER}", 1)
    else:
        close_idx = _find_grid_close(html)
        if close_idx == -1:
            print(f"  ! Could not find .grid in {html_path} — card not injected.",
                  file=sys.stderr)
            return False
        # Insert before the line containing </div>
        line_start = html.rfind("\n", 0, close_idx)
        insert_at  = (line_start + 1) if line_start != -1 else close_idx
        html = html[:insert_at] + card_html + "\n\n" + html[insert_at:]

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def update_breadcrumb_js(js_path: str, key: str, label: str, url: str) -> bool:
    """Add key → {label, url} to the map in breadcrumb.js.

    Returns True if added, False if the key was already present or file not found.
    """
    if not os.path.exists(js_path):
        print(f"  ! {js_path} not found — breadcrumb not updated.", file=sys.stderr)
        return False

    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if key already registered (bare or quoted)
    pattern = rf"(^|\s)'{re.escape(key)}':|(\s){re.escape(key)}:"
    if re.search(pattern, content):
        return False

    # Find closing }; of the map and insert before it
    insert_point = content.rfind("  };")
    if insert_point == -1:
        print(f"  ! Could not locate map in {js_path}.", file=sys.stderr)
        return False

    key_str  = f"'{key}'" if "-" in key else key
    pad_key  = " " * max(1, 18 - len(key_str))
    pad_lbl  = " " * max(1, 22 - len(label))
    new_line = f"    {key_str}:{pad_key}{{ label: '{label}',{pad_lbl}url: '{url}' }},\n"
    content  = content[:insert_point] + new_line + content[insert_point:]

    # Also add to the Supported keys: JSDoc comment
    close_comment = " */"
    idx = content.find(close_comment)
    if idx != -1:
        comment_line = f" *   {key:<18} → {label:<22} ({url})\n"
        content = content[:idx] + comment_line + content[idx:]

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ---------------------------------------------------------------------------
# Recursive parent management
# ---------------------------------------------------------------------------

def ensure_parent(child_path: str, card_html: str) -> None:
    """Ensure the parent collection exists and contains card_html.

    If parent is missing, offer to create it interactively and recurse up the tree.
    """
    parent_path = infer_parent_path(child_path)
    if parent_path is None:
        return  # reached root level

    if os.path.exists(parent_path):
        print(f"  → Updating: {parent_path}", file=sys.stderr)
        inject_card_into_collection(parent_path, card_html)
        return

    parent_label = label_from_path(parent_path)
    print(f"\n  Parent collection '{parent_label}' ({parent_path}) does not exist.")
    if not prompt_yes("Create it?"):
        print(f"  ! Skipped. Manually create {parent_path} and add the card.",
              file=sys.stderr)
        return

    print(f"  Building '{parent_label}' collection...")
    section  = infer_section(parent_path)
    meta_hint = "Florida, USA · 3 albums" if section == "photos" else "3 videos"
    meta     = prompt_optional("  Meta line", hint=meta_hint)
    desc     = prompt_optional("  Description (optional subtitle)")

    back_label_p, back_url_p = infer_breadcrumb(parent_path)
    html = build_collection_page(
        title=parent_label,
        output_path=parent_path,
        back_label=back_label_p,
        back_url=back_url_p,
        meta=meta,
        description=desc,
    )
    write_page(parent_path, html)

    # Register in breadcrumb.js
    key    = key_from_path(parent_path)
    bc_url = "/" + parent_path.replace("\\", "/")
    if update_breadcrumb_js(BREADCRUMB_JS, key, parent_label, bc_url):
        print(f"  → breadcrumb.js: registered '{key}'", file=sys.stderr)

    # Inject the child's card into the new parent
    inject_card_into_collection(parent_path, card_html)

    # Now handle the grandparent — the new parent is always a collection
    grandparent_card = make_category_card(
        href=bc_url,
        title=parent_label,
        meta=meta,
    )
    ensure_parent(parent_path, grandparent_card)


# ---------------------------------------------------------------------------
# Write helper
# ---------------------------------------------------------------------------

def write_page(output_path: str, html: str) -> None:
    dir_part = os.path.dirname(os.path.abspath(output_path))
    if dir_part:
        os.makedirs(dir_part, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  → Saved: {output_path}", file=sys.stderr)
