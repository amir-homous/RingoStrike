# Focus media: backgrounds and music (B31, #401)

The "Do it now" focus view shows a background image behind the timer and can play quiet music.
Adding an image or a track needs no code change: put the file in the right folder.

## Path folders

| Path key | Folder |
| --- | --- |
| `career` | `Work` |
| `creativity` | `Creative` |
| `fitness` | `Fitness` |
| `learning` | `Learning` |
| `sleep` | `Sleep` |

The challenge key is the challenge's icon key: the challenge name in lower case, with every run of
other characters turned into `-` (`challengeIconKey` in `frontend/src/lib/challengeIconKeys.js`).
For example "Deep Work 25" becomes `deep-work-25`.

## Background images (tracked in git)

Folder: `frontend/src/assets/focus-backgrounds/`. Images are bundled by Vite (`import.meta.glob`),
so a new image needs a rebuild.

Lookup order, first match wins:

1. `{Folder}/{challenge_key}.webp`
2. `{Folder}/default.webp`
3. `default.webp` (the root)
4. No image: the plain dark card.

`.webp` is preferred; `.png`, `.jpg` and `.jpeg` also work, in any letter case (for the same name the
order is webp, png, jpg, jpeg).

Current images: one `default.webp` in each of the five folders (Work, Learning, Sleep, Fitness,
Creative; 1376x768, 22 to 30 KB) and the root `default.webp` (1600x900) as the global fallback.
Credits are in `docs/MEDIA_CREDITS.md`.

Size: 16:9 or close (1600x900, 1376x768). The card is about 348x196 (362x204 on a phone) and crops
with `object-fit: cover`, so keep the subject in the middle. A file over 250 KB should be converted
to WebP (quality about 82); keep each file under about 80 KB. A dark scrim sits over the image so the
digits and buttons stay readable (aim for at least 4.5:1 for white text in the digits and buttons
areas).

## Music (NOT tracked in git)

Folder: `frontend/public/Musics/`. Audio files are ignored by `.gitignore` (mp3, ogg, m4a, wav);
only the folders (`.gitkeep`), this doc and the licences are in git.

Lookup order, first folder that has a track wins:

1. `Musics/{Folder}/{challenge_key}/*`
2. `Musics/{Folder}/*`
3. `Musics/Default*` (files in the root whose name starts with `Default`)
4. No track: no music, and the mute button is hidden.

Only `.mp3`, `.ogg`, `.m4a` and `.wav` are used; `.txt`, `README`, `.gitkeep` and anything else is
ignored. Several tracks in one folder play one after another; one track loops. Volume is 35 %.

How it is listed: the Vite plugin `frontend/vite/focusMusicManifest.js` scans `public/Musics` and
exposes the list as `virtual:focus-music`. In dev, adding or removing a file reloads the page. For
production the list is fixed at `npm run build`, so the files must be in `frontend/public/Musics/`
on the server **before** the build (the build copies them into `dist/Musics/`). A file copied
straight into `dist/Musics/` after the build is served but is not in the list, so it never plays.

Behaviour: the music starts right after the "Do it now" tap, Pause pauses it, Done, Cancel and
leaving the view stop it. Mute is remembered on this device (`localStorage`
`ringostrike_focus_music_muted`). If the browser blocks playback, or after a reload, the button shows
"Unmute music" and a tap starts it. A file that fails to load is skipped quietly.

### Deploy (VPS)

```bash
rsync -av frontend/public/Musics/ ringo@<vps>:/home/ringo/RingoStrike/frontend/public/Musics/
```

Then build on the server as usual. Current tracks: 1 file, 3.6 MB
(`Default_atlasaudio-chill-chill-music-507815.mp3`).

## Adding a file with a licence

1. Put the file in its folder (above).
2. Save the licence or download certificate in `docs/media-licenses/music/` (or
   `docs/media-licenses/images/`), named after the file.
3. Add a row to `docs/MEDIA_CREDITS.md`: file, folder, source URL, id, licence file, date.
4. Images: commit the image. Music: never `git add` the audio file; copy it to the server (above).
