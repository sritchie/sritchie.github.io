#!/usr/bin/env python3
"""
Download all images from a Ghost blog and organize them into Hugo page bundles.

Reads images from:
  1. Ghost JSON export (HTML, mobiledoc, lexical, feature_image fields)
  2. Ghost Content API (live HTML with absolute URLs)

Downloads them and organizes into content/posts/{slug}/ directories.

Usage:
    python3 scripts/download_ghost_images.py
"""

import json
import os
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, unquote

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GHOST_URL = "https://sritchie.ghost.io"
CONTENT_API_KEY = "0594dccb8b3317a171427de454"
ADMIN_API_KEY = "69adc5eee241a60001baeae1:e48fde59f9f32dd04bbd86980845c3bc49f7cde02ccade62f95e18575302951c"

EXPORT_PATH = os.path.expanduser(
    "~/Downloads/sams-blog.ghost.2026-03-08-22-31-40.json"
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEMP_DIR = os.path.join(SCRIPT_DIR, "ghost_images")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content", "posts")

# Regex patterns for finding image paths in Ghost content
GHOST_IMG_RE = re.compile(
    r'(?:__GHOST_URL__|https?://sritchie\.ghost\.io)(/content/images/[^"\s\'\\)<>]+)'
)
EXTERNAL_IMG_RE = re.compile(
    r'(https?://[^"\s\'\\<>]+\.(?:jpg|jpeg|png|gif|svg|webp|avif|ico)(?:\?[^"\s\'\\<>]*)?)',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_ssl_context():
    """Create a permissive SSL context for downloads."""
    ctx = ssl.create_default_context()
    return ctx


SSL_CTX = make_ssl_context()


def download_file(url, dest, retries=1):
    """Download *url* to *dest*. Returns True on success."""
    for attempt in range(1 + retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
                with open(dest, "wb") as f:
                    shutil.copyfileobj(resp, f)
            return True
        except Exception as exc:
            if attempt < retries:
                time.sleep(1)
            else:
                print(f"  FAILED ({exc})")
                return False
    return False


def clean_image_path(raw_path):
    """Strip trailing punctuation that may have been captured by regex."""
    # Remove trailing ), ], ;, comma, etc.
    return raw_path.rstrip(")],;")


def image_filename(url_or_path):
    """Extract a clean filename from a URL or path."""
    parsed = urlparse(url_or_path)
    path = unquote(parsed.path)
    return os.path.basename(path).split("?")[0]


# ---------------------------------------------------------------------------
# Step 1: Read Ghost JSON export
# ---------------------------------------------------------------------------


def load_export(path):
    print(f"Reading Ghost export: {path}")
    with open(path) as f:
        data = json.load(f)
    posts = data["db"][0]["data"]["posts"]
    print(f"  Found {len(posts)} posts in export")
    return posts


# ---------------------------------------------------------------------------
# Step 2: Extract image URLs from export
# ---------------------------------------------------------------------------


def extract_images_from_export(posts):
    """Return dict mapping slug -> set of image URLs/paths."""
    slug_images = defaultdict(set)
    all_ghost_paths = set()
    all_external = set()

    for post in posts:
        slug = post.get("slug", "unknown")

        # Collect all text fields that might reference images
        text_sources = []
        for field in ("html", "mobiledoc", "lexical", "codeinjection_head", "codeinjection_foot"):
            val = post.get(field)
            if val:
                text_sources.append(val)

        # feature_image
        fi = post.get("feature_image")
        if fi:
            text_sources.append(fi)

        combined = "\n".join(text_sources)

        # Ghost-hosted images
        for match in GHOST_IMG_RE.findall(combined):
            clean = clean_image_path(match)
            slug_images[slug].add(("ghost", clean))
            all_ghost_paths.add(clean)

        # External images
        for match in EXTERNAL_IMG_RE.findall(combined):
            clean = clean_image_path(match)
            # Skip if it's actually a ghost URL (already captured above)
            if "sritchie.ghost.io" in clean:
                continue
            # Skip common non-image URLs that slip through
            if any(skip in clean for skip in (".css", ".js", "fonts.")):
                continue
            slug_images[slug].add(("external", clean))
            all_external.add(clean)

    print(f"  Ghost-hosted image paths: {len(all_ghost_paths)}")
    print(f"  External image URLs: {len(all_external)}")
    return slug_images


# ---------------------------------------------------------------------------
# Step 3: Discover images via Content API
# ---------------------------------------------------------------------------


def fetch_content_api_posts():
    """Fetch posts from the Ghost Content API and return them."""
    url = (
        f"{GHOST_URL}/ghost/api/content/posts/"
        f"?key={CONTENT_API_KEY}&limit=all&include=tags&formats=html"
    )
    print(f"Fetching posts from Content API...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode())
        api_posts = data.get("posts", [])
        print(f"  Got {len(api_posts)} posts from API")
        return api_posts
    except Exception as exc:
        print(f"  WARNING: Content API fetch failed: {exc}")
        return []


def merge_api_images(slug_images, api_posts):
    """Extract images from API posts and merge into slug_images."""
    new_count = 0
    for post in api_posts:
        slug = post.get("slug", "unknown")
        html = post.get("html") or ""
        fi = post.get("feature_image") or ""
        combined = html + "\n" + fi

        for match in GHOST_IMG_RE.findall(combined):
            clean = clean_image_path(match)
            key = ("ghost", clean)
            if key not in slug_images.get(slug, set()):
                slug_images[slug].add(key)
                new_count += 1

        for match in EXTERNAL_IMG_RE.findall(combined):
            clean = clean_image_path(match)
            if "sritchie.ghost.io" in clean:
                continue
            if any(skip in clean for skip in (".css", ".js", "fonts.")):
                continue
            key = ("external", clean)
            if key not in slug_images.get(slug, set()):
                slug_images[slug].add(key)
                new_count += 1

    print(f"  API added {new_count} new image references")
    return slug_images


# ---------------------------------------------------------------------------
# Step 4: Download images to temp directory
# ---------------------------------------------------------------------------


def download_all_images(slug_images):
    """Download all images to TEMP_DIR. Returns download stats."""
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Build a deduplicated download list: url -> local_path
    downloads = {}  # url -> temp_path
    url_for_ref = {}  # (kind, ref) -> url

    for slug, refs in slug_images.items():
        for kind, ref in refs:
            if kind == "ghost":
                url = GHOST_URL + ref
            else:
                url = ref
            if url in downloads:
                continue

            fname = image_filename(url)
            if not fname:
                continue

            # Use subdirectory matching Ghost's path structure to avoid name collisions
            if kind == "ghost":
                # ref looks like /content/images/2018/07/foo.jpg
                rel = ref.lstrip("/")  # content/images/2018/07/foo.jpg
                local_path = os.path.join(TEMP_DIR, rel)
            else:
                # For external images, put in external/ subdir
                safe = re.sub(r'[^\w./\-]', '_', urlparse(url).netloc + urlparse(url).path)
                local_path = os.path.join(TEMP_DIR, "external", safe)

            downloads[url] = local_path
            url_for_ref[(kind, ref)] = url

    total = len(downloads)
    print(f"\nDownloading {total} unique images...")

    success = 0
    failed = 0
    skipped = 0

    for i, (url, local_path) in enumerate(downloads.items(), 1):
        # Skip if already downloaded
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            skipped += 1
            if i % 50 == 0 or i == total:
                print(f"  [{i}/{total}] (cached) ...{url[-60:]}")
            success += 1
            continue

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        if i % 10 == 0 or i == 1 or i == total:
            print(f"  [{i}/{total}] {url[-80:]}")

        if download_file(url, local_path):
            success += 1
        else:
            failed += 1

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "skipped": skipped,
        "downloads": downloads,
        "url_for_ref": url_for_ref,
    }


# ---------------------------------------------------------------------------
# Step 5: Organize into Hugo page bundles
# ---------------------------------------------------------------------------


def organize_into_bundles(slug_images, stats):
    """Copy downloaded images into content/posts/{slug}/ directories."""
    downloads = stats["downloads"]
    url_for_ref = stats["url_for_ref"]

    bundles_created = 0
    images_copied = 0
    slugs_with_images = 0

    print(f"\nOrganizing images into page bundles under {CONTENT_DIR}/...")

    for slug, refs in sorted(slug_images.items()):
        if not refs:
            continue

        bundle_dir = os.path.join(CONTENT_DIR, slug)
        copied_for_slug = 0

        for kind, ref in refs:
            url = url_for_ref.get((kind, ref))
            if not url:
                continue
            src = downloads.get(url)
            if not src or not os.path.exists(src):
                continue

            # Determine destination filename
            fname = image_filename(url)
            if not fname:
                continue

            dest = os.path.join(bundle_dir, fname)

            # Skip if already exists and same size
            if os.path.exists(dest) and os.path.getsize(dest) == os.path.getsize(src):
                copied_for_slug += 1
                images_copied += 1
                continue

            os.makedirs(bundle_dir, exist_ok=True)
            shutil.copy2(src, dest)
            copied_for_slug += 1
            images_copied += 1

        if copied_for_slug > 0:
            slugs_with_images += 1
            if not os.path.exists(os.path.join(bundle_dir, "index.md")):
                bundles_created += 1

    return {
        "slugs_with_images": slugs_with_images,
        "bundles_created": bundles_created,
        "images_copied": images_copied,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("Ghost Image Downloader & Hugo Bundle Organizer")
    print("=" * 60)

    # 1. Load export
    if not os.path.exists(EXPORT_PATH):
        print(f"ERROR: Export file not found: {EXPORT_PATH}")
        sys.exit(1)
    posts = load_export(EXPORT_PATH)

    # 2. Extract images from export
    slug_images = extract_images_from_export(posts)

    # 3. Fetch from Content API and merge
    api_posts = fetch_content_api_posts()
    if api_posts:
        slug_images = merge_api_images(slug_images, api_posts)

    # Count totals
    all_refs = set()
    for refs in slug_images.values():
        all_refs.update(refs)
    print(f"\nTotal unique image references: {len(all_refs)}")

    # 4. Download
    dl_stats = download_all_images(slug_images)

    # 5. Organize into bundles
    bundle_stats = organize_into_bundles(slug_images, dl_stats)

    # 6. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total unique images found:    {dl_stats['total']}")
    print(f"  Successfully downloaded:      {dl_stats['success']}")
    print(f"  Already cached (skipped DL):  {dl_stats['skipped']}")
    print(f"  Failed downloads:             {dl_stats['failed']}")
    print(f"  Posts with images:            {bundle_stats['slugs_with_images']}")
    print(f"  Images copied to bundles:     {bundle_stats['images_copied']}")
    print(f"  Temp download dir:            {TEMP_DIR}")
    print(f"  Hugo content dir:             {CONTENT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
