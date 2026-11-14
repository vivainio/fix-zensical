# fix-zensical: agent quickstart

Adds reading tools to a [Zensical](https://zensical.org) site: click-to-zoom Mermaid diagrams
(full-screen view), full-screen tables, and Nav / TOC / Wide layout toggles.

Package: `fix-zensical` on PyPI. Python 3.11+, no dependencies. Run with `uvx`.

## What it does

For every `zensical.toml` and `zensical.<name>.toml` in the repo root it:

1. Copies `reading-tools.css` and `reading-tools.js` into `<docs_dir>/assets/reading-tools/`
   (`docs_dir` defaults to `docs`).
2. Appends `assets/reading-tools/reading-tools.css` to `extra_css` and
   `assets/reading-tools/reading-tools.js` to `extra_javascript`, keeping existing entries.
3. Warns if a `.github/workflows/*.yml` that mentions zensical has a `paths:` filter that does
   not cover the installed files.

It is idempotent: running it again changes nothing unless the assets are out of date.
The config is re-serialized, so comments in `zensical.toml` are not kept. Run it in CI, on the
runner's checkout, and do not commit the result.

## Use it in GitHub Actions

Run it before the build. Nothing needs to be committed.

```yaml
name: Documentation

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v6
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v7
      - run: uvx fix-zensical            # install reading tools
      - run: uvx fix-zensical --check    # fail if anything is still missing
      - run: uvx zensical build --clean
      - uses: actions/upload-pages-artifact@v5
        with:
          path: site
      - uses: actions/deploy-pages@v5
        id: deployment
```

Requirements: the repo's Pages source must be set to "GitHub Actions". Pin a version with
`uvx fix-zensical==0.1.0`.

## Mermaid must be enabled

The diagram features only apply to Mermaid blocks, which need this in `zensical.toml`:

```toml
[project.markdown_extensions.pymdownx.superfences]
custom_fences = [
  { name = "mermaid", class = "mermaid", format = "pymdownx.superfences.fence_code_format" },
]
```

## Options

| Command | Effect |
| --- | --- |
| `fix-zensical` | install/update in every `zensical*.toml` in `.` |
| `fix-zensical --repo PATH` | use PATH as the repository root |
| `fix-zensical --config FILE` | only these configs (repeatable) |
| `fix-zensical --shared DIR` | keep one copy in DIR, symlink each book's files to it |
| `fix-zensical --check` | change nothing; exit 1 if anything is missing or stale |
| `fix-zensical --dry-run` | show what would change |

Exit codes: `0` ok, `1` `--check` found problems, `2` no `zensical*.toml` found.

## Verify

After `zensical build`, `site/assets/reading-tools/` contains both files and the built pages
reference them.

Source and live demo: https://github.com/vivainio/fix-zensical ,
https://vivainio.github.io/fix-zensical/
