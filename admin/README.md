# Site Manager — Setup & User Guide

This tool lets you add photos, videos, and collections to your website from your browser, without using any code.

---

## One-Time Setup

These steps only need to be done once. Felix will help you with them.

### Step 1 — Install Python

1. Go to **python.org/downloads** and download the latest version for Windows.
2. Run the installer.
3. **Important:** on the first screen, tick the box that says **"Add Python to PATH"** before clicking Install.

### Step 2 — Install the required package

1. Open the **Start Menu** and search for **Command Prompt**. Click on it.
2. Type the following and press Enter:
   ```
   pip install flask
   ```
3. Wait for it to finish. You can close the window when it is done.

### Step 3 — Set up the website files

Felix will do this step for you (he sets up the website folder and connects it to GitHub).

---

## Daily Use

### To start the tool

1. Open the **`admin`** folder inside your website folder.
2. Double-click **`launch.bat`**.
3. A black window will open — leave it running. Your browser will open automatically.
4. Use the browser to add photos, videos, or collections.
5. When you are done, close the browser tab and close the black window.

> If your browser does not open automatically, wait a few seconds and then go to **http://localhost:5000** in your browser.

---

## What each page does

### Add a Photo Album
Use this to publish a Google Photos album to your website.

You will need:
- **The album's sharing link** — open the album in Google Photos, click the share button, and copy the link.
- **The location and year** — for example: `Florida, USA · 2018`

The album title is fetched automatically from Google Photos.

### Add a Video
Use this to publish a YouTube video to your website.

You will need:
- **The YouTube video ID** — open the video on YouTube. Look at the address bar. After `watch?v=` you will see a code made of 11 letters and numbers. That is the ID. For example: `dQw4w9WgXcQ`.
- **The location and year** — for example: `Australia · 1995`

The video title is fetched automatically from YouTube.

### Create a Collection
Use this to create a new folder that groups albums or videos together — for example, a new country, trip, or theme. Create the collection first, then add albums or videos to it.

### Generate a Password Code
Use this to get a security code when you want to password-protect a page. The website's standard password is **Claude** (with a capital C). Type the password here to get the code, then paste the code when creating the protected page.

---

## Troubleshooting

**The black window closes immediately when I double-click launch.bat**
- Python may not be installed, or may not be on the PATH. Redo Step 1 of the setup, making sure to tick "Add Python to PATH".

**The page says "Network error"**
- Make sure the black window is still open. If you closed it, double-click `launch.bat` again.

**I get an error message in the result box**
- Read the error message carefully. Common causes:
  - The Google Photos album is not shared publicly (the album must be set to "Anyone with the link").
  - The YouTube video ID is wrong (check that it is exactly 11 characters).
  - You chose the wrong collection for the page.
- If you are not sure, take a screenshot and send it to Felix.
