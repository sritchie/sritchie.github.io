# samritchie.io — Hugo Site

## Overview
Hugo site using hugo-tufte theme (loikein fork), deployed via GitHub Actions to GitHub Pages at samritchie.io. Tufte CSS-inspired, text-forward design with beautiful typography, sidenotes, and margin notes.

## Architecture
- **Theme:** Git submodule at `themes/hugo-tufte/` — never edit theme files directly
- **Overrides:** Place in site-level `layouts/` or `assets/` to override theme
- **Page bundles:** All content uses page bundles (folder with `index.md` + co-located assets)
- **Images:** Committed to git in page bundles, referenced with relative paths

## Content Structure
```
content/
  _index.md          # Home page
  about/index.md     # About page
  posts/             # Blog posts (page bundles)
  projects/          # Project gallery (page bundles)
  talks/             # Talks & presentations
```

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
**From theme:** `youtube`, `figure`, `sidenote`, `marginnote`, `epigraph`, `newthought`, `blockquote`, `section`, `cols`, `div`, `cite`, `button`, `tag`
**Custom:** `strava`, `substack-link`, `project-card`

## External Links
- [Road to Reality Substack](https://roadtoreality.substack.com/) — linked, not migrated
- Newsletter via Buttondown (RSS-to-email)

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
