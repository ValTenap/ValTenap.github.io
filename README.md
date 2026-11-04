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
| Name, tagline, home image | `_config.yml` |
| Home page text | `index.md` |
| Menu, research topics, footer icons, contact info | `_data/settings.yml` |
| Publications | `_data/publications.yml` |
| CV sections | `_data/cv/*.yml` (empty files hide their section) |
| News / updates | `_posts/YYYY-MM-DD-title.md` |
| Images | `assets/img/` |

The figures in `assets/img/` are placeholders made by `_tools/make_figures.py`; swap in your own lab photos or paper figures any time.

## Open TODOs
- GitHub username in `_config.yml`
- APL Photonics DOI/volume in `_data/publications.yml`
- Profiles (ORCID, Scholar, LinkedIn, GitHub) in `_data/settings.yml`
- Contact photo + office, TA course name, awards
