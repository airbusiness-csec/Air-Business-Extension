// Shared by background.js (via importScripts) and popup.js.
//
// Built-in scope: the content_scripts "matches" in manifest.json. Those sites
// always get the polyfill and can't be removed from the popup. Anything else
// the user adds with the popup button is tracked as an optional host
// permission and registered dynamically by background.js.

// Plain http(s) site patterns, e.g. "https://intranet.example.com/*".
const SITE_PATTERN = /^https?:\/\/[^/]+\/\*$/;

function builtInPatterns() {
  return (chrome.runtime.getManifest().content_scripts || []).flatMap((cs) => cs.matches || []);
}

// Minimal match-pattern check for "scheme://host/*" patterns, where scheme may
// be "*" (http or https) and host may start with "*." (domain + subdomains).
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

// Sites the user added with the button (excludes built-in scope, so the
// polyfill is never injected twice).
async function userAddedSites() {
  const builtIn = new Set(builtInPatterns());
  const { origins = [] } = await chrome.permissions.getAll();
  return origins.filter((o) => SITE_PATTERN.test(o) && !builtIn.has(o)).sort();
}
