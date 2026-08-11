# COMP 1350 — Web Administration

Labs, online activities (flipped material), and the group project for BCIT's COMP 1350, in the Computer Information Technology (CIT) diploma program. The course covers installing, configuring, securing, scaling, and monitoring web servers — Apache, Nginx, and IIS — across local VMs and remote hosts.

**Published site:** https://therealcodevoyage.github.io/COMP1350-WebAdmin/

## What is published here

| Published | Not published |
|---|---|
| 11 labs | Slides (`.pptx`) |
| 11 online activities (flipped material) | Quizzes (these contain answer keys) |
| Group project spec | Midterm and final exams |
| Course overview and learning outcomes | Internal planning documents |

Everything in the second column is excluded by [`.gitignore`](.gitignore) and is never tracked by git, so it cannot reach GitHub even though it sits in the same folder locally.

## Repository layout

```
.
├── Week-01/ ... Week-12/     Working source of truth (labs, online activities,
│                             and locally, the un-tracked slides and quizzes)
├── docs/                     The Jekyll site published by GitHub Pages
│   ├── _config.yml
│   ├── index.md              Homepage: labs, online activities, project index
│   ├── labs/                 Generated — do not edit by hand
│   ├── online-activities/    Generated — do not edit by hand
│   └── projects/             Generated — do not edit by hand
├── scripts/
│   └── sync-docs.py          Regenerates docs/ from the Week-XX folders
├── COMP1350_Group_Project.md Project spec (published)
└── .gitignore
```

Note that weeks 8, 13, and 14 have no folder: Week 8 is the midterm exam week, Week 14 is the final exam week, and Week 13 is course review and project presentations with no new material.

## Editing workflow

Edit lab and online-activity files in their `Week-XX/` folder — those are the originals. The copies under `docs/labs/`, `docs/online-activities/`, and `docs/projects/` are generated, so hand edits there get overwritten.

After any edit:

```bash
python3 scripts/sync-docs.py
git add -A
git commit -m "Update Lab 5"
git push
```

GitHub Pages rebuilds automatically, usually within a minute.

`sync-docs.py` publishes only the files listed explicitly at the top of the script — nothing is published by glob. It also refuses to run on any filename containing `quiz`, `test`, `exam`, `answer`, `solution`, or `midterm`, as a second line of defence behind `.gitignore`.

### Why generated pages are wrapped in `{% raw %}`

Course material contains shell, Nginx, and template syntax that can include double braces. Jekyll's Liquid template engine evaluates that syntax — including inside fenced code blocks — and would silently render those examples as empty strings. The sync script wraps each page body in `{% raw %}` to disable Liquid while leaving Markdown rendering intact.

## GitHub Pages setup

One-time configuration after pushing:

1. **Settings → Pages → Build and deployment**
2. **Source:** Deploy from a branch
3. **Branch:** `main`, folder: **`/docs`**

If you name the repository something other than `COMP1350-WebAdmin`, update `baseurl` in [`docs/_config.yml`](docs/_config.yml) to match — a mismatch makes the theme's CSS and all internal links 404.

## Before making the repository public

```bash
git status --ignored      # confirm quizzes/slides/exams appear under "Ignored files"
git ls-files              # confirm no quiz, exam, or .pptx file is listed
```

## Local preview (optional)

```bash
cd docs
bundle exec jekyll serve
```

Requires Ruby and the `github-pages` gem.

## License

Course materials are released under the [MIT License](LICENSE).
