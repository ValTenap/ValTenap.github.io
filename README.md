# Valeria Tena-Piñon — personal academic website

Built on the MIT-licensed [academic Jekyll theme](https://github.com/LeNPaul/academic) by Paul Le, with the layout of [mffg1993.github.io](https://mffg1993.github.io).

## Put it online (GitHub Pages)
1. On GitHub, create a **public** repository named exactly `YOUR-USERNAME.github.io`.
2. Upload everything in this folder (drag-and-drop on "Add file → Upload files", or `git push`).
3. Repo **Settings → Pages** → Source: *Deploy from a branch* → `main` / `(root)` → Save.
4. In a minute or two the site is live at `https://YOUR-USERNAME.github.io`.
5. Edit `_config.yml` and replace `ValTenap`.

## Where to edit things
| What | File |
|---|---|
| Name, tagline | `_config.yml` |
| Home page text (hero sentence, About me, the five curves) | `index.md` |
| Menu, research projects (cards + research page), footer links, contact info | `_data/settings.yml` |
| Publications | `_data/publications.yml` |
| CV sections | `_data/cv/*.yml` (an empty file hides its section) |
| News | `_posts/YYYY-MM-DD-title.md` |
| Images | `assets/img/` |
| Hero animation (q-plate vector beam) | `assets/js/beam.js` |

## Where the pictures come from
- `lloyd_mirror.jpg`: rendered with Blender from `_tools/lloyd_mirror.py` (`pip install bpy`, then `python _tools/lloyd_mirror.py out.png 1800 96`). `_tools/lloyd_mirror.blend` opens in Blender.
- `spaceplate_card.png`: `_tools/spaceplate_figure.py`.
- Steganography figures (curves, Stokes maps, setup, concept, q-plate): taken from the MSc thesis defense slides.

## Open TODOs
- APL Photonics DOI/volume in `_data/publications.yml`
- Profiles (ORCID, Scholar, LinkedIn) in `_data/settings.yml`
- Contact photo + office, TA course name, awards
