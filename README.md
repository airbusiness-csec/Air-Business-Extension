# Air Business XSLT Polyfill

Air Business XSLT Polyfill is a browser extension for Microsoft Edge and Google Chrome. It keeps Air Business web systems that use XML and XSLT displaying correctly as browsers withdraw built-in support for that technology.

This guide explains why the extension is needed, the two ways to install it, and how to use it.

---

## Why is this needed?

Some Air Business systems deliver pages as XML documents, which the browser converts into a readable page using an XSLT stylesheet. Browsers have done this conversion themselves for many years.

Google and Microsoft are removing XSLT support from Chrome and Edge. Microsoft lists the change on its [site-impacting changes page](https://learn.microsoft.com/microsoft-edge/web-platform/site-impacting-changes?tabs=latest). Once it has been removed, affected pages show raw code or a blank screen instead of their normal content. Until then, Edge shows a red warning banner at the top of these pages.

This extension restores the conversion inside the browser, so affected pages continue to display exactly as before. No changes are needed to the Air Business systems themselves.

---

## Choosing an installation method

There are two ways to install the extension. Most organisations should use Option A.

| | Option A: Managed deployment (Microsoft Intune) | Option B: Manual installation (browser add-on) |
| --- | --- | --- |
| **Best for** | Organisations with Intune-managed Windows devices | Individual users, or devices not managed by Intune |
| **Who installs it** | Your IT administrator, once, for all users | Each user, on their own computer |
| **Browsers** | Microsoft Edge | Microsoft Edge or Google Chrome |
| **Operating systems** | Windows 10 and 11 | Windows or macOS |
| **Updates** | Automatic | Manual, by downloading each new version |
| **User action needed** | None | About five minutes per computer |
| **Requirements** | Microsoft Intune; devices enrolled in Intune | Browser "Developer mode" must be allowed on the device |

---

## Option A: Managed deployment with Microsoft Intune

*For IT administrators.*

The extension is distributed as a Win32 app for Microsoft Intune. The app adds the extension to Microsoft Edge's managed-extension policy. Edge then installs the signed extension directly from this project's official releases and keeps it up to date automatically. Users don't need to do anything, and they can't remove or disable the extension.

### What you need

- Microsoft Intune, with permission to add and assign Windows apps.
- Windows 10 (1809 or later) or Windows 11 devices enrolled in Intune.
- Microsoft Edge on those devices.

### Steps

1. From the [latest release](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest), download `air-business-xslt-polyfill.intunewin`, `air-business-xslt-polyfill-Detect.ps1` and `SHA256SUMS`.
2. Check the downloads against `SHA256SUMS`. In PowerShell, run `Get-FileHash <file> -Algorithm SHA256` for each file and compare the result with the matching line. Don't continue if they differ.
3. In the Intune admin centre, go to **Apps → Windows → Add → Windows app (Win32)** and upload `air-business-xslt-polyfill.intunewin`.
4. Set the install command to `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1`, the uninstall command to `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Uninstall.ps1`, and the install behaviour to **System**.
5. Under **Detection rules**, choose **Use a custom detection script**, upload `air-business-xslt-polyfill-Detect.ps1`, and set **Run script as 32-bit process on 64-bit clients** to **No**.
6. Assign the app as **Required** to a small pilot group, confirm it works, then assign it to all users who need it.

The [full deployment guide](https://github.com/airbusiness-csec/Air-Business-Extension/blob/main/intune/DEPLOYMENT.md) covers every setting, verification on a test device, optional settings such as pinning the button to the toolbar, and removal.

> **Already managing Edge extensions through Intune or Group Policy?** If you already use the *Control which extensions are installed silently* policy, add `mmnheljcggbgjibghjangafmlajjnnag;https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/updates.xml` to your existing policy instead of deploying the Win32 app. This avoids two policies overwriting each other.

### Updates

New versions are installed automatically. Edge checks for updates every few hours. You only need to upload a new Intune package if a release's notes say the deployment scripts have changed.

---

## Option B: Manual installation

*For individual users.*

### Before you start

**[Download the latest version (zip file)](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill.zip)**

1. Save the zip file somewhere permanent, such as your **Documents** folder.
2. Right-click the zip file and choose **Extract All…**, then **Extract**.
3. Leave the extracted folder where it is. The browser loads the extension from this folder each time it starts, so **don't move, rename or delete it**.

> **If your Documents folder is in OneDrive:** right-click the extracted folder and choose **Always keep on this device**. Otherwise the extension may stop working when OneDrive frees up space.

### Microsoft Edge

1. Type `edge://extensions` into the address bar and press **Enter**.
2. Turn on **Developer mode**. The switch is near the bottom of the left-hand panel; in a narrow window, open the menu at the top left first.
3. Click **Load unpacked**, at the top right under **Installed extensions**.
4. Select the extracted folder (the one containing `manifest.json`) and click **Select Folder**.
5. **Air Business XSLT Polyfill** now appears in your list of extensions.

![The Edge extensions page, with the Developer mode switch circled in red at the bottom of the left-hand panel, the Load unpacked button at the top right, and Air Business XSLT Polyfill listed and switched on](docs/edge-developer-mode.png)

*The Edge extensions page after installation: **Developer mode** is circled in red, **Load unpacked** is at the top right, and **Air Business XSLT Polyfill** is listed and switched on.*

### Google Chrome

1. Type `chrome://extensions` into the address bar and press **Enter**.
2. Turn on **Developer mode** (the switch at the top right).
3. Click **Load unpacked**.
4. Select the extracted folder (the one containing `manifest.json`) and click **Select Folder**.
5. **Air Business XSLT Polyfill** now appears in your list of extensions.

### Pin the extension to your toolbar

1. Click the **Extensions** button (the jigsaw-piece icon) next to the address bar.
2. Click the pin icon (Chrome) or eye icon (Edge) next to **Air Business XSLT Polyfill**.

The red **ab** button now appears next to the address bar.

> **Can't find Developer mode or Load unpacked?** Your organisation may have disabled them. Ask your IT team about deploying the extension using Option A.

### Updates

1. [Download the latest version](https://github.com/airbusiness-csec/Air-Business-Extension/releases/latest/download/air-business-xslt-polyfill.zip) and extract it.
2. Replace the contents of your existing extension folder with the new files, keeping the folder in the same place.
3. Go to `edge://extensions` or `chrome://extensions` and click **Reload** (the circular arrow) on **Air Business XSLT Polyfill**.
4. Click the red **ab** button and check the version shown under **About**.

Any sites you've added are kept when you update.

---

## Using the extension

### Air Business sites

The extension works automatically on:

- `airbusiness.com` and all its subdomains
- `onadvantagecs.com` and all its subdomains

No setup is needed. Clicking the red **ab** button on one of these sites shows **Included by default**:

![The extension's pop-up on www.airbusiness.com, showing "Included by default in this extension", the list of built-in domains, an empty "Domains you've added" list and the About section](docs/popup.png)

### Adding another site

If a page on another site shows raw code or a blank screen, you can enable the extension for that site:

1. Go to the affected page.
2. Click the red **ab** button next to the address bar. If it isn't visible, click the jigsaw-piece **Extensions** button first.
3. Click **Add this domain**.
4. When your browser asks for permission, click **Allow**.

The page reloads and displays correctly. The extension remembers the site from then on.

### Removing a site

Click the red **ab** button, then either click **Remove this domain** while on that site, or click **Remove** next to the site under **Domains you've added**. The built-in Air Business sites can't be removed.

### Help

Click **Help** at the top of the extension's pop-up to open this guide at any time.

---

## Privacy and security

- **Limited reach:** the extension only runs on the Air Business sites listed above and on sites you choose to add. Each added site requires your explicit permission.
- **XML pages only:** normal web pages are left untouched.
- **No data collection:** the extension doesn't collect, store or transmit any personal or browsing information. All processing happens locally in your browser.
- **Same-site only:** when converting a page, the extension only loads files from that page's own website.
- **Signed and verifiable:** managed installations are cryptographically signed, so Edge only accepts official releases. Every release publishes SHA-256 checksums so downloads can be verified.
- **Reviewed releases:** every change is reviewed before release, and each release requires approval before it's published.

---

## Troubleshooting

| Problem | What to try |
| --- | --- |
| A page still shows raw code or a blank screen | Click the red **ab** button and check the site is listed. If it isn't, click **Add this domain**, then refresh the page. |
| The extension isn't installed after an Intune deployment | Check the device has synced with Intune, then fully close and reopen Edge. Administrators can confirm the policy at `edge://policy`. |
| The extension has disappeared (manual installation) | Check the extracted folder hasn't been moved or deleted. If it has, restore it or install again. |
| Chrome warns about developer mode extensions | This is expected for manual installations. Choose to keep the extension enabled. |
| The browser says the extension is corrupted or can't be loaded | Remove the extension from the extensions page, extract a fresh copy of the zip file and install it again. |
| **Air Business XSLT Polyfill** appears twice on the extensions page | It was installed manually before your organisation deployed it. Remove the copy marked as a developer-mode extension, and keep the one installed by your organisation. You may need to add any extra sites again. |

---

## Versions and releases

Your installed version is shown under **About** in the extension's pop-up. All versions, with details of what changed in each, are listed on the [releases page](https://github.com/airbusiness-csec/Air-Business-Extension/releases).

---

## Support

For help with the extension or with any Air Business system, please contact your Air Business account contact.

---

## Licence and acknowledgements

Developed by Sam Tilling at Air Business.

Based on the open-source [XSLT Polyfill](https://github.com/mfreed7/xslt_polyfill) by Mason Freed, used under the BSD 3-Clause licence (see `LICENSE`).
