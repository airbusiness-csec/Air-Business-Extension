// Used by background.js and popup.js.
// Built-in sites come from content_scripts in manifest.json. Anything else is an
// optional host permission the user granted from the popup.

// e.g. "https://intranet.example.com/*"
const SITE_PATTERN = /^https?:\/\/[^/]+\/\*$/;

function builtInPatterns() {
  return (chrome.runtime.getManifest().content_scripts || []).flatMap((cs) => cs.matches || []);
}

// Only handles "scheme://host/*" patterns, which is all we use.
function patternMatchesUrl(pattern, url) {
  const m = /^(\*|https?):\/\/([^/]+)\/\*$/.exec(pattern);
  if (!m) return false;
  let u;
  try {
    u = new URL(url);
  } catch {
    return false;
  }
  const scheme = u.protocol.slice(0, -1);
  if (scheme !== 'http' && scheme !== 'https') return false;
  if (m[1] !== '*' && m[1] !== scheme) return false;
  const host = m[2];
  if (host === '*') return true;
  if (host.startsWith('*.')) {
    const base = host.slice(2);
    return u.hostname === base || u.hostname.endsWith(`.${base}`);
  }
  return u.hostname === host;
}

// Skips the built-in sites so the script isn't injected twice.
async function userAddedSites() {
  const builtIn = new Set(builtInPatterns());
  const { origins = [] } = await chrome.permissions.getAll();
  return origins.filter((o) => SITE_PATTERN.test(o) && !builtIn.has(o)).sort();
}
