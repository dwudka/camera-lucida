# camera-lucida

Long reads and interactive charts on AI and healthcare economics, built from public data.

Site: <https://dwudka.github.io/camera-lucida/>

The name comes from the camera lucida, the drawing aid Santiago Ramón y Cajal used to trace what he saw through the microscope onto paper. This repo holds the finished drawings; the working material lives elsewhere.

Views are my own and do not represent my employer.

## What is here
Each published page is one folder at the repo root:

```
<YYYY-MM-DD>-<slug>/
  index.html      the page (self-contained)
  interactive/    a standalone interactive chart, when the page has one
  meta.json       title, date, lane, kind, description
```

`index.html` and `feed.xml` at the site root are generated from the `meta.json` files on every push; they are not committed.

## How pages get here
Pages are written and reviewed in a private workspace. A page is copied here only after it passes an adversarial review (number provenance, source checks, method checks) and is approved. Nothing built from synthetic data is published.

- All data is public: CMS public use files, the Federal Register, published research. Each page lists its sources and how its numbers were computed.
- Corrections are never silent. A factual fix adds a dated line to the corrections log at the bottom of the page.
- A withdrawn page leaves a short notice at its URL.

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

## Contributing
Commits follow Conventional Commits (`type(scope): summary`), are atomic, and carry a body when the subject is not enough. Published pages use `feat(read): publish <folder>`; corrections use `fix(read): <folder> <what changed>`. Pull requests follow `.github/pull_request_template.md`.
