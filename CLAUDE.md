# samritchie.io — Hugo Site

## Overview
Hugo site using PaperMod theme, deployed via GitHub Actions to GitHub Pages at samritchie.io. Custom typography (Literata), KaTeX math, sidenotes, dark mode, Pagefind search.

## Git Workflow
- **Never push directly to master** — always create a new branch and open a PR
- **Squash merges only** — always use `gh pr merge --squash`
- Deploy happens automatically when master is updated via GitHub Actions

## Architecture
- **Theme:** PaperMod at `themes/PaperMod/` — never edit theme files directly
- **Overrides:** Place in site-level `layouts/` or `assets/` to override theme
- **Page bundles:** All content uses page bundles (folder with `index.md` + co-located assets)
- **Images:** Committed to git in page bundles, referenced with relative paths
- **Analytics:** GoatCounter (`samritchie.goatcounter.com`)

## Content Structure
```
content/
  _index.md          # Home page
  about/index.md     # About page
  bookshelf/index.md # Book list
  posts/             # Blog posts (page bundles)
  projects/          # Project gallery (page bundles)
  racing/index.md    # Adventure Resume
  talks/_index.md    # Talks & presentations
  search/            # Pagefind search
  tags/              # Tag pages with Ghost redirect aliases
```

## Navigation (matches Ghost)
About | Blog Index | Bookshelf | Talks | Projects | Adventure Resume | Search

## Taxonomy
- **Categories** (broad): programming, math-and-physics, adventure, projects, essays
- **Tags** (fine-grained, from Ghost): clojure, haskell, sicmutils, ultrarunning, etc.
- **Series** (multi-part): for connected post sequences

## Permalinks
Posts use `/:slug/` to match old Ghost URLs for SEO continuity.

## Math
- Set `math: true` in frontmatter for posts with LaTeX
- `$$...$$` for display math, `$...$` for inline math
- Rendered via KaTeX

## Code
- Fenced code blocks with language identifier (e.g., ```clojure)
- Light theme (github style), `noClasses: false`

## Shortcodes Available
**From theme:** `youtube`, `figure`
**Custom:** `strava`, `substack-link`, `project-card`, `sidenote`, `marginnote`, `epigraph`

## External Links
- [Road to Reality Substack](https://roadtoreality.substack.com/) — linked, not migrated
- Newsletter via Buttondown (RSS-to-email) — TODO

## Build Commands
- `hugo server -D` — local preview with drafts
- `hugo --gc --minify` — production build
- Push to `master` to deploy via GitHub Actions

## Project Front Matter
```yaml
title: "Project Name"
description: "Short description"
project_url: "https://github.com/..."
status: "active"  # active | maintained | archived | completed
tech: ["Clojure", "ClojureScript"]
image: "screenshot.png"
weight: 1
group: "open-source"
```
