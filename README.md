# 🦕 RexNet — Sentiment Analysis Chrome Extension

> Because everything is more fun with dinosaurs.

RexNet is a Chrome extension that performs real-time sentiment analysis on text in your browser and reacts with tiny, adorable dinosaur stickers. Whether you're wading through grim headlines, dense research papers, or a passive-aggressive work email, RexNet gives you an instant emotional gut-check — delivered by a prehistoric reptile.

---

## 🌟 Features

- **Auto Mode** — RexNet passively scans text on the page and overlays small dinosaur stickers near detected passages, reacting to the emotional tone in real time.
- **Highlight Mode** — Select any text, right-click, and choose **"What dino is this?"** from the context menu to get a sentiment-matched dinosaur on demand.
- Dinosaurs are **small, non-intrusive, and delightful**.
- Works great on news sites, Gmail, Google Scholar, research portals, and most content-heavy pages.

---

## 🦖 The Dino Legend

Each dinosaur corresponds to a sentiment category:

| Sentiment | Dinosaur | Vibe |
|---|---|---|
| Very Positive 🎉 | T-Rex (dancing) | Absolutely jazzed |
| Positive 😊 | Brachiosaurus | Optimistic, head held high |
| Neutral 😐 | Stegosaurus | Unbothered. Just existing. |
| Negative 😟 | Triceratops | Defensive, a little worried |
| Very Negative 😱 | Ankylosaurus | Braced for impact |
| Sarcastic / Mixed 🤨 | Velociraptor | Suspicious. Always suspicious. |

---

## 🛠️ How It Works

### Auto Mode

When enabled via the extension popup, RexNet activates a content script that periodically scans visible text nodes on the page. Each chunk of text is analyzed using a sentiment scoring model, and a small dinosaur sticker (a lightweight SVG or PNG overlay) is injected near the relevant passage. Stickers are subtle by design — think sticky note, not billboard.

### Highlight Mode

1. Select any text on a webpage
2. Right-click to open the browser context menu
3. Click **"RexNet: What dino is this?"**
4. A dinosaur sticker will appear near your selected text, reflecting its sentiment

The context menu option is registered via Chrome's `contextMenus` API and only appears when text is selected.

## ⚙️ Configuration

Click the RexNet icon in your Chrome toolbar to access settings:

- **Auto Mode** — Toggle passive page scanning on/off
- **Scan Frequency** — How often the page is re-analyzed (default: on scroll/page load)
- **Sticker Size** — Small / Medium (we keep it tasteful)
- **Dino Pack** — Choose your preferred dinosaur art style (pixel art, flat, sketch)

---

## 📁 Project Structure

```
rexnet/
├── public/
│   ├── manifest.json       # Chrome extension manifest (v3)
│   └── icons/              # Extension icons
├── src/
│   ├── background.js       # Service worker: context menu registration
│   ├── content.js          # Content script: DOM parsing & sticker injection
│   ├── popup/              # Extension popup UI (toggle auto mode, settings)
│   │   ├── popup.html
│   │   └── popup.js
│   └── sentiment/          # Sentiment analysis logic
│       └── analyzer.js
├── assets/
│   └── dinos/              # Dinosaur sticker assets
├── dist/                   # Built extension (generated)
├── package.json
└── README.md
```

---

*Made with 🦕 and a concerning amount of paleontology enthusiasm.*