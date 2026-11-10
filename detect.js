// First-stage content script: runs on every page in scope, so it's kept tiny.
// It only asks background.js to inject the polyfill (xslt-extension.js, ~1.4 MB)
// into this frame when the document is XML and the browser lacks native XSLT.
// Ordinary HTML pages never receive the polyfill.
//
// Runs in the extension's isolated world, so page scripts can't tamper with
// XSLTProcessor to influence the native-support check.
(() => {
  const type = document.contentType;
  const isXml = type === 'text/xml' || type === 'application/xml' || type.endsWith('+xml');
  if (!isXml || location.protocol === 'file:') return;

  let nativeSupported = typeof XSLTProcessor === 'function';
  if (nativeSupported) {
    try {
      new XSLTProcessor();
    } catch {
      nativeSupported = false;
    }
  }
  if (nativeSupported) return;

  chrome.runtime.sendMessage({ type: 'inject' }).catch(() => {
    // Extension reloaded or updating; the page just won't be transformed.
  });
})();
