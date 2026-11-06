// Anything that comes from the page goes in via textContent, never innerHTML.
// Helpers like userAddedSites() live in scope.js.

const $ = (id) => document.getElementById(id);

let tab = null;
let pattern = null;
let enabled = false;

function patternFor(url) {
  try {
    const u = new URL(url);
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return null;
    return `${u.protocol}//${u.hostname}/*`;
  } catch {
    return null;
  }
}

const labelFor = (p) => p.replace(/\/\*$/, '');

function showError(message) {
  const el = $('error');
  el.textContent = message;
  el.hidden = !message;
}

async function syncRegistration() {
  const result = await chrome.runtime.sendMessage({ type: 'sync' });
  if (!result?.ok) throw new Error(result?.error || 'Could not update the extension.');
}

async function render() {
  const sites = await userAddedSites();
  const builtIn = builtInPatterns();

  $('builtin').replaceChildren(
    ...builtIn.map((p) => {
      const li = document.createElement('li');
      const name = document.createElement('span');
      name.textContent = labelFor(p);
      li.append(name);
      return li;
    }),
  );

  const toggle = $('toggle');
  if (pattern && tab?.url && builtIn.some((p) => patternMatchesUrl(p, tab.url))) {
    enabled = true;
    $('host').textContent = labelFor(pattern);
    $('state').textContent = 'Included by default in this extension.';
    toggle.textContent = 'Included by default';
    toggle.classList.remove('remove');
    toggle.disabled = true;
  } else if (pattern) {
    enabled = sites.includes(pattern);
    $('host').textContent = labelFor(pattern);
    $('state').textContent = enabled
      ? 'The polyfill runs on this domain.'
      : 'The polyfill does not run on this domain.';
    toggle.textContent = enabled ? 'Remove this domain' : 'Add this domain';
    toggle.classList.toggle('remove', enabled);
    toggle.disabled = false;
  } else {
    $('host').textContent = 'This page can’t be added';
    $('state').textContent = 'Only http and https sites are supported.';
    toggle.disabled = true;
  }

  const list = $('sites');
  list.replaceChildren(
    ...sites.map((site) => {
      const li = document.createElement('li');
      const name = document.createElement('span');
      name.textContent = labelFor(site);
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = 'Remove';
      remove.setAttribute('aria-label', `Remove ${labelFor(site)}`);
      remove.addEventListener('click', () => removeSite(site));
      li.append(name, remove);
      return li;
    }),
  );
  $('empty').hidden = sites.length > 0;
}

async function removeSite(site) {
  showError('');
  try {
    await chrome.permissions.remove({ origins: [site] });
    await syncRegistration();
    if (site === pattern && tab) await chrome.tabs.reload(tab.id);
  } catch (error) {
    showError(error.message || String(error));
  }
  await render();
}

$('toggle').addEventListener('click', async () => {
  if (!pattern || $('toggle').disabled) return;
  if (enabled) {
    await removeSite(pattern);
    return;
  }
  showError('');
  try {
    // Has to be the first await or it no longer counts as a user click.
    const granted = await chrome.permissions.request({ origins: [pattern] });
    if (!granted) {
      await render();
      return;
    }
    await syncRegistration();
    // Reload so the script runs on this page.
    await chrome.tabs.reload(tab.id);
    window.close();
  } catch (error) {
    showError(error.message || String(error));
    await render();
  }
});

$('version').textContent = `Version ${chrome.runtime.getManifest().version}`;

$('help').addEventListener('click', async () => {
  await chrome.tabs.create({ url: chrome.runtime.getURL('README.html') });
  window.close();
});

(async () => {
  try {
    [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    pattern = tab?.url ? patternFor(tab.url) : null;
  } catch {
    pattern = null;
  }
  await render();
})();
