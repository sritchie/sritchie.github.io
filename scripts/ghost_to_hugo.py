#!/usr/bin/env python3
"""
Convert a Ghost JSON export to Hugo page bundles.

Usage:
    python3 scripts/ghost_to_hugo.py

Reads the Ghost export from ~/Downloads/sams-blog.ghost.2026-03-08-22-31-40.json
and creates Hugo page bundles under content/posts/{slug}/index.md.
"""

import json
import os
import re
import sys
from pathlib import Path

# --- Configuration ---

GHOST_EXPORT = os.path.expanduser(
    "~/Downloads/sams-blog.ghost.2026-03-08-22-31-40.json"
)
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "posts"
SKIP_SLUGS = {"about"}

# Category inference from tags
CATEGORY_TAG_MAP = {
    "programming": {
        "clojure", "haskell", "scala", "cascalog", "open-source", "emacs",
        "programming", "hadoop", "storm", "mapreduce", "coding", "summingbird",
        "algebird",
    },
    "math-and-physics": {
        "math", "physics", "proof", "sicmutils", "automatic-differentiation",
        "differential-geometry",
    },
    "adventure": {
        "ultrarunning", "climbing", "paddling", "race-report", "cycling",
        "leadville", "running", "adventure",
    },
    "projects": {"rv10", "windows", "airplane", "projects"},
    "essays": {"book-review", "stories", "meditation", "essay", "personal"},
}

LATEX_PATTERNS = ["$$", "\\(", "\\)", "\\[", "\\]", "\\begin{", "katex"]


