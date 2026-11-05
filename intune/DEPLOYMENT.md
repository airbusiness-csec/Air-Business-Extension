# Deploying with Intune (self-hosted on GitHub)

Managed devices get Air Business XSLT Polyfill straight from this repository's GitHub Releases. An Intune Win32 app adds one entry to Edge's force-install policy; Edge then installs the signed extension and keeps it updated on its own. Staff do nothing.

```
Push to main with a new version
  → GitHub Actions builds, signs and publishes:
      air-business-xslt-polyfill.crx  (signed extension)
      updates.xml                     (latest version + .crx download link)
      air-business-xslt-polyfill.intunewin + -Detect.ps1  (Intune Win32 app, uploaded once by IT)
  → Edge on managed devices checks updates.xml every few hours and updates itself
```

Nothing in `intune/` ships in the release zip.

> **Why this only works on managed devices:** Edge on Windows only installs extensions from outside the Edge Add-ons store when told to by policy on a domain-joined or MDM-enrolled (Intune) device. Unmanaged PCs can still use the manual zip install in the README.

---

## 1. Create the signing key (once, ever)

The key signs every release and fixes the extension's ID. **Anyone with this key and the ability to publish could push code to every managed browser**, so treat it like a privileged credential.

> **Key already created.** Its extension ID is **`mmnheljcggbgjibghjangafmlajjnnag`**. Make sure the key is stored in the team password vault and the `CRX_PRIVATE_KEY` secret (step 2), and that no local copy remains. Only repeat the steps below if the key is ever lost or compromised; a new key means a new extension ID, so the Intune scripts would need updating and redeploying.

