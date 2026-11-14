# fix-zensical

Reading tools for [Zensical](https://zensical.org) sites: click-to-zoom Mermaid diagrams with a
full-screen view, full-screen tables, and Nav / TOC / Wide layout toggles.

Live demo (also the end-to-end test): https://vivainio.github.io/fix-zensical/

```bash
uvx fix-zensical             # install/update in every zensical*.toml in ./
uvx fix-zensical --check     # change nothing; exit 1 if stale (for CI)
uvx fix-zensical --dry-run   # preview
uvx fix-zensical --shared docs-shared   # several books: one shared copy, per-file symlinks
```

It copies the files into `<docs_dir>/assets/reading-tools/` and appends them to `extra_css` /
`extra_javascript`, leaving other entries alone. Idempotent: rerun to update. Add the path to the
publish workflow's `paths:` filter if it warns. Requires the Zensical theme (`.md-typeset`,
`div.mermaid`).

## Use in a GitHub Actions workflow

Run it right before the build. It is idempotent and only touches the book's docs folder and
`zensical.toml` in the runner's checkout (nothing is committed), so you don't need to keep the
assets or the `extra_css` / `extra_javascript` entries in the repo.

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: astral-sh/setup-uv@v7
  - run: uvx fix-zensical          # add the reading tools
  - run: uvx fix-zensical --check  # optional: fail if anything is still missing
  - run: uvx zensical build --clean
```

Pin a version with `uvx fix-zensical==0.1.0`. This repo's own
[docs workflow](.github/workflows/docs.yml) does exactly this and publishes the demo site.

Tips:

- Several books in one repo: `uvx fix-zensical --shared docs-shared`.
- If the workflow has a `paths:` filter, the tool warns when it doesn't cover the installed files
  (`docs/assets/reading-tools/**`); add it so changes to them trigger a build.
- Because configs are re-serialized, comments in `zensical.toml` are not kept in the file it
  writes. That only matters if you run it locally and commit the result.

Zensical renders Mermaid into a closed shadow root; the script patches `Element.prototype.attachShadow`
before diagrams render to reach the SVG.
