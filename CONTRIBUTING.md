# Contributing and maintenance notes

Technical notes for maintaining this repo. For what the site is, see the [README](README.md).

## Layout
Each published page is one folder at the repo root:

```
<YYYY-MM-DD>-<slug>/
  index.html      the page (self-contained)
  interactive/    a standalone interactive chart, when the page has one
  meta.json       title, date, lane, kind, description
```

`index.html` and `feed.xml` at the site root are generated from the `meta.json` files on every push; they are not committed.

## How pages get here
Pages are written and reviewed in a separate workspace and copied here only after they pass review and are approved. Nothing built from synthetic data is published. A withdrawn page leaves a short notice at its URL.

## Build locally
```
python3 scripts/build_site.py _site
python3 -m http.server -d _site 8000
```
Standard library only. Tests: `python3 -m pytest -q`.

## Workflows
| Workflow | Trigger | Purpose |
|---|---|---|
| `pages.yml` | Push to `main`, manual | Builds the index and feed, deploys to GitHub Pages |
| `ci.yml` | Pull request | Tests the site builder and lints commit messages |

## Commits and pull requests
Commits follow Conventional Commits (`type(scope): summary`), are atomic, and carry a body when the subject is not enough. Published pages use `feat(read): publish <folder>`; corrections use `fix(read): <folder> <what changed>`. Pull requests follow `.github/pull_request_template.md`.
