#!/usr/bin/env python3
"""Convert a Substack export to Hugo page bundles.

Usage:
    python3 scripts/substack_to_hugo.py

Reads the Substack export from ~/Downloads/cKOh8-syTkqtpHqEzrbGpA/ and creates
Hugo page bundles under content/posts/{slug}/index.md.
"""

import csv
import os
import re
import json
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SUBSTACK_EXPORT = os.path.expanduser("~/Downloads/cKOh8-syTkqtpHqEzrbGpA")
HUGO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(HUGO_ROOT, "content", "posts")

# ---------------------------------------------------------------------------
# Keyword-based tag/category inference
# ---------------------------------------------------------------------------

TAG_KEYWORDS = {
    "running": ["running", "race", "ultra", "marathon", "trail", "100k", "100m",
                 "leadville", "hardrock", "miwok", "endurance"],
    "music": ["music", "guitar", "piano", "song", "album", "instrument",
              "composition", "chord"],
    "programming": ["programming", "code", "lisp", "clojure", "emacs",
                    "software", "github", "functional"],
    "math": ["math", "algebra", "calculus", "theorem", "equation", "physics"],
    "writing": ["writing", "essay", "blog", "newsletter", "journal"],
    "cycling": ["bike", "cycling", "mountain bike", "vapor trail"],
    "strength-training": ["squat", "deadlift", "bench press", "strongman",
                          "lifting", "strength training", "barbell"],
    "philosophy": ["philosophy", "stoic", "memento mori", "meditation",
                   "mindfulness"],
    "family": ["twins", "daughter", "baby", "family", "kids"],
    "books": ["book", "reading", "read", "author"],
    "knitting": ["knitting", "knit"],
    "computing": ["computing", "universe", "simulation", "wolfram",
                  "cellular automata"],
}

CATEGORY_KEYWORDS = {
    "Endurance": ["running", "race", "ultra", "marathon", "trail", "cycling",
                  "bike", "ironman", "leadville", "hardrock", "endurance",
                  "strava"],
    "Technology": ["programming", "code", "lisp", "clojure", "emacs",
                   "software", "computing", "math", "algebra"],
    "Creative": ["music", "guitar", "writing", "knitting", "composition",
                 "instrument"],
    "Life": ["philosophy", "stoic", "family", "twins", "newsletter",
             "memento mori", "meditation"],
}


def infer_tags(text: str) -> list[str]:
    """Return tags based on keyword matches in the text."""
    lower = text.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            tags.append(tag)
    return sorted(tags)


def infer_categories(text: str) -> list[str]:
    """Return categories based on keyword matches in the text."""
    lower = text.lower()
    cats = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            cats.append(cat)
    return sorted(cats)


# ---------------------------------------------------------------------------
# HTML to Markdown conversion
# ---------------------------------------------------------------------------

def extract_youtube_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube-nocookie\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def extract_strava_id(url: str) -> str | None:
    """Extract Strava activity ID from URL."""
    m = re.search(r'strava\.com/activities/(\d+)', url)
    return m.group(1) if m else None


def html_to_markdown(html: str) -> str:
    """Convert Substack HTML to Markdown.

    Attempts to use html2text if installed, otherwise falls back to
    regex-based conversion.
    """
    # Pre-process: convert Substack-specific containers before main conversion
    html = preprocess_substack_html(html)

    try:
        import html2text
        converter = html2text.HTML2Text()
        converter.body_width = 0  # no line wrapping
        converter.protect_links = True
        converter.wrap_links = False
        converter.unicode_snob = True
        md = converter.handle(html)
    except ImportError:
        md = regex_html_to_markdown(html)

    # Post-process: convert remaining iframes/embeds to Hugo shortcodes
    md = postprocess_markdown(md)
    return md.strip() + "\n"


