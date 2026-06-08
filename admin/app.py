import os
import re
import sys
import hashlib
import threading
import webbrowser
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates', static_folder='static')

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Collection scanning
# ---------------------------------------------------------------------------

def scan_collections(section=None):
    """Return existing collection pages as [{label, path, section}].

    'path' is a repo-relative directory path (forward slashes, trailing slash)
    suitable for passing as output_path to the create_* scripts in AUTO mode.
    """
    collections = []
    sections = ['photos', 'videos'] if section is None else [section]

    for sec in sections:
        root_file = 'index.html' if sec == 'photos' else 'videos.html'
        root_label = 'My Photos — top level' if sec == 'photos' else 'My Videos — top level'
        if (REPO_ROOT / root_file).exists():
            collections.append({'label': root_label, 'path': sec + '/', 'section': sec})

        sec_dir = REPO_ROOT / sec
        if not sec_dir.exists():
            continue

        for html_file in sorted(sec_dir.rglob('*.html')):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            # A collection page has a card grid but no photo/video embed.
            # Handles both hand-built pages (no <!-- /grid --> marker) and
            # script-created pages (which do have the marker).
            is_collection = (
                '<!-- /grid -->' in content
                or (
                    'class="grid"' in content
                    and 'pa-gallery-player-widget' not in content
                    and 'youtube.com/embed' not in content
                )
            )
            if not is_collection:
                continue

            m = re.search(r'<title>([^<]+)</title>', content)
            raw_title = m.group(1) if m else html_file.stem
            title = raw_title.split(' — ')[0].strip()

            rel = html_file.relative_to(REPO_ROOT)
            child_dir = (rel.parent / rel.stem).as_posix() + '/'
            label = f'{title}  ({child_dir})'
            collections.append({'label': label, 'path': child_dir, 'section': sec})

    return collections


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------

def run_script(cmd):
    """Run cmd with cwd=REPO_ROOT and return {output, success}."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            stdin=subprocess.DEVNULL,
            timeout=120,
        )
        output = result.stdout
        if result.stderr:
            output += ('\n--- stderr ---\n' if output else '') + result.stderr
        return {'output': output.strip() or '(no output)', 'success': result.returncode == 0}
    except subprocess.TimeoutExpired:
        return {'output': 'Error: Script timed out after 120 seconds.', 'success': False}
    except Exception as exc:
        return {'output': f'Error launching script: {exc}', 'success': False}


def _str(data, key):
    return (data.get(key) or '').strip()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/collections')
def api_collections():
    section = request.args.get('section') or None
    return jsonify(scan_collections(section))


@app.route('/photo', methods=['GET', 'POST'])
def photo():
    if request.method == 'POST':
        data = request.get_json()
        parent      = _str(data, 'parent')
        album_url   = _str(data, 'album_url')
        location    = _str(data, 'location')
        description = _str(data, 'description')
        password    = _str(data, 'password')
        thumbnail   = _str(data, 'thumbnail')
        position    = _str(data, 'position')

        cmd = [sys.executable, 'scripts/create_photo_page.py', parent, album_url,
               '--location', location]
        if description: cmd += ['--description', description]
        if password:    cmd += ['--password', password]
        if thumbnail:   cmd += ['--thumbnail', thumbnail]
        if position:    cmd += ['--position', position]

        return jsonify(run_script(cmd))

    return render_template('photo.html', collections=scan_collections('photos'))


@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        data = request.get_json()
        parent      = _str(data, 'parent')
        youtube_id  = _str(data, 'youtube_id')
        location    = _str(data, 'location')
        description = _str(data, 'description')
        password    = _str(data, 'password')
        position    = _str(data, 'position')

        cmd = [sys.executable, 'scripts/create_video_page.py', parent, youtube_id,
               '--location', location]
        if description: cmd += ['--description', description]
        if password:    cmd += ['--password', password]
        if position:    cmd += ['--position', position]

        return jsonify(run_script(cmd))

    return render_template('video.html', collections=scan_collections('videos'))


@app.route('/collection', methods=['GET', 'POST'])
def collection():
    if request.method == 'POST':
        data        = request.get_json()
        parent      = _str(data, 'parent')
        title       = _str(data, 'title')
        meta        = _str(data, 'meta')
        description = _str(data, 'description')
        thumbnail   = _str(data, 'thumbnail')
        youtube_id  = _str(data, 'youtube_id')
        position    = _str(data, 'position')

        # Default meta to avoid interactive prompt when left blank
        if not meta:
            meta = '0 videos' if parent.startswith('videos') else '0 albums'

        cmd = [sys.executable, 'scripts/create_collection_page.py', parent, title,
               '--meta', meta]
        if description: cmd += ['--description', description]
        if thumbnail:   cmd += ['--thumbnail', thumbnail]
        if youtube_id:  cmd += ['--youtube-id', youtube_id]
        if position:    cmd += ['--position', position]

        return jsonify(run_script(cmd))

    return render_template('collection.html', collections=scan_collections())


@app.route('/hash', methods=['GET', 'POST'])
def hash_page():
    if request.method == 'POST':
        data = request.get_json()
        password = _str(data, 'password')
        if not password:
            return jsonify({'hash': '', 'success': False,
                            'output': 'Please enter a password.'})
        h = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return jsonify({'hash': h, 'success': True, 'output': h})

    return render_template('hash.html')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    threading.Timer(1.2, lambda: webbrowser.open('http://localhost:5000')).start()
    app.run(debug=False, port=5000)
