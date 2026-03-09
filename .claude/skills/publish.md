---
name: publish
description: Build, commit, and push to deploy the site
user_invocable: true
---

# Publish

Build the site, verify it, commit changes, and push to deploy.

## Steps

1. Run `hugo --gc --minify` to verify the build succeeds
2. Report any build warnings or errors
3. Run `git status` and `git diff --stat` to show what changed
4. Show a summary of new/modified content (posts, projects, etc.)
5. Ask the user for a commit message (suggest one based on changes)
6. Stage the relevant files and commit
7. Push to master: `git push origin master`
8. Confirm push succeeded — GitHub Actions will deploy automatically
