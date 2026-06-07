#!/usr/bin/env python3
"""
generate_embed.py — Generate publicalbum embed HTML from a Google Photos shared album.

Replaces the need to use reabr.com manually.

Usage:
    python scripts/generate_embed.py <google_photos_url> "<Album Title>" [output_file.html]

Examples:
    python scripts/generate_embed.py https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 "Miami - Key West"
    python scripts/generate_embed.py https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 "Miami - Key West" output.html

If no output file is given, prints the embed <div> to stdout so you can copy-paste it.
"""

import sys
import re
import urllib.request
import urllib.error

PHOTO_SIZE = "w1920-h1080"  # Size appended to each photo URL (matches existing site embeds)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8"), resp.url


def resolve_share_url(url):
    """Follow the short goo.gl redirect to get the full photos.google.com/share/... URL."""
    _, final_url = fetch(url)
    return final_url


def extract_photo_urls(html):
    """Extract unique photo base URLs and append the display size."""
    # Match lh3.googleusercontent.com/pw/... URLs (the /pw/ prefix = user photo, not avatar)
    raw = re.findall(r'https://lh3\.googleusercontent\.com/pw/[^"\'=\s]+', html)
    # Strip any trailing size params (=wNNN-hNNN...) that may have slipped through
    bases = []
    seen = set()
    for url in raw:
        base = re.sub(r'=w\d.*$', '', url)
        if base not in seen:
            seen.add(base)
            bases.append(base)
    # Append the target display size
    return [f"{b}={PHOTO_SIZE}" for b in bases]


def extract_album_meta(html):
    """Extract album name and date from the og:title meta tag.

    Google Photos og:title format:
        "Album Name · Day, Mon DD, YYYY 📸"

    Returns:
        (album_name, date_str, year) — any value may be None if not found.
    """
    m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if not m:
        return None, None, None

    og_title = m.group(1)
    # Split on " · " (middle dot U+00B7 with surrounding spaces)
    parts = og_title.split(' · ', 1)
    if len(parts) == 2:
        album_name = parts[0].strip()
        date_raw   = parts[1].strip()
        # Strip non-ASCII characters (e.g. the 📸 emoji)
        date_str = re.sub(r'[^\x00-\x7F]', '', date_raw).strip().rstrip(' .,')
        year_m = re.search(r'\b(20\d{2})\b', date_str)
        year = year_m.group(1) if year_m else None
        return album_name, date_str or None, year
    else:
        # No date separator — og:title is just the album name
        return og_title.strip(), None, None


def make_embed(share_url, title, photo_urls):
    """Build the publicalbum <div> block."""
    objects = "\n  ".join(f'<object data="{u}"></object>' for u in photo_urls)
    return f"""<div class="pa-gallery-player-widget" style="width:100%; display:none;"
  data-delay="3"
  data-link="{share_url}"
  data-title="{title}"
  data-description="">
  {objects}
</div>"""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_url = sys.argv[1]
    title = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"→ Resolving share URL...", file=sys.stderr)
    try:
        share_url = resolve_share_url(input_url)
    except Exception as e:
        print(f"Error resolving URL: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  {share_url}", file=sys.stderr)

    print(f"→ Fetching album page...", file=sys.stderr)
    try:
        html, _ = fetch(share_url)
    except Exception as e:
        print(f"Error fetching album: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"→ Extracting photo URLs...", file=sys.stderr)
    photo_urls = extract_photo_urls(html)
    print(f"  Found {len(photo_urls)} photos.", file=sys.stderr)

    if not photo_urls:
        print("No photos found. The album may be private or the page structure has changed.", file=sys.stderr)
        sys.exit(1)

    embed = make_embed(share_url, title, photo_urls)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(embed)
        print(f"→ Embed saved to: {output_file}", file=sys.stderr)
    else:
        print(embed)


if __name__ == "__main__":
    main()
