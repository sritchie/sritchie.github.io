---
name: new-project
description: Create a new project page bundle
user_invocable: true
---

# New Project

Create a new project entry in the portfolio gallery.

## Steps

1. Ask the user for:
   - **Title** (required)
   - **Description** (short, one line)
   - **Project URL** (GitHub, website, etc.)
   - **Status**: active, maintained, archived, or completed
   - **Tech stack** (comma-separated)
   - **Group**: open-source, applications, aviation, or writing
   - **Weight** (sort order within group, lower = first)

2. Generate a slug from the title

3. Create the page bundle: `content/projects/{slug}/`

4. Create `content/projects/{slug}/index.md` with frontmatter:
```yaml
---
title: "{title}"
description: "{description}"
project_url: "{url}"
status: "{status}"
tech: [{tech}]
image: ""
weight: {weight}
group: "{group}"
---
```

5. Remind user to add a screenshot or logo image to the page bundle folder and update the `image` field in frontmatter.
