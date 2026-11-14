# fix-zensical

Reading tools for [Zensical](https://zensical.org) sites. **This site is the demo and the
end-to-end test**: it is built by the same workflow that checks the tool, and the extras you
see here were registered by running `fix-zensical` before the build.

- **Click a diagram** to open it zoomed, full screen. See [Diagrams](diagrams.md).
- **Full-screen tables** for wide data. See [Tables](tables.md).
- **Nav / TOC / Wide toggles** for the page layout.

```bash
uvx fix-zensical             # install/update in every zensical*.toml
uvx fix-zensical --check     # exit 1 if stale (for CI)
```

!!! note
    `zensical.toml` in this repo has no `extra_css` / `extra_javascript` entries. The docs
    workflow adds them at build time.
