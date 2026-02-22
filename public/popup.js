document.addEventListener('DOMContentLoaded', () => {

  const DEFAULTS = { autoMode: false };
  const autoCheck = document.getElementById('auto-mode');
  const modeLabel = document.getElementById('mode-description');

  function updateLabel() {
    modeLabel.textContent = autoCheck.checked
      ? 'SCAN PAGE TEXT'
      : 'SCAN HIGHLIGHTED TEXT';
  }

  chrome.storage.sync.get(['rexnetSettings'], ({ rexnetSettings }) => {
    const saved = (rexnetSettings && typeof rexnetSettings.autoMode === 'boolean')
      ? rexnetSettings.autoMode
      : DEFAULTS.autoMode;

    autoCheck.checked = saved;
    updateLabel();
  });

  function save() {
    chrome.storage.sync.set({
      rexnetSettings: { autoMode: autoCheck.checked }
    });
  }

  autoCheck.addEventListener('change', () => {
    save();
    updateLabel();
  });

});