def preprocess_substack_html(html: str) -> str:
    """Handle Substack-specific HTML patterns before main conversion."""

    # Convert YouTube iframes to placeholder markers (survive html2text)
    def replace_youtube_iframe(m):
        src = m.group(0)
        vid = extract_youtube_id(src)
        if vid:
            return f'\n\n{{{{< youtube {vid} >}}}}\n\n'
        return m.group(0)

    html = re.sub(
        r'<div[^>]*class="youtube-wrap"[^>]*>.*?</div>\s*</div>',
        lambda m: replace_youtube_iframe(m),
        html,
        flags=re.DOTALL,
    )

    # Also catch bare YouTube iframes not in the wrapper div
    def replace_bare_youtube(m):
        vid = extract_youtube_id(m.group(0))
        if vid:
            return f'\n\n{{{{< youtube {vid} >}}}}\n\n'
        return m.group(0)

    html = re.sub(
        r'<iframe[^>]*youtube[^>]*>.*?</iframe>',
        replace_bare_youtube,
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Convert Strava iframes
    def replace_strava_iframe(m):
        sid = extract_strava_id(m.group(0))
        if sid:
            return f'\n\n{{{{< strava {sid} >}}}}\n\n'
        return m.group(0)

    html = re.sub(
        r'<iframe[^>]*strava[^>]*>.*?</iframe>',
        replace_strava_iframe,
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Unwrap captioned-image-container: extract img and figcaption
    def simplify_captioned_image(m):
        block = m.group(0)
        # Find the primary img src (the one on the <img> tag, not srcset)
        img_match = re.search(r'<img[^>]*\bsrc="([^"]*)"', block)
        alt_match = re.search(r'\balt="([^"]*)"', block)
        caption_match = re.search(
            r'<figcaption[^>]*>(.*?)</figcaption>', block, re.DOTALL
        )
        if img_match:
            src = img_match.group(1)
            alt = alt_match.group(1) if alt_match else ""
            result = f'<img src="{src}" alt="{alt}" />'
            if caption_match:
                caption = caption_match.group(1).strip()
                # Strip inner HTML tags from caption
                caption = re.sub(r'<[^>]+>', '', caption).strip()
                result += f"\n<p><em>{caption}</em></p>"
            return result
        return block

    html = re.sub(
        r'<div[^>]*class="captioned-image-container"[^>]*>.*?</div>\s*</figure>\s*</div>',
        simplify_captioned_image,
        html,
        flags=re.DOTALL,
    )

    # Remove Substack button/SVG noise
    html = re.sub(r'<button[^>]*>.*?</button>', '', html, flags=re.DOTALL)
    html = re.sub(r'<svg[^>]*>.*?</svg>', '', html, flags=re.DOTALL)

    return html


def postprocess_markdown(md: str) -> str:
    """Clean up Markdown after conversion."""
    # Collapse excessive blank lines
    md = re.sub(r'\n{4,}', '\n\n\n', md)

    # Clean up any leftover HTML iframe tags that weren't caught
    def replace_leftover_iframe(m):
        tag = m.group(0)
        vid = extract_youtube_id(tag)
        if vid:
            return f'{{{{< youtube {vid} >}}}}'
        sid = extract_strava_id(tag)
        if sid:
            return f'{{{{< strava {sid} >}}}}'
        # Preserve as HTML comment if we can't convert
        src_match = re.search(r'src="([^"]*)"', tag)
        if src_match:
            return f'<!-- iframe: {src_match.group(1)} -->'
        return ''

    md = re.sub(r'<iframe[^>]*>.*?</iframe>', replace_leftover_iframe,
                md, flags=re.DOTALL | re.IGNORECASE)

    return md


def regex_html_to_markdown(html: str) -> str:
    """Fallback regex-based HTML to Markdown conversion."""
    text = html

    # Headers
    for i in range(6, 0, -1):
        text = re.sub(
            rf'<h{i}[^>]*>(.*?)</h{i}>',
            lambda m, lvl=i: f'\n\n{"#" * lvl} {m.group(1).strip()}\n\n',
            text, flags=re.DOTALL
        )

    # Bold / italic / emphasis
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)

    # Links
    text = re.sub(
        r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        r'[\2](\1)',
        text, flags=re.DOTALL
    )

    # Images
    def img_replace(m):
        tag = m.group(0)
        src_m = re.search(r'src="([^"]*)"', tag)
        alt_m = re.search(r'alt="([^"]*)"', tag)
        src = src_m.group(1) if src_m else ""
        alt = alt_m.group(1) if alt_m else ""
        return f'![{alt}]({src})'

    text = re.sub(r'<img[^>]*/?\s*>', img_replace, text, flags=re.DOTALL)

    # Lists
    text = re.sub(r'<li[^>]*>\s*<p>(.*?)</p>\s*</li>',
                  r'\n- \1', text, flags=re.DOTALL)
    text = re.sub(r'<li[^>]*>(.*?)</li>',
                  r'\n- \1', text, flags=re.DOTALL)
    text = re.sub(r'</?[uo]l[^>]*>', '', text)

    # Paragraphs and line breaks
    text = re.sub(r'<p[^>]*>(.*?)</p>',
                  lambda m: f'\n\n{m.group(1).strip()}\n\n',
                  text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)

    # Blockquotes
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>',
                  lambda m: '\n' + '\n'.join(
                      '> ' + line for line in m.group(1).strip().split('\n')
                  ) + '\n',
                  text, flags=re.DOTALL)

    # Horizontal rules
    text = re.sub(r'<hr[^>]*/?\s*>', '\n\n---\n\n', text)

    # Protect Hugo shortcodes from tag stripping
    shortcode_placeholder = {}
    def save_shortcode(m):
        key = f"__SHORTCODE_{len(shortcode_placeholder)}__"
        shortcode_placeholder[key] = m.group(0)
        return key
    text = re.sub(r'\{\{<.*?>}}', save_shortcode, text)

    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Restore Hugo shortcodes
    for key, val in shortcode_placeholder.items():
        text = text.replace(key, val)

    # Decode common HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')

    return text