OpenSSL comes with Git for Windows; it just isn't on PowerShell's PATH. In PowerShell (the key goes in your user folder, which OneDrive doesn't sync; adjust the repository path if yours differs):

```powershell
$env:Path = "$env:LOCALAPPDATA\Programs\Git\mingw64\bin;$env:Path"   # this window only; use "C:\Program Files\Git\mingw64\bin" if Git is installed for all users
New-Item -ItemType Directory -Force "$env:USERPROFILE\crx-key" | Out-Null
Set-Location "$env:USERPROFILE\crx-key"
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out crx-key.pem
python "<path to repository>\scripts\pack_crx.py" --key crx-key.pem --print-id
```

The last command prints the **extension ID** (32 letters a–p). The ID isn't secret; it goes into the Intune scripts (step 3).

Then:

1. `notepad crx-key.pem`, copy everything (including the `BEGIN`/`END` lines) into the GitHub secret (step 2) and the team password vault.
2. Clear the clipboard and delete the local copy:
   ```powershell
   Set-Clipboard -Value ' '
   Set-Location $env:USERPROFILE
   Remove-Item -Recurse -Force "$env:USERPROFILE\crx-key"
   ```
3. If Windows clipboard history (**Win+V**) is on, delete the key from it too.

Never commit the key (`.gitignore` blocks `*.pem`) or paste it into chat, email or tickets.

---

## 2. Set up the GitHub "release" environment

The signing key lives in a GitHub *environment*, so only the release job can use it, and only after approval.

**Repository → Settings → Environments → New environment**, named `release`:

| Setting | Value |
| --- | --- |
| **Required reviewers** | You and one other person (e.g. the csec team). Every release waits for one of them to approve before it's signed and published. |
| **Prevent self-review** | On, if you have two reviewers. |
| **Deployment branches and tags** | *Selected branches*: `main` only. |
| **Environment secrets → Add secret** | Name `CRX_PRIVATE_KEY`; value: the entire contents of `crx-key.pem`, including the `BEGIN`/`END` lines. |

Also recommended, under **Settings → Branches → Add branch protection rule** for `main`: require a pull request with approval from code owners before merging. Otherwise anyone with write access could push straight to `main` and have it released.

---

## 3. Put the extension ID into the scripts

**Already done:** `Install.ps1`, `Uninstall.ps1` and `Detect.ps1` contain `mmnheljcggbgjibghjangafmlajjnnag`. If the key ever changes, update `$ExtensionId` in all three; the scripts refuse to run with an ID that isn't 32 letters a–p.

---

## 4. Publish the first release

Bump `"version"` in `manifest.json`, merge to `main` and approve the release when GitHub asks. Then check the release has `air-business-xslt-polyfill.crx`, `updates.xml`, `air-business-xslt-polyfill.intunewin` and `air-business-xslt-polyfill-Detect.ps1` attached, and that this link downloads the update file:

`https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/updates.xml`

Its `appid` must be `mmnheljcggbgjibghjangafmlajjnnag`.

---

## 5. Create the Intune Win32 app

### Download the package

GitHub builds the Intune package with every release; there's nothing to build yourself. From the [latest release](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest), download:

- [`air-business-xslt-polyfill.intunewin`](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill.intunewin): the Win32 app package;
- [`air-business-xslt-polyfill-Detect.ps1`](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill-Detect.ps1): the detection script;
- `SHA256SUMS`, to check the downloads.

Check the files before uploading. In PowerShell, in your Downloads folder:

```powershell
Get-FileHash .\air-business-xslt-polyfill.intunewin, .\air-business-xslt-polyfill-Detect.ps1 -Algorithm SHA256
Get-Content .\SHA256SUMS
```

The hashes must match the lines in `SHA256SUMS` (case doesn't matter). If they don't, don't upload; download again and, if they still differ, report it.

> The release workflow builds the package with Microsoft's Win32 Content Prep Tool, pinned to a specific version and checked against its SHA-256 and Microsoft's signature before it runs. To build it by hand instead: `IntuneWinAppUtil.exe -c intune -s Install.ps1 -o out -q`.

### Add it in Intune

**Intune admin centre → Apps → Windows → Add → Windows app (Win32)**, and upload `air-business-xslt-polyfill.intunewin`.

| Page | Setting | Value |
| --- | --- | --- |
| App information | Name | Air Business XSLT Polyfill |
| | Publisher | Air Business |
| | Logo | `icons/icon-128.png` |
| Program | Install command | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1` |
| | Uninstall command | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Uninstall.ps1` |
| | Install behaviour | **System** |
| | Device restart behaviour | No specific action |
| Requirements | Operating system | Windows 10 1809 or later (64-bit) |
| Detection rules | Rule format | **Use a custom detection script**: upload `air-business-xslt-polyfill-Detect.ps1` |
| | Run script as 32-bit process on 64-bit clients | No |
| | Enforce script signature check | No (or Yes if you sign the scripts) |
| Assignments | Required | A small pilot group first, then all staff |

The app only changes Edge policy, so it doesn't need updating for new extension versions. Edge fetches those itself. Every release includes a fresh `.intunewin`, but you only need to upload a new one to Intune if the release notes say the `intune/` scripts changed (for example, a new extension ID or update URL).

### Optional: pin the button to the toolbar

Separately in a **Settings catalog** policy (**Microsoft Edge → Extensions → Configure extension management settings**):

```json
{
  "mmnheljcggbgjibghjangafmlajjnnag": { "toolbar_state": "force_shown" }
}
```

This makes sure staff can see the red **ab** button for **Add this domain** and **Help**. It doesn't conflict with the Win32 app.

### Optional: switch off Developer mode for staff

With the extension delivered by Intune, staff no longer need Developer mode. Turning it off (**Microsoft Edge → Extensions → Control the availability of developer mode on the Extensions page → Don't allow**) stops unreviewed extensions being side-loaded. Check no other team relies on it first.

---

## Checking it worked

On a device in the assigned group, after Intune has synced:

1. `edge://policy` → **Reload policies**. `ExtensionInstallForcelist` should list `mmnheljcggbgjibghjangafmlajjnnag;https://github.com/...updates.xml` with **Status: OK**.
2. `edge://extensions`: **Air Business XSLT Polyfill** is listed as installed by your organisation, with the right version, and has no **Remove** button.
3. The install log is at `C:\ProgramData\Microsoft\IntuneManagementExtension\Logs\AirBusinessXsltPolyfill.log`.

Edge checks for updates every few hours. To check straight away, turn on Developer mode in `edge://extensions` and click **Update**; if Developer mode is switched off by policy, fully close and reopen Edge instead.

## Things to be aware of

- **Existing extension policies:** if Intune or Group Policy already sets *Control which extensions are installed silently* (`ExtensionInstallForcelist`) for other extensions, that policy may overwrite this app's entry. In that case, don't use the Win32 app; add `mmnheljcggbgjibghjangafmlajjnnag;https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/updates.xml` to the existing policy instead.
- **Staff who installed it manually** before the rollout will see two copies. They should remove the one with the Developer mode badge (see the README's Troubleshooting).
- **Google Chrome:** the same `.crx` and `updates.xml` work for Chrome's `ExtensionInstallForcelist` policy (under `SOFTWARE\Policies\Google\Chrome`) on managed devices, if needed later.
- **Rolling back:** releases can't be downgraded in place. To undo a bad release, publish a new, higher version with the fix.