def load_ghost_export(path):
    """Load and parse the Ghost JSON export."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    db = data["db"][0]["data"]
    return db["posts"], db["tags"], db["posts_tags"]


def build_tag_lookup(tags, posts_tags):
    """Build a dict mapping post_id -> sorted list of tag slugs."""
    tag_by_id = {t["id"]: t for t in tags}
    post_tags = {}
    for pt in posts_tags:
        pid = pt["post_id"]
        tid = pt["tag_id"]
        if tid in tag_by_id:
            post_tags.setdefault(pid, []).append(
                (pt["sort_order"], tag_by_id[tid]["slug"])
            )
    # Sort by sort_order and return just the slugs
    return {
        pid: [slug for _, slug in sorted(entries)]
        for pid, entries in post_tags.items()
    }


def infer_categories(tag_slugs):
    """Infer categories from tag slugs using the mapping."""
    tag_set = set(tag_slugs)
    categories = []
    for category, tag_names in CATEGORY_TAG_MAP.items():
        if tag_set & tag_names:
            categories.append(category)
    return sorted(categories)


def has_latex(html):
    """Check if HTML contains LaTeX patterns."""
    if not html:
        return False
    return any(pat in html for pat in LATEX_PATTERNS)


def extract_ghost_image_basename(url):
    """Extract basename from a Ghost-hosted image URL, or return None."""
    if not url:
        return None
    if "__GHOST_URL__/content/images/" in url:
        return os.path.basename(url)
    # Also handle full ghost URLs like https://example.com/content/images/...
    m = re.match(r"https?://[^/]+/content/images/.+", url)
    if m:
        return os.path.basename(url)
    return None


# --- HTML to Markdown conversion ---

def convert_youtube_iframes(html):
    """Convert YouTube iframes to Hugo shortcodes."""
    def replace_youtube(m):
        src = m.group(0)
        vid_match = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]+)", src)
        if vid_match:
            video_id = vid_match.group(1)
            return '{{< youtube "' + video_id + '" >}}'
        return src
    return re.sub(
        r'<iframe[^>]*youtube\.com/embed/[^>]*>(?:</iframe>)?',
        replace_youtube,
        html,
        flags=re.IGNORECASE,
    )


def convert_strava_iframes(html):
    """Convert Strava iframes to Hugo shortcodes."""
    def replace_strava(m):
        src = m.group(0)
        act_match = re.search(r"strava\.com/activities/(\d+)", src)
        if act_match:
            activity_id = act_match.group(1)
            return '{{< strava id="' + activity_id + '" >}}'
        return src
    return re.sub(
        r'<iframe[^>]*strava\.com/activities/[^>]*>(?:</iframe>)?',
        replace_strava,
        html,
        flags=re.IGNORECASE,
    )


def convert_figures(html):
    """Convert <figure> with <figcaption> to Hugo figure shortcodes."""
    def replace_figure(m):
        figure_html = m.group(0)
        # Extract image src
        img_match = re.search(r'<img[^>]*src="([^"]*)"', figure_html)
        caption_match = re.search(
            r"<figcaption>(.*?)</figcaption>", figure_html, re.DOTALL
        )
        if img_match:
            src = fix_ghost_image_ref(img_match.group(1))
            caption = ""
            if caption_match:
                # Strip HTML tags from caption
                caption = re.sub(r"<[^>]+>", "", caption_match.group(1)).strip()
            if caption:
                return '{{< figure src="' + src + '" caption="' + caption + '" >}}'
            else:
                return '{{< figure src="' + src + '" >}}'
        return figure_html

    return re.sub(
        r"<figure[^>]*>.*?</figure>", replace_figure, html, flags=re.DOTALL
    )


def fix_ghost_image_ref(src):
    """Convert __GHOST_URL__/content/images/... to just the filename."""
    if "__GHOST_URL__/content/images/" in src:
        return os.path.basename(src)
    return src


def fix_all_ghost_image_refs(html):
    """Fix all Ghost image references in HTML."""
    return re.sub(
        r"__GHOST_URL__/content/images/\d{4}/\d{2}/([^\s\"'<>]+)",
        r"\1",
        html,
    )


def convert_code_blocks(html):
    """Convert <pre><code> blocks to fenced markdown code blocks."""
    def replace_code(m):
        code_tag = m.group(1)
        content = m.group(2)
        # Try to detect language from class
        lang = ""
        lang_match = re.search(r'class="language-(\w+)"', code_tag)
        if lang_match:
            lang = lang_match.group(1)
        # Decode HTML entities in code
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&amp;", "&")
        content = content.replace("&quot;", '"')
        content = content.replace("&#39;", "'")
        # Remove trailing whitespace per line but keep structure
        content = content.strip()
        return "\n```" + lang + "\n" + content + "\n```\n"

    return re.sub(
        r"<pre><code([^>]*)>(.*?)</code></pre>",
        replace_code,
        html,
        flags=re.DOTALL,
    )


def convert_img_tags(html):
    """Convert standalone <img> tags (not inside figures) to markdown images."""
    def replace_img(m):
        full = m.group(0)
        src_match = re.search(r'src="([^"]*)"', full)
        alt_match = re.search(r'alt="([^"]*)"', full)
        if src_match:
            src = fix_ghost_image_ref(src_match.group(1))
            alt = alt_match.group(1) if alt_match else ""
            return "![" + alt + "](" + src + ")"
        return full

    return re.sub(r"<img[^>]*>", replace_img, html)


def fix_latex(text):
    r"""Fix LaTeX delimiters for Hugo/KaTeX.

    - Convert \(...\) to $...$
    - Convert \[...\] to $$...$$
    - Fix double-escaped backslashes: \\\\ -> \\
    """
    # Convert \(...\) to $...$  (inline math)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)
    # Convert \[...\] to $$...$$ (display math)
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    # Fix double-escaped backslashes
    text = text.replace("\\\\\\\\", "\\\\")
    return text


def basic_html_to_markdown(html):
    """Basic regex-based HTML to Markdown converter."""
    if not html:
        return ""

    text = html

    # Process shortcodes first (YouTube, Strava, figures)
    text = convert_youtube_iframes(text)
    text = convert_strava_iframes(text)
    text = convert_figures(text)
    text = convert_code_blocks(text)

    # Fix ghost image refs before converting img tags
    text = fix_all_ghost_image_refs(text)
    text = convert_img_tags(text)

    # Remove Ghost card markers
    text = re.sub(r"<!--kg-card-begin: \w+-->", "", text)
    text = re.sub(r"<!--kg-card-end: \w+-->", "", text)

    # Convert block-level elements
    # Headers
    for i in range(6, 0, -1):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m, level=i: "\n" + "#" * level + " " + m.group(1).strip() + "\n",
            text,
            flags=re.DOTALL,
        )

    # Blockquotes
    text = re.sub(
        r"<blockquote[^>]*>(.*?)</blockquote>",
        lambda m: "\n"
        + "\n".join(
            "> " + line
            for line in re.sub(r"</?p[^>]*>", "\n", m.group(1)).strip().split("\n")
            if line.strip()
        )
        + "\n",
        text,
        flags=re.DOTALL,
    )

    # Horizontal rules
    text = re.sub(r"<hr\s*/?>", "\n---\n", text)

    # Lists - handle <ul>/<ol> and <li>
    def convert_list(m):
        list_html = m.group(0)
        is_ordered = m.group(1).lower() == "ol"
        items = re.findall(r"<li[^>]*>(.*?)</li>", list_html, re.DOTALL)
        result = "\n"
        for i, item in enumerate(items):
            # Strip inner HTML tags for simple items
            item_text = re.sub(r"</?(?:p|br)[^>]*>", " ", item).strip()
            # Keep inline HTML (links, etc) but clean up
            if is_ordered:
                result += f"{i + 1}. {item_text}\n"
            else:
                result += f"- {item_text}\n"
        return result + "\n"

    text = re.sub(
        r"<(ul|ol)[^>]*>.*?</\1>", convert_list, text, flags=re.DOTALL | re.IGNORECASE
    )

    # Paragraphs
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\n\1\n", text, flags=re.DOTALL)

    # Line breaks
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Inline elements
    # Bold
    text = re.sub(r"<(?:strong|b)>(.*?)</(?:strong|b)>", r"**\1**", text, flags=re.DOTALL)
    # Italic
    text = re.sub(r"<(?:em|i)>(.*?)</(?:em|i)>", r"*\1*", text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r"<code>(.*?)</code>", r"`\1`", text, flags=re.DOTALL)
    # Links
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.DOTALL)

    # Remove remaining HTML tags that we haven't converted,
    # but preserve any raw HTML blocks that Hugo can render
    # (don't strip divs, iframes, etc. that might be intentional)
    # Only strip known safe-to-remove tags
    text = re.sub(r"</?(?:span|section|article|header|footer|main|nav)[^>]*>", "", text)

    # Clean up excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def html_to_markdown(html):
    """Convert HTML to Markdown, with optional html2text support."""
    try:
        import html2text
        h = html2text.HTML2Text()
        h.body_width = 0  # Don't wrap lines
        h.protect_links = True
        h.wrap_links = False
        h.unicode_snob = True

        # Pre-process: convert shortcodes before html2text
        processed = html
        processed = convert_youtube_iframes(processed)
        processed = convert_strava_iframes(processed)
        processed = convert_figures(processed)
        processed = convert_code_blocks(processed)
        processed = fix_all_ghost_image_refs(processed)

        # Remove Ghost card markers
        processed = re.sub(r"<!--kg-card-begin: \w+-->", "", processed)
        processed = re.sub(r"<!--kg-card-end: \w+-->", "", processed)

        text = h.handle(processed)
    except ImportError:
        text = basic_html_to_markdown(html)

    return text


def generate_frontmatter(post, tag_slugs):
    """Generate YAML frontmatter for a Hugo post."""
    title = post["title"] or "Untitled"
    # Escape quotes in title for YAML
    title_escaped = title.replace('"', '\\"')

    date = post.get("published_at") or post.get("created_at") or ""
    slug = post["slug"]
    is_draft = post["status"] != "published"

    categories = infer_categories(tag_slugs)
    description = post.get("custom_excerpt") or post.get("meta_description") or ""
    html = post.get("html") or ""
    math = has_latex(html)

    feature_image = post.get("feature_image") or ""
    image_basename = extract_ghost_image_basename(feature_image)

    lines = ["---"]
    lines.append(f'title: "{title_escaped}"')
    lines.append(f"date: {date}")
    lines.append(f"slug: {slug}")

    if is_draft:
        lines.append("draft: true")

    if tag_slugs:
        lines.append("tags:")
        for t in tag_slugs:
            lines.append(f"  - {t}")

    if categories:
        lines.append("categories:")
        for c in categories:
            lines.append(f"  - {c}")

    if description:
        desc_escaped = description.replace('"', '\\"')
        lines.append(f'description: "{desc_escaped}"')

    if math:
        lines.append("math: true")

    if image_basename:
        lines.append(f"image: {image_basename}")

    lines.append("---")
    return "\n".join(lines)


def process_post(post, tag_slugs):
    """Process a single post and return (path, content, metadata)."""
    slug = post["slug"]
    html = post.get("html") or ""

    # Generate frontmatter
    frontmatter = generate_frontmatter(post, tag_slugs)

    # Convert HTML to Markdown
    markdown = html_to_markdown(html)

    # Fix LaTeX if post has math
    if has_latex(html):
        markdown = fix_latex(markdown)

    content = frontmatter + "\n\n" + markdown + "\n"

    # Collect metadata for summary
    meta = {
        "slug": slug,
        "draft": post["status"] != "published",
        "math": has_latex(html),
        "has_images": bool(
            re.findall(r"__GHOST_URL__/content/images/", html)
        ) or bool(extract_ghost_image_basename(post.get("feature_image") or "")),
    }

    return content, meta


def main():
    print(f"Reading Ghost export from: {GHOST_EXPORT}")

    if not os.path.exists(GHOST_EXPORT):
        print(f"ERROR: Ghost export not found at {GHOST_EXPORT}")
        sys.exit(1)

    posts, tags, posts_tags = load_ghost_export(GHOST_EXPORT)
    tag_lookup = build_tag_lookup(tags, posts_tags)

    print(f"Found {len(posts)} posts, {len(tags)} tags")
    print(f"Output directory: {CONTENT_DIR}")
    print()

    # Ensure output directory exists
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {
        "converted": 0,
        "drafts": 0,
        "math": 0,
        "images": 0,
        "skipped": 0,
    }

    for post in posts:
        slug = post["slug"]

        if slug in SKIP_SLUGS:
            print(f"  SKIP: {slug}")
            stats["skipped"] += 1
            continue

        post_tag_slugs = tag_lookup.get(post["id"], [])
        content, meta = process_post(post, post_tag_slugs)

        # Create page bundle directory
        bundle_dir = CONTENT_DIR / slug
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # Write index.md
        index_path = bundle_dir / "index.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

        status = "DRAFT" if meta["draft"] else "OK"
        extras = []
        if meta["math"]:
            extras.append("math")
        if meta["has_images"]:
            extras.append("images")
        extra_str = f" [{', '.join(extras)}]" if extras else ""
        print(f"  {status}: {slug} (tags: {post_tag_slugs}){extra_str}")

        stats["converted"] += 1
        if meta["draft"]:
            stats["drafts"] += 1
        if meta["math"]:
            stats["math"] += 1
        if meta["has_images"]:
            stats["images"] += 1

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Posts converted: {stats['converted']}")
    print(f"  Drafts:          {stats['drafts']}")
    print(f"  Posts with math: {stats['math']}")
    print(f"  Posts with images: {stats['images']}")
    print(f"  Skipped:         {stats['skipped']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
