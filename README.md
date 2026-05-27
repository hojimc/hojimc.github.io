# hojimc.github.io — Site Reference

Quick reference for **Felix** (runs the Python scripts) and **Claude Ho-Jim** (edits directly on GitHub).

Live site: **https://hojimc.github.io**

---

## Felix — Creating a photo album page

Use `create_photo_page.py` to generate a complete, ready-to-deploy HTML file.

### Auto mode (recommended)

Just give the parent folder and the Google Photos link. The script reads the album name, generates the slug, and creates the file:

```bash
python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6
# → Album name: 'Murales 2017'
# → Output:     photos/murales/murales-2017.html
# → Tip: re-run with --location "Montréal, Canada · 2017"
```

With location and optional password:

```bash
python create_photo_page.py photos/murales/ https://photos.app.goo.gl/XFPP4BNU3p3FZJzc6 \
    --location "Montréal, Canada · 2017"

python create_photo_page.py photos/europe/ https://photos.app.goo.gl/J2FfnjQrz7tjE45P6 mysecretpassword \
    --location "Lille, France · 2014"
```

> **Year auto-detection:** omitting `--location` is fine on a first run — the script reads the year from Google Photos and prints a suggestion. The city/country must be typed manually.

### Arguments

| Argument | Description |
|---|---|
| `parent_dir/` | Parent folder — title and filename auto-derived from album |
| `album_url` | Google Photos share link |
| `password` | Plain-text password — SHA-256 hashed automatically |
| `--location` | Location · year shown under the title |
| `--description` | Description paragraph under the location |

### After running the script

1. Open the **parent category page** (e.g. `photos/usa.html`) and add a new card:
   - Album cards (leaf pages): `class="card"`
   - Folder cards (pages with sub-albums): `class="card card--category"` with meta `N albums · Name1, Name2…`
2. If new photos are added to an album later, re-run the same command to regenerate the page with fresh photo URLs.
3. Commit and push — live within ~60 seconds:

```bash
git add .
git commit -m "add Miami - Key West album"
git push
```

---

## Felix — Changing a page password

1. Run `generate_hash.py` to get the SHA-256 hash:
   ```bash
   python generate_hash.py
   # Enter password when prompted → prints hash + ready-to-paste <script> tag
   ```
2. Open the protected HTML file and replace the `data-hash` value in line 8:
   ```html
   <script src="/js/auth.js" data-hash="REPLACE_THIS" defer></script>
   ```
3. Commit and push — live within ~60 seconds.

> Pages that still use the demo password `password` — update before sharing with family:
> - `photos/europe/famille.html`
> - `photos/europe/lille-2014/lille-famille.html`
> - `photos/caraibes/punta-cana-famille-2010.html`

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
     <div class="card__body">
       <h3 class="card__title">Video Title</h3>
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
