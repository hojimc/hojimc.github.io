"""
Optimize card thumbnails for web: resize to 600px wide and convert to WebP.

Usage:
    python optimize_thumbnails.py                    # process all non-WebP images in assets/thumbnails/
    python optimize_thumbnails.py path/to/image.jpg  # process a specific file
    python optimize_thumbnails.py path/to/folder/    # process a specific subfolder

After running, pass the .webp path to create_photo_page.py --thumbnail.
"""

import sys
from pathlib import Path
from PIL import Image

REPO = Path(__file__).parent
THUMB_DIR = REPO / "assets" / "thumbnails"
MAX_WIDTH = 600
WEBP_QUALITY = 85
SOURCE_EXTS = {".jpg", ".jpeg", ".png"}


def optimize(img_path: Path):
    webp_path = img_path.with_suffix(".webp")
    orig_kb = img_path.stat().st_size // 1024

    with Image.open(img_path) as img:
        if img.width > MAX_WIDTH:
            new_h = round(img.height * MAX_WIDTH / img.width)
            img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)
        img.save(webp_path, "WEBP", quality=WEBP_QUALITY, method=6)

    new_kb = webp_path.stat().st_size // 1024
    img_path.unlink()
    print(f"  {img_path.name} -> {webp_path.name}  ({orig_kb}KB -> {new_kb}KB)")
    return img_path, webp_path


def update_html(converted: list):
    updated = []
    for html_path in REPO.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        new_text = text
        for orig, webp in converted:
            old_ref = "/" + orig.relative_to(REPO).as_posix()
            new_ref = "/" + webp.relative_to(REPO).as_posix()
            new_text = new_text.replace(old_ref, new_ref)
        if new_text != text:
            html_path.write_text(new_text, encoding="utf-8")
            updated.append(html_path)
    return updated


def collect_targets(arg: Path) -> list:
    if arg.is_file():
        return [arg] if arg.suffix.lower() in SOURCE_EXTS else []
    if arg.is_dir():
        return [p for p in sorted(arg.rglob("*")) if p.suffix.lower() in SOURCE_EXTS]
    return []


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = []
        for a in sys.argv[1:]:
            targets.extend(collect_targets(Path(a).resolve()))
    else:
        targets = [p for p in sorted(THUMB_DIR.rglob("*")) if p.suffix.lower() in SOURCE_EXTS]

    if not targets:
        print("No images to process.")
        sys.exit(0)

    print(f"Processing {len(targets)} image(s)...")
    converted = [optimize(p) for p in targets]

    updated = update_html(converted)
    if updated:
        print(f"\nUpdated HTML references in:")
        for f in updated:
            print(f"  {f.relative_to(REPO)}")

    total_saved = sum(
        (orig.stat().st_size if orig.exists() else 0) for orig, _ in converted
    )
    print(f"\nDone. {len(converted)} image(s) optimized.")
