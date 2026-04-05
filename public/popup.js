document.addEventListener('DOMContentLoaded', () => {

  const DEFAULTS = {
    autoMode: false
  };

  const API_IMAGE_URL = 'http://localhost:5000/api/image';
  const MAX_TEXT_CHARS = 100_000;

  const autoCheck = document.getElementById('auto-mode');
  const modeLabel = document.getElementById('mode-description');
  const scanBtn = document.getElementById('scan-btn');
  const scanStatus = document.getElementById('scan-status');
  const resultWrap = document.getElementById('result-wrap');
  const resultImg = document.getElementById('result-img');
  const emotionRow = document.getElementById('emotion-row');

  let lastResultObjectUrl = null;

  /* ================= AUTO LABEL ================= */

  function updateAutoLabel() {
    const modeTitle = document.getElementById('mode-title');
    if (autoCheck.checked) {
      modeTitle.textContent = 'AUTO MODE';
      modeLabel.textContent = 'SCAN PAGE TEXT';
      scanBtn.textContent = 'SCAN PAGE';
    } else {
      modeTitle.textContent = 'SELECT MODE';
      modeLabel.textContent = 'SCAN HIGHLIGHTED TEXT';
      scanBtn.textContent = 'SCAN SELECTION';
    }
  }

  /* ================= SYSTEM THEME ================= */

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  function applySystemTheme(e) {
    const isDark = e.matches;
    document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }

  // Apply immediately
  applySystemTheme(mediaQuery);

  // Listen for OS theme changes live
  mediaQuery.addEventListener('change', applySystemTheme);

  /* Load settings */

  updateAutoLabel();

  chrome.storage.sync.get(['rexnetSettings'], ({ rexnetSettings }) => {

    const savedAuto = rexnetSettings?.autoMode ?? DEFAULTS.autoMode;

    autoCheck.checked = savedAuto;
    updateAutoLabel();
  });

  /* Save settings */

  function saveSettings() {
    chrome.storage.sync.get(['rexnetSettings'], ({ rexnetSettings }) => {
      chrome.storage.sync.set({
        rexnetSettings: {
          ...rexnetSettings,
          autoMode: autoCheck.checked
        }
      });
    });
  }

  autoCheck.addEventListener('change', () => {
    updateAutoLabel();
    saveSettings();
  });

  /* Scan to API */

  function setStatus(message, isError) {
    scanStatus.textContent = message || '';
    scanStatus.classList.toggle('error', Boolean(isError));
  }

  function clearResultImage() {
    if (lastResultObjectUrl) {
      URL.revokeObjectURL(lastResultObjectUrl);
      lastResultObjectUrl = null;
    }
    resultImg.removeAttribute('src');
    resultWrap.hidden = true;
    emotionRow.textContent = '';
  }

  async function getTextFromActiveTab(autoMode) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      throw new Error('No active tab.');
    }

    const url = tab.url || '';
    if (url.startsWith('chrome://') || url.startsWith('chrome-extension://') || url.startsWith('edge://')) {
      throw new Error('Cannot run on this page. Try a normal website.');
    }

    let injected;
    try {
      [injected] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        args: [autoMode, MAX_TEXT_CHARS],
        func: (auto, maxLen) => {
          if (auto) {
            const raw = document.body?.innerText ?? '';
            const t = raw.trim();
            return t.length > maxLen ? t.slice(0, maxLen) : t;
          }
          return window.getSelection().toString().trim();
        },
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      throw new Error(msg.includes('Cannot access') ? 'Cannot access this page.' : msg);
    }

    const text = injected?.result;
    if (typeof text !== 'string') {
      throw new Error('Could not read from this page.');
    }
    return text;
  }

  scanBtn.addEventListener('click', async () => {
    clearResultImage();
    setStatus('');
    scanBtn.disabled = true;

    try {
      const autoMode = autoCheck.checked;
      const text = await getTextFromActiveTab(autoMode);

      if (!text) {
        setStatus(
          autoMode
            ? 'No page text found.'
            : 'No selection. Highlight text on the page, then click again.',
          true
        );
        return;
      }

      setStatus('Calling API…');

      const res = await fetch(API_IMAGE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        let detail = res.statusText;
        try {
          const data = await res.json();
          if (data?.error) detail = data.error;
        } catch {
          /* use statusText */
        }
        throw new Error(detail);
      }

      const blob = await res.blob();
      if (!blob.size) {
        throw new Error('Empty image response.');
      }

      lastResultObjectUrl = URL.createObjectURL(blob);
      resultImg.src = lastResultObjectUrl;
      resultWrap.hidden = false;

      const label = res.headers.get('X-Emotion');
      const score = res.headers.get('X-Emotion-Score');
      emotionRow.textContent =
        label != null
          ? `EMOTION: ${label}${score != null ? ` · ${score}` : ''}`
          : '';

      setStatus('Done.');
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setStatus(msg, true);
    } finally {
      scanBtn.disabled = false;
    }
  });

});