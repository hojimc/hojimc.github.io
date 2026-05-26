# hojimc.github.io — Site Reference

Quick reference for **Felix** (runs the Python scripts) and **Claude Ho-Jim** (edits directly on GitHub).

Live site: **https://hojimc.github.io**

---

## Felix — Creating a photo album page

Use `create_photo_page.py` to generate a complete, ready-to-deploy HTML file.

### Auto mode (recommended) — title and filename come from the album

Just give the parent folder and the Google Photos link. The script reads the album name, generates the slug, and creates the file:

```bash
python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6
# → Album name: 'Murales 2017'
# → Output:     photos/murales/murales-2017.html
# → Detected date: Saturday, Jun 17, 2017
# → Tip: re-run with --location "Place · 2017"
```

With location (once you know the city):

```bash
python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6 \
    --location "Montréal, Canada · 2017"
```

With password protection:

```bash
python create_photo_page.py photos/europe/lille/ https://photos.app.goo.gl/J2FfnjQrz7tjE45P6 mysecretpassword \
    --location "Lille, France · 2014"
```

> The password is SHA-256 hashed automatically — the plain-text password is never stored in the file.

### Explicit mode — full control over path and title

Use this for placeholder pages (no album yet), or when you need a custom filename:

```bash
# Placeholder — no album yet, carousel added later
python create_photo_page.py photos/usa/new-york.html "New York" \
    --location "New York, USA"

# Full explicit with album URL
python create_photo_page.py photos/usa/miami-key-west.html "Miami - Key West" \
    https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 \
    --location "Florida, USA · 2017"
```

### All arguments

| Argument | Mode | Description |
|---|---|---|
| `parent_dir/` | auto | Parent folder — title and filename auto-derived from album |
| `output.html` | explicit | Full output path |
| `album_url` | auto (required) / explicit (optional) | Google Photos share link |
| `title` | explicit only | Album title shown in the page header |
| `password` | both | Plain-text password — SHA-256 hashed automatically |
| `--location` | both | Location · year shown under the title |
| `--description` | both | Description paragraph under the location |
| `--back-label` | both | Breadcrumb label (auto-inferred from path if omitted) |
| `--back-url` | both | Breadcrumb URL (auto-inferred from path if omitted) |

> **Year auto-detection:** omitting `--location` is fine on a first run — the script reads the year from Google Photos and prints a suggestion. Only the year is auto-detected; the city/country must be typed manually.

### After running the script

1. Open the **parent category page** (e.g. `photos/usa.html`) and add a new `.card` entry linking to the new file.
2. Commit and push:

```bash
git add .
git commit -m "add Miami - Key West album"
git push
```

GitHub Pages rebuilds automatically — live within ~60 seconds.

---

## Felix — Refreshing a carousel (new photos added to an album)

Photo URLs are baked in at generation time. If new photos were added to an album on Google Photos, regenerate the page:

```bash
python create_photo_page.py photos/usa/miami-key-west.html "Miami - Key West" \
    https://photos.app.goo.gl/PHMb52hzQu7KpgEv8 \
    --location "Florida, USA · 2017"
```

This overwrites the existing file with fresh photo URLs.

---

## Claude Ho-Jim — Adding a video (via GitHub.com)

1. Go to the correct folder on GitHub (e.g. `videos/travel/`)
2. Click **Add file → Create new file**, name it `title-year.html`
3. Copy the contents of `videos/travel/fraser-island.html`
4. Replace: title, location/year, description, and the YouTube video ID in the `src` URL
5. Open the category page (e.g. `videos/travel.html`) and add a new card:
   ```html
   <a href="/videos/travel/your-video.html" class="card">
     <div class="card__img-wrap">
       <img class="card__img" src="https://img.youtube.com/vi/YOUR_VIDEO_ID/hqdefault.jpg" alt="Video title" loading="lazy">
     </div>
     <div class="card__info">
       <p class="card__title">Video Title</p>
       <p class="card__meta">Location · Year</p>
     </div>
   </a>
   ```
6. Click **Commit changes** — live within ~60 seconds

---

## Claude Ho-Jim — Adding a blog post (via GitHub.com)

1. Go to the `blog/` folder on GitHub
2. Click **Add file → Create new file**, name it `destination-year.html`
3. Copy the contents of `blog/_template.html`
4. Fill in all sections marked `✏️ EDIT` (title, date, text, photos, embeds)
5. Open `blog.html` and add a new `.blog-card` entry (see the commented example inside that file)
6. Click **Commit changes** — live within ~60 seconds

---

## All Google Photos album links

All album links are stored in **`links.md`** in the project root (not pushed to GitHub — local only).

---

## Deploying (Felix)

```bash
git add .
git commit -m "describe what changed"
git push
```

GitHub Pages rebuilds automatically — live within ~60 seconds.
