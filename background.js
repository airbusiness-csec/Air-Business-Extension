// Registers detect.js on any extra sites added from the popup, and injects the
// polyfill when detect.js finds an XML page. The granted host permissions are
// the source of truth, so removing a site from the browser's extension
// settings works too.

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
        js: ['detect.js'],
        runAt: 'document_start',
        allFrames: true,
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

// detect.js found an XML document without native XSLT support: inject the
// polyfill into that frame only. Targeting the document (not just the frame)
// means nothing is injected if the frame has navigated away in the meantime.
// executeScript only succeeds where the extension has host permission, i.e.
// the built-in domains and the sites the user has added.
function injectPolyfill(sender) {
  if (!sender.tab) return;
  const target = sender.documentId
    ? { tabId: sender.tab.id, documentIds: [sender.documentId] }
    : { tabId: sender.tab.id, frameIds: [sender.frameId] };
  chrome.scripting
    .executeScript({
      target,
      files: ['xslt-extension.js'],
      world: 'MAIN',
      injectImmediately: true,
    })
    .catch((error) => console.warn('Could not inject the XSLT polyfill:', error));
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id) return false;

  if (message?.type === 'inject') {
    injectPolyfill(sender);
    return false;
  }

  // The popup waits on this before reloading the tab.
  if (message?.type !== 'sync') return false;
  sync().then(
    () => sendResponse({ ok: true }),
    (error) => sendResponse({ ok: false, error: String(error) }),
  );
  return true; // async response
});
