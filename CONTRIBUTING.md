# Maintenance notes

Mostly notes to myself on how this repo works. If you're here to read, the [README](README.md) is the place to start.

## Layout
Each published page is one folder at the repo root:

```
<YYYY-MM-DD>-<slug>/
  index.html      the page (self-contained)
  hero.png        the post's image, for a short post
  interactive/    a standalone interactive chart, when the page has one
  meta.json       title, date, lane, kind, description
```

`index.html` and `feed.xml` at the site root are generated from the `meta.json` files on every push; they are not committed.

## How pages get here
I write and check each page somewhere else and copy it here once it's ready. Nothing made from placeholder data gets published. If I take a page down, I leave a short note at its URL.

## Build locally
```
python3 scripts/build_site.py _site
python3 -m http.server -d _site 8000
```
No dependencies. Tests: `python3 -m pytest -q`.

## Workflows
| Workflow | Trigger | Purpose |
|---|---|---|
| `pages.yml` | Push to `main`, manual | Builds the index and feed, deploys to GitHub Pages |
| `ci.yml` | Pull request | Tests the site builder and lints commit messages |

## Commits and pull requests
I use Conventional Commits (`type(scope): summary`), one change per commit, with a body when the subject doesn't say enough. New pages are `feat(read): publish <folder>`; corrections are `fix(read): <folder> <what changed>`. PRs use the template in `.github/`.
