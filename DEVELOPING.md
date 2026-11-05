# Developer notes

Not shipped to end users. The end-user guide is `README.md` (generated into `README.html`).

## Files

| File | Purpose |
| --- | --- |
| `manifest.json` | Extension settings, including the built-in domains (`content_scripts` → `matches`) and the version |
| `background.js` | Registers the polyfill on the domains users have added |
| `scope.js` | Domain-matching code shared by the background script and popup |
| `popup.html`, `popup.js`, `popup.css` | The toolbar popup |
| `xslt-extension.js` | The content script. Generated from `content.js` + `xslt-polyfill.min.js` by `node scripts/bundle.mjs` |
| `README.md` → `README.html` | End-user guide, opened by the popup's Help button. `python scripts/build_readme_html.py` |
| `scripts/build_release.py` | Builds the release zip into `releases/` |

## Making a release

1. Bump `"version"` in `manifest.json`.
2. Add a row to **Version history** in `README.md`.
3. Run `python scripts/build_release.py` locally to check it builds, and commit.
4. Tag and push: `git tag v1.2.0` then `git push origin main v1.2.0` (the tag must match the manifest version).

GitHub Actions (`.github/workflows/release.yml`) then builds the zip and publishes a GitHub release with `air-business-xslt-polyfill.zip` attached. End users download it from:

`https://github.com/<owner>/<repo>/releases/latest/download/air-business-xslt-polyfill.zip`

`build_release.py` regenerates `README.html`, checks `xslt-extension.js` is up to date and every file the manifest refers to is present, then writes:

- `releases/air-business-xslt-polyfill-<version>.zip`: what end users install;
- `releases/air-business-xslt-polyfill-<version>.zip.sha256`: its SHA-256, so the zip can be verified.

It refuses to overwrite an existing version (use `--force` to rebuild an unreleased one). `releases/` is git-ignored; attach zips to a release instead of committing them.
