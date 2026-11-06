// Registers the polyfill on any extra sites added from the popup. The granted
// host permissions are the source of truth, so removing a site from the
// browser's extension settings works too.

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

// One sync at a time, otherwise register/unregister can clash.
let queue = Promise.resolve();
function sync() {
  queue = queue.then(doSync, doSync);
  return queue;
}

chrome.runtime.onInstalled.addListener(() => sync());
chrome.runtime.onStartup.addListener(() => sync());
chrome.permissions.onAdded.addListener(() => sync());
chrome.permissions.onRemoved.addListener(() => sync());

// The popup waits on this before reloading the tab.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id || message?.type !== 'sync') {
    return false;
  }
  sync().then(
    () => sendResponse({ ok: true }),
    (error) => sendResponse({ ok: false, error: String(error) }),
  );
  return true; // async response
});
