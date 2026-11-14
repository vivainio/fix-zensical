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

Zensical renders Mermaid into a closed shadow root; the script patches `Element.prototype.attachShadow`
before diagrams render to reach the SVG.
