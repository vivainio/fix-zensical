# fix-zensical

Reading tools for [Zensical](https://zensical.org) sites: click-to-zoom Mermaid diagrams with a
full-screen view, full-screen tables, and Nav / TOC / Wide layout toggles.

Live demo (also the end-to-end test): https://vivainio.github.io/fix-zensical/

Link this document to your AI agent to fix your Zensical: [agent-quickstart.md](https://vivainio.github.io/fix-zensical/agent-quickstart.md)

```bash
uvx fix-zensical             # install/update in every zensical*.toml in ./
uvx fix-zensical --check     # change nothing; exit 1 if stale (for CI)
uvx fix-zensical --dry-run   # preview
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

To pin a version, use `uvx fix-zensical==0.1.0`. This repo's own
[docs workflow](.github/workflows/docs.yml) runs the tool from the repo source
(`uv run fix-zensical`) and publishes the demo site.

Notes:

- **`paths:` filter:** if your workflow only runs on some paths, the tool warns when the filter
  doesn't cover the installed files (`docs/assets/reading-tools/**`). Add that path, or changes
  to the tool's files won't trigger a build.
- **Comments in `zensical.toml`** are dropped when the tool rewrites the file. That doesn't matter
  in CI, where the result isn't committed. If you run it locally, don't commit the rewritten config.

Zensical renders Mermaid into a closed shadow root; the script patches `Element.prototype.attachShadow`
before diagrams render to reach the SVG.
