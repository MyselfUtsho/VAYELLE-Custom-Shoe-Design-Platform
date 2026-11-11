# VAYELLE Frontend — Match It. Vibe It.

CSE471 System Analysis & Design — Team 03, Lab Section 01 (Fall 2026)

## 📌 About This Frontend
This is the complete, converted, and finished frontend for **VAYELLE — Custom Shoe Design and AI-Powered Recommendation Platform**.

Converted from Lovable's unfinished React/TypeScript/Tailwind prototype into our university project's preferred technology stack:
- **HTML5**
- **CSS3** (Preserving Lovable's exact stone palette, Manrope typography, and layout tokens)
- **Vanilla JavaScript (ES6+)**
- **Bootstrap 5 compatible design tokens**

---

## 🚀 How to Run the Frontend Locally

### Option 1: Directly in Any Web Browser (No Server Needed)
Simply double-click `index.html` or right-click `index.html` → **Open with** → **Google Chrome / Microsoft Edge / Firefox**.

All pages, styles, scripts, SVG shoe rendering, and `localStorage` features work right in your browser out-of-the-box!

### Option 2: Using VS Code Live Server (Recommended for Development)
1. Open the project in VS Code.
2. Install the **Live Server** extension (by Ritwick Dey).
3. Right-click `index.html` and select **"Open with Live Server"**.
4. The site will open at `http://127.0.0.1:5500/index.html`.

### Option 3: Using Node.js or Python Local Server
- **Python 3:**
  ```bash
  cd frontend
  python -m http.server 8000
  ```
  Open `http://localhost:8000` in your browser.

- **Node.js (`npx serve`):**
  ```bash
  cd frontend
  npx serve .
  ```

---

## 📂 Project Folder Structure

```
frontend/
├── index.html                   # VAYELLE Homepage
├── README.md                    # This documentation file
│
├── pages/                       # All individual subpages
│   ├── explore.html             # Browse shoes with real-time filtering & search
│   ├── category.html            # Category view (Men's, Women's, Unisex, Sneakers, etc.)
│   ├── shoe-details.html        # Shoe details, views, specs & color preview
│   ├── colors.html              # Interactive Color Studio & Harmonies
│   ├── budget.html              # Dynamic budget-based slider & price filter
│   ├── materials.html           # Step 2: Material selection with specs
│   ├── soles.html               # Step 3: Sole platform selection
│   ├── decorations.html         # Step 4: Stripes, patterns, patches, glyphs
│   ├── studio.html              # Step 5: Full 2D Design Studio with undo/redo/save
│   ├── preview.html             # Before/After live comparison & summary
│   ├── viewer.html              # 3D-perspective rotation & zoom viewer
│   ├── on-foot.html             # On-foot & lifestyle streetwear simulation
│   ├── price.html               # Itemized dynamic price calculator
│   ├── layers.html              # Interactive layer toggling & split slider
│   ├── accessible.html          # Color-blind-friendly Okabe–Ito palette mode
│   ├── material-recommendations.html # Smart budget/style material ranking
│   ├── outfit-upload.html       # Drag-and-drop outfit photo upload & validation
│   ├── outfit-analysis.html     # Dominant color extraction & style classification
│   ├── recommendations.html     # Smart shoe recommendations from outfit/vibe
│   ├── size-guide.html          # Foot measurement calculator & size chart
│   ├── checkout.html            # Simulated order review & shipping form
│   ├── payment-success.html     # Demo verified payment response screen
│   ├── payment-failure.html     # Demo failed payment response screen
│   ├── community.html           # Public design gallery with likes
│   ├── community-detail.html    # Detailed design view with creator credit
│   ├── remix.html               # Interactive design remixing engine
│   ├── saved.html               # Saved custom shoe designs manager
│   ├── favorites.html           # User-favorited shoe collection
│   ├── order-history.html       # Simulated order records & tracking
│   ├── login.html               # Demo student sign-in
│   ├── register.html            # Demo student account registration
│   ├── profile.html             # User profile, usual size & quick studio links
│   └── about.html               # Project info, CSE471 details & team roster
│
├── css/
│   ├── style.css                # Core design system tokens, typography & base layout
│   ├── components.css           # Buttons, cards, chips, forms, badges, modals
│   └── responsive.css           # Breakpoints (Mobile, Tablet, Desktop)
│
├── js/
│   ├── data.js                  # Shoe models, materials, soles, colors, size chart
│   ├── store.js                 # LocalStorage persistence & state pub/sub engine
│   ├── colors.js                # Color harmonies, RGB/HSL, canvas color extraction
│   └── main.js                  # Header/footer injection, toast alerts, SVG ShoeArt
│
└── assets/
    └── images/                  # All shoe, lifestyle & outfit photos
```

---

## 👥 Team Responsibilities Covered

- **Athoy Roy (ID: 23101197):**
  - Category and gender browsing (`explore.html`, `category.html`)
  - Material and sole options (`materials.html`, `soles.html`)
  - Decorative elements library & on-foot preview (`decorations.html`, `on-foot.html`)
  - 3D perspective shoe viewer (`viewer.html`)

- **Miftahul Islam Prangon (ID: 24101537):**
  - Color exploration and harmony suggestions (`colors.html`)
  - Interactive 2D design canvas studio with undo/redo/save (`studio.html`)
  - Live design preview & split layer simulation (`preview.html`, `layers.html`)
  - Color-blind-friendly accessible palette mode (`accessible.html`)

- **Diya Zerin (ID: 22101062):**
  - Budget-based shoe search & filtering (`budget.html`)
  - Itemized estimated price calculator (`price.html`)
  - Material recommendations and saved designs (`material-recommendations.html`, `saved.html`)
  - Outfit color analysis display (`outfit-analysis.html`)

- **Khairul Islam Bhuiya (ID: 23101347):**
  - Outfit image upload with file validation (`outfit-upload.html`)
  - Foot measurement calculator and size chart (`size-guide.html`)
  - Sandbox checkout flow & response screens (`checkout.html`, `payment-success.html`, `payment-failure.html`)
  - Smart AI shoe recommendations (`recommendations.html`)
  - Community design showcase & remix engine (`community.html`, `community-detail.html`, `remix.html`)

---

## 🛠 Where to Make Changes Later

- **Adding or modifying shoes/prices/materials:** Edit [js/data.js](js/data.js).
- **Tweaking colors or styles:** Edit [css/style.css](css/style.css) or [css/components.css](css/components.css).
- **State and storage behaviors:** Edit [js/store.js](js/store.js).
- **Navigation or common layout items:** Edit [js/main.js](js/main.js).
