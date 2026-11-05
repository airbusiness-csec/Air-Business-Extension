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
| `scripts/pack_crx.py` | Signs the release zip as a `.crx` and writes `updates.xml` (used by the release workflow) |
| `intune/` | Intune Win32 app scripts (packaged into a `.intunewin` on every release by GitHub Actions) and deployment guide ([intune/DEPLOYMENT.md](intune/DEPLOYMENT.md)). Not shipped |

## Making a release

1. Bump `"version"` in `manifest.json`.
2. Run `python scripts/build_release.py` locally to check it builds.
3. Open a pull request into `main` and merge it once approved (`main` is protected).
4. Approve the release when GitHub asks (the `release` environment requires a reviewer).
5. Optionally, edit the release's notes on GitHub to describe what changed; staff see these on the releases page.

GitHub Actions (`.github/workflows/release.yml`) sees there's no release for the new version yet, builds the zip, signs it as a `.crx` with the `CRX_PRIVATE_KEY` secret, creates the `v<version>` tag and publishes a GitHub release with the zip, `.crx`, `updates.xml`, the Intune package (`.intunewin` + detection script, built on a Windows runner) and `SHA256SUMS` attached. Managed devices pick up the new version from `updates.xml` within a few hours. Pushes that don't change the version don't publish anything. If a build fails, fix it and push again (or re-run it from the Actions tab). Setup of the key, environment and Intune app: [intune/DEPLOYMENT.md](intune/DEPLOYMENT.md).

Manual installs download the zip from:

`https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill.zip`

`build_release.py` regenerates `README.html`, checks `xslt-extension.js` is up to date and every file the manifest refers to is present, then writes:

- `releases/air-business-xslt-polyfill-<version>.zip`: what end users install;
- `releases/air-business-xslt-polyfill-<version>.zip.sha256`: its SHA-256, so the zip can be verified.

It refuses to overwrite an existing version (use `--force` to rebuild an unreleased one). `releases/` is git-ignored; the workflow publishes the zip to GitHub Releases, so it's never committed.
