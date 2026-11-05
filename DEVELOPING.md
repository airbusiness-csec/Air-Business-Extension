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
3. Run `python scripts/build_release.py` locally to check it builds.
4. Commit and push to `main`.

That's it. GitHub Actions (`.github/workflows/release.yml`) sees there's no release for the new version yet, builds the zip, creates the `v<version>` tag and publishes a GitHub release with `air-business-xslt-polyfill.zip` attached. Pushes that don't change the version don't publish anything. If a build fails, fix it and push again (or re-run it from the Actions tab). End users download it from:

`https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill.zip`

`build_release.py` regenerates `README.html`, checks `xslt-extension.js` is up to date and every file the manifest refers to is present, then writes:

- `releases/air-business-xslt-polyfill-<version>.zip`: what end users install;
- `releases/air-business-xslt-polyfill-<version>.zip.sha256`: its SHA-256, so the zip can be verified.

It refuses to overwrite an existing version (use `--force` to rebuild an unreleased one). `releases/` is git-ignored; the workflow publishes the zip to GitHub Releases, so it's never committed.
