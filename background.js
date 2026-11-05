// Keeps the polyfill content script registered on exactly the extra sites the
// user has granted via the popup (the built-in scope in manifest.json is
// handled statically). The browser's granted host permissions are the single
// source of truth, so revoking a site in the browser's own extension settings
// also stops the polyfill running there.

importScripts('scope.js');

const SCRIPT_ID = 'xslt-polyfill';

async function doSync() {
  const matches = await userAddedSites();

  const existing = await chrome.scripting.getRegisteredContentScripts({ ids: [SCRIPT_ID] });
  if (existing.length) {
    await chrome.scripting.unregisterContentScripts({ ids: [SCRIPT_ID] });
  }
  if (matches.length) {
    await chrome.scripting.registerContentScripts([
      {
        id: SCRIPT_ID,
        matches,
        js: ['xslt-extension.js'],
        runAt: 'document_start',
        allFrames: true,
        world: 'MAIN',
        persistAcrossSessions: true,
      },
    ]);
  }
}

// Serialise syncs so concurrent triggers can't race on the script ID.
let queue = Promise.resolve();
function sync() {
  queue = queue.then(doSync, doSync);
  return queue;
}

chrome.runtime.onInstalled.addListener(() => sync());
chrome.runtime.onStartup.addListener(() => sync());
chrome.permissions.onAdded.addListener(() => sync());
chrome.permissions.onRemoved.addListener(() => sync());

// The popup asks for a sync and waits, so it can reload the tab afterwards.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id || message?.type !== 'sync') {
    return false;
  }
  sync().then(
    () => sendResponse({ ok: true }),
    (error) => sendResponse({ ok: false, error: String(error) }),
  );
  return true; // Respond asynchronously.
});
