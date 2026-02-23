document.addEventListener('DOMContentLoaded', () => {

  const DEFAULTS = {
    autoMode: false
  };

  const autoCheck = document.getElementById('auto-mode');
  const modeLabel = document.getElementById('mode-description');

  /* ================= AUTO LABEL ================= */

  function updateAutoLabel() {
    const modeTitle = document.getElementById('mode-title');
    if (autoCheck.checked) {
      modeTitle.textContent = 'AUTO MODE';
      modeLabel.textContent = 'SCAN PAGE TEXT';
    } else {
      modeTitle.textContent = 'SELECT MODE';
      modeLabel.textContent = 'SCAN HIGHLIGHTED TEXT';
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

  /* ================= LOAD SETTINGS ================= */

  chrome.storage.sync.get(['rexnetSettings'], ({ rexnetSettings }) => {

    const savedAuto = rexnetSettings?.autoMode ?? DEFAULTS.autoMode;

    autoCheck.checked = savedAuto;
    updateAutoLabel();
  });

  /* ================= SAVE ================= */

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

});