# ---------------------------------------------------------------------------
# Frontmatter generation
# ---------------------------------------------------------------------------

def make_frontmatter(title: str, date: str, slug: str, subtitle: str,
                     draft: bool, tags: list[str],
                     categories: list[str]) -> str:
    """Generate YAML frontmatter for a Hugo post."""
    lines = ["---"]
    # Escape quotes in title
    safe_title = title.replace('"', '\\"')
    lines.append(f'title: "{safe_title}"')
    if date:
        lines.append(f"date: {date}")
    lines.append(f"slug: {slug}")
    if draft:
        lines.append("draft: true")
    if subtitle:
        safe_sub = subtitle.replace('"', '\\"')
        lines.append(f'subtitle: "{safe_sub}"')
    lines.append('source: "substack"')
    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f"  - {t}")
    if categories:
        lines.append("categories:")
        for c in categories:
            lines.append(f"  - {c}")
    lines.append("---")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main conversion logic
# ---------------------------------------------------------------------------

def read_posts_csv(export_dir: str) -> list[dict]:
    """Read the Substack posts.csv and return list of post metadata dicts."""
    csv_path = os.path.join(export_dir, "posts.csv")
    posts = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
    return posts


def find_html_file(posts_dir: str, post_id_slug: str) -> str | None:
    """Find the HTML file for a given post_id field (e.g. '134293809.the-road-to...')."""
    # The post_id field in CSV is already the filename stem
    html_path = os.path.join(posts_dir, f"{post_id_slug}.html")
    if os.path.isfile(html_path):
        return html_path
    return None


def parse_post_id_slug(post_id_field: str) -> tuple[str, str]:
    """Parse the post_id CSV field into (numeric_id, slug).

    The field looks like: '134293809.the-road-to-the-hardrock-100'
    """
    dot_idx = post_id_field.index(".")
    numeric_id = post_id_field[:dot_idx]
    slug = post_id_field[dot_idx + 1:]
    return numeric_id, slug


