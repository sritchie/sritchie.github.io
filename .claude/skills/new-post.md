---
name: new-post
description: Create a new blog post page bundle
user_invocable: true
---

# New Post

Create a new blog post as a Hugo page bundle.

## Steps

1. Ask the user for:
   - **Title** (required)
   - **Tags** (optional, comma-separated)
   - **Categories** (optional, from: programming, math-and-physics, adventure, projects, essays)
   - **Whether math is needed** (adds `math: true` to frontmatter)
   - **Series** (optional, for multi-part posts)

2. Generate a slug from the title (lowercase, hyphens, no special chars)

3. Create the page bundle directory: `content/posts/{slug}/`

4. Create `content/posts/{slug}/index.md` with frontmatter:
```yaml
---
title: "{title}"
date: {current ISO date}
slug: "{slug}"
tags: [{tags}]
categories: [{categories}]
math: {true if math needed}
series: ["{series}"]  # only if provided
draft: true
---
```

5. Report the file path and remind user to:
   - Drop images into the page bundle folder
   - Reference images with relative paths: `![alt](photo.jpg)`
   - Preview with `hugo server -D`
   - Remove `draft: true` when ready to publish