def get_existing_slugs(content_dir: str) -> set[str]:
    """Return set of slugs that already exist in content/posts/."""
    slugs = set()
    if not os.path.isdir(content_dir):
        return slugs
    for entry in os.listdir(content_dir):
        entry_path = os.path.join(content_dir, entry)
        # Page bundles are directories containing index.md
        if os.path.isdir(entry_path):
            if os.path.isfile(os.path.join(entry_path, "index.md")):
                slugs.add(entry)
    return slugs


def main():
    posts_dir = os.path.join(SUBSTACK_EXPORT, "posts")
    posts = read_posts_csv(SUBSTACK_EXPORT)
    existing_slugs = get_existing_slugs(CONTENT_DIR)

    stats = {
        "converted": 0,
        "drafts": 0,
        "skipped_duplicate": 0,
        "skipped_no_html": 0,
        "skipped_no_title": 0,
    }

    print(f"Found {len(posts)} entries in posts.csv")
    print(f"Found {len(existing_slugs)} existing post slugs in {CONTENT_DIR}")
    print()

    for row in posts:
        post_id_field = row.get("post_id", "").strip()
        title = row.get("title", "").strip()
        subtitle = row.get("subtitle", "").strip()
        post_date = row.get("post_date", "").strip()
        is_published = row.get("is_published", "").strip().lower() == "true"

        if not post_id_field or "." not in post_id_field:
            continue

        # Parse ID and slug
        try:
            numeric_id, slug = parse_post_id_slug(post_id_field)
        except (ValueError, IndexError):
            print(f"  WARN: Cannot parse post_id: {post_id_field}")
            continue

        # Skip posts with empty titles -- mark as draft anyway if we proceed
        if not title:
            stats["skipped_no_title"] += 1
            if not is_published:
                # Skip entirely: unpublished + no title
                print(f"  SKIP (no title, unpublished): {post_id_field}")
                continue
            # Published but no title is weird; skip
            print(f"  SKIP (no title): {post_id_field}")
            continue

        # Find matching HTML file
        html_file = find_html_file(posts_dir, post_id_field)
        if not html_file:
            stats["skipped_no_html"] += 1
            print(f"  SKIP (no HTML file): {slug}")
            continue

        # Check for duplicates against existing Ghost content
        if slug in existing_slugs:
            stats["skipped_duplicate"] += 1
            print(f"  WARN: Duplicate slug '{slug}' -- Ghost version exists, skipping Substack version")
            continue

        # Read HTML
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Convert HTML to Markdown
        md_body = html_to_markdown(html_content)

        # Determine draft status
        draft = not is_published

        # Infer tags and categories from title + subtitle + body
        text_for_inference = f"{title} {subtitle} {md_body}"
        tags = infer_tags(text_for_inference)
        categories = infer_categories(text_for_inference)

        # Generate frontmatter
        frontmatter = make_frontmatter(
            title=title,
            date=post_date,
            slug=slug,
            subtitle=subtitle,
            draft=draft,
            tags=tags,
            categories=categories,
        )

        # Create page bundle
        bundle_dir = os.path.join(CONTENT_DIR, slug)
        os.makedirs(bundle_dir, exist_ok=True)

        index_path = os.path.join(bundle_dir, "index.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write("\n")
            f.write(md_body)

        status = "DRAFT" if draft else "OK"
        print(f"  [{status}] {slug} -- \"{title}\"")

        stats["converted"] += 1
        if draft:
            stats["drafts"] += 1

    # Summary
    print()
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"  Posts converted:        {stats['converted']}")
    print(f"    of which drafts:      {stats['drafts']}")
    print(f"  Skipped (duplicate):    {stats['skipped_duplicate']}")
    print(f"  Skipped (no HTML):      {stats['skipped_no_html']}")
    print(f"  Skipped (no title):     {stats['skipped_no_title']}")
    print(f"  Total entries in CSV:   {len(posts)}")


if __name__ == "__main__":
    main()
