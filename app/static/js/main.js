/* ============================================
   VAYELLE — Main JavaScript
   Handles: shared header/footer injection,
   navigation highlighting, mobile menu,
   toast notifications, and global utilities.
   ============================================ */

// --- Determine if we're in the root folder or pages/ subfolder ---
// This helps build correct relative paths for links and assets
function getBasePath() {
  const path = window.location.pathname;
  if (path.includes('/pages/')) {
    return '../';
  }
  return '';
}

// --- SVG Icons (inline, used throughout the site) ---
const icons = {
  search: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
  heart: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
  heartFilled: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
  user: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  menu: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>',
  x: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
  shoppingBag: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
  star: '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
  chevronRight: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
  chevronLeft: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
  upload: '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
  check: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  trash: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>',
  eye: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
  eyeOff: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>',
  palette: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="13.5" cy="6.5" r="0.5" fill="currentColor"/><circle cx="17.5" cy="10.5" r="0.5" fill="currentColor"/><circle cx="8.5" cy="7.5" r="0.5" fill="currentColor"/><circle cx="6.5" cy="12.5" r="0.5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2Z"/></svg>',
  arrowRight: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
  save: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
  grid: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/></svg>',
  share: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>',
  rotate: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>',
  zoomIn: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="11" x2="11" y1="8" y2="14"/><line x1="8" x2="14" y1="11" y2="11"/></svg>',
  zoomOut: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/><line x1="8" x2="14" y1="11" y2="11"/></svg>'
};

// --- Navigation structure for header ---
const navItems = [
  { label: 'Home',          href: 'index.html',               folder: '' },
  { label: 'Explore',       href: 'pages/explore.html',       folder: 'pages' },
  { label: 'Design Studio', href: 'pages/studio.html',        folder: 'pages' },
  { label: 'AI Match',      href: 'pages/outfit-upload.html', folder: 'pages' },
  { label: 'Budget',        href: 'pages/budget.html',        folder: 'pages' },
  { label: 'Community',     href: 'pages/community.html',     folder: 'pages' }
];

// --- Inject the site header into the page ---
function renderHeader() {
  const headerEl = document.getElementById('site-header');
  if (!headerEl) return;

  const base = getBasePath();
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  // Count favorites for badge
  const favCount = getState().favorites.length;
  const user = getState().user;

  let navLinksHTML = navItems.map(item => {
    const href = base + item.href;
    const isActive = currentPage === item.href.split('/').pop();
    return `<li><a href="${href}" class="${isActive ? 'active' : ''}">${item.label}</a></li>`;
  }).join('');

  headerEl.className = 'vayelle-header';
  headerEl.innerHTML = `
    <div class="header-inner">
      <a href="${base}index.html" class="vayelle-logo">VAYELLE<span style="color:var(--accent);font-size:0.5em;vertical-align:super;">●</span></a>

      <nav>
        <ul class="nav-links">${navLinksHTML}</ul>
      </nav>

      <div class="header-actions">
        <a href="${base}pages/favorites.html" class="header-icon-btn" title="Favorites" style="position:relative;">
          ${icons.heart}
          ${favCount > 0 ? `<span style="position:absolute;top:-2px;right:-2px;background:var(--accent);color:white;font-size:0.625rem;width:16px;height:16px;border-radius:50%;display:flex;align-items:center;justify-content:center;">${favCount}</span>` : ''}
        </a>
        <a href="${base}pages/checkout.html" class="header-icon-btn" title="Cart">
          ${icons.shoppingBag}
        </a>
        <a href="${base}pages/${user ? 'profile' : 'login'}.html" class="header-icon-btn" title="${user ? user.name : 'Sign in'}">
          ${icons.user}
        </a>
        <button class="mobile-menu-btn" onclick="toggleMobileMenu()" aria-label="Open menu">
          ${icons.menu}
        </button>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div class="mobile-nav-overlay" id="mobile-nav-overlay" onclick="closeMobileMenu()"></div>
    <div class="mobile-nav-panel" id="mobile-nav-panel">
      <div class="mobile-nav-close">
        <button onclick="closeMobileMenu()" aria-label="Close menu">${icons.x}</button>
      </div>
      <ul class="mobile-nav-links">
        ${navItems.map(item => `<li><a href="${base + item.href}" onclick="closeMobileMenu()">${item.label}</a></li>`).join('')}
        <li><a href="${base}pages/favorites.html">Favorites</a></li>
        <li><a href="${base}pages/saved.html">Saved Designs</a></li>
        <li><a href="${base}pages/${user ? 'profile' : 'login'}.html">${user ? 'Profile' : 'Sign In'}</a></li>
      </ul>
    </div>
  `;
}

// --- Mobile menu toggle ---
function toggleMobileMenu() {
  document.getElementById('mobile-nav-overlay').classList.toggle('open');
  document.getElementById('mobile-nav-panel').classList.toggle('open');
}

function closeMobileMenu() {
  document.getElementById('mobile-nav-overlay').classList.remove('open');
  document.getElementById('mobile-nav-panel').classList.remove('open');
}

// --- Inject the site footer into the page ---
function renderFooter() {
  const footerEl = document.getElementById('site-footer');
  if (!footerEl) return;

  const base = getBasePath();

  footerEl.className = 'vayelle-footer';
  footerEl.innerHTML = `
    <div class="footer-inner">
      <div class="footer-grid">
        <div class="footer-brand">
          <h3>VAYELLE<span style="color:var(--accent);">●</span></h3>
          <p>Your style. Your rules. Custom shoe design and AI-powered recommendation platform.</p>
          <p style="margin-top:12px;font-size:0.75rem;color:var(--stone-500);">CSE471 — System Analysis and Design<br>Team 03, Lab Section 01 — Fall 2026</p>
        </div>
        <div class="footer-col">
          <h4>Shop</h4>
          <ul>
            <li><a href="${base}pages/explore.html">Explore Shoes</a></li>
            <li><a href="${base}pages/budget.html">Budget Search</a></li>
            <li><a href="${base}pages/size-guide.html">Size Guide</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Create</h4>
          <ul>
            <li><a href="${base}pages/studio.html">Design Studio</a></li>
            <li><a href="${base}pages/colors.html">Color Explorer</a></li>
            <li><a href="${base}pages/saved.html">Saved Designs</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Discover</h4>
          <ul>
            <li><a href="${base}pages/community.html">Community</a></li>
            <li><a href="${base}pages/outfit-upload.html">AI Match</a></li>
            <li><a href="${base}pages/about.html">About VAYELLE</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 VAYELLE. All rights reserved.</p>
        <p>Dhaka, Bangladesh · Prices in BDT (৳)</p>
      </div>
    </div>
  `;
}

// --- Toast Notification System ---
function showToast(message, type) {
  type = type || 'default';
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  container.appendChild(toast);

  // Remove after 3 seconds
  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 3000);
}

// --- Confirmation Modal ---
function showConfirm(title, message, onConfirm) {
  // Remove any existing modal
  const existing = document.getElementById('confirm-modal');
  if (existing) existing.remove();

  const modal = document.createElement('div');
  modal.id = 'confirm-modal';
  modal.className = 'modal-overlay open';
  modal.innerHTML = `
    <div class="modal-box">
      <h3>${title}</h3>
      <p>${message}</p>
      <div class="modal-actions">
        <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        <button class="btn btn-accent" id="confirm-action-btn">Confirm</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  document.getElementById('confirm-action-btn').addEventListener('click', () => {
    modal.remove();
    if (onConfirm) onConfirm();
  });

  // Close on overlay click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });
}

// --- Render a Product Card HTML string ---
function renderProductCard(shoe, basePath) {
  basePath = basePath || getBasePath();
  const fav = isFavorite(shoe.id);
  const colorsHTML = shoe.colors.slice(0, 3).map(c =>
    `<span class="color-dot-sm" style="background:${c}"></span>`
  ).join('');

  return `
    <div class="product-card" onclick="window.location.href='${basePath}pages/shoe-details.html?id=${shoe.id}'">
      <img src="${basePath}${shoe.image}" alt="${shoe.name}" class="product-card-image" loading="lazy">
      <span class="product-card-badge">${shoe.type}</span>
      <button class="product-card-favorite ${fav ? 'active' : ''}" onclick="event.stopPropagation(); toggleFavoriteCard('${shoe.id}', this)" title="Toggle favorite">
        ${fav ? icons.heartFilled : icons.heart}
      </button>
      <div class="product-card-body">
        <div class="product-card-name">${shoe.name}</div>
        <div class="product-card-desc">${shoe.description}</div>
        <div class="product-card-footer">
          <div class="product-card-colors">${colorsHTML}</div>
          <div class="product-card-rating">
            <span class="star">${icons.star}</span> ${shoe.rating}
          </div>
        </div>
        <div class="product-card-price" style="margin-top:8px;">${bdt(shoe.price)}</div>
      </div>
    </div>
  `;
}

// --- Toggle favorite from product card button ---
function toggleFavoriteCard(shoeId, btn) {
  toggleFavorite(shoeId);
  const fav = isFavorite(shoeId);
  btn.classList.toggle('active', fav);
  btn.innerHTML = fav ? icons.heartFilled : icons.heart;
  showToast(fav ? 'Added to favorites' : 'Removed from favorites', fav ? 'success' : 'default');
}

// --- Generate the SVG shoe illustration ---
// This recreates the Lovable ShoeArt component as an inline SVG
function renderShoeArt(options) {
  const colors = options.colors || defaultColors;
  const soleId = options.soleId || 'flat';
  const materialId = options.materialId || null;
  const decos = options.decos || [];
  const hidden = options.hidden || {};
  const width = options.width || 400;
  const height = options.height || 200;
  const rotate = options.rotate || 0;

  const soleObj = getSole(soleId);
  const soleH = soleObj ? soleObj.height : 10;

  // Material texture pattern
  let patternDef = '';
  if (materialId === 'mesh') {
    patternDef = `<pattern id="tex-mesh" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.5" fill="black" opacity="0.18"/></pattern>`;
  } else if (materialId === 'suede') {
    patternDef = `<pattern id="tex-suede" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="3" x2="6" y2="3" stroke="black" stroke-width="0.5" opacity="0.06"/></pattern>`;
  } else if (materialId === 'canvas') {
    patternDef = `<pattern id="tex-canvas" width="6" height="6" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="6" y2="6" stroke="black" stroke-width="0.5" opacity="0.1"/><line x1="6" y1="0" x2="0" y2="6" stroke="black" stroke-width="0.5" opacity="0.1"/></pattern>`;
  } else if (materialId === 'leather') {
    patternDef = `<pattern id="tex-leather" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="black" opacity="0.04"/></pattern>`;
  } else if (materialId === 'synthetic') {
    patternDef = `<pattern id="tex-synthetic" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="black" opacity="0.03"/></pattern>`;
  }

  const texFill = materialId ? `url(#tex-${materialId})` : 'none';
  const soleY = 170 - soleH;

  let svg = `<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" style="width:${width}px;max-width:100%;aspect-ratio:2/1;${rotate ? `transform:perspective(900px) rotateY(${rotate}deg);` : ''}">
    <defs>${patternDef}</defs>`;

  // Shadow
  svg += `<ellipse cx="200" cy="190" rx="160" ry="8" fill="black" opacity="0.08"/>`;

  // Sole
  if (!hidden.sole) {
    svg += `<path d="M60,${soleY} Q60,${soleY+soleH} 80,${soleY+soleH} L320,${soleY+soleH} Q340,${soleY+soleH} 340,${soleY} Z" fill="${colors.sole || '#fff'}"/>`;
  }

  // Upper (main body)
  if (!hidden.upper) {
    svg += `<path d="M80,${soleY} Q60,${soleY-40} 80,${soleY-80} Q120,${soleY-110} 200,${soleY-90} Q280,${soleY-70} 340,${soleY-60} Q360,${soleY-40} 340,${soleY} Z" fill="${colors.upper || '#F8F7F3'}"/>`;
    if (materialId) {
      svg += `<path d="M80,${soleY} Q60,${soleY-40} 80,${soleY-80} Q120,${soleY-110} 200,${soleY-90} Q280,${soleY-70} 340,${soleY-60} Q360,${soleY-40} 340,${soleY} Z" fill="${texFill}"/>`;
    }
  }

  // Toe cap
  if (!hidden.toe) {
    svg += `<path d="M80,${soleY} Q60,${soleY-40} 80,${soleY-70} Q100,${soleY-85} 130,${soleY-80} Q110,${soleY-50} 100,${soleY} Z" fill="${colors.toe || '#E9E2D4'}" opacity="0.7"/>`;
  }

  // Heel counter
  if (!hidden.heel) {
    svg += `<path d="M300,${soleY} Q310,${soleY-30} 340,${soleY-55} Q350,${soleY-35} 340,${soleY} Z" fill="${colors.heel || '#F36B38'}"/>`;
  }

  // Stripe
  if (!hidden.stripe) {
    svg += `<path d="M150,${soleY-75} Q200,${soleY-55} 280,${soleY-50}" stroke="${colors.stripe || '#171717'}" stroke-width="8" fill="none" stroke-linecap="round"/>`;
  }

  // Laces
  if (!hidden.laces) {
    for (let i = 0; i < 5; i++) {
      const lx = 140 + i * 20;
      const ly = soleY - 85 + i * 5;
      svg += `<line x1="${lx}" y1="${ly}" x2="${lx+15}" y2="${ly-12}" stroke="${colors.laces || '#F8F7F3'}" stroke-width="5" stroke-linecap="round"/>`;
    }
  }

  // Construction line
  svg += `<path d="M80,${soleY} L340,${soleY}" stroke="#888" stroke-width="0.5" stroke-dasharray="4,4"/>`;

  // Decorations
  for (const deco of decos) {
    const decoData = getDecoration(deco.id);
    if (decoData) {
      const x = (deco.x / 100) * 400;
      const y = (deco.y / 100) * 200;
      const scale = deco.scale || 1;
      svg += `<text x="${x}" y="${y}" font-size="${24 * scale}" text-anchor="middle" dominant-baseline="central" style="pointer-events:none;">${decoData.glyph}</text>`;
    }
  }

  svg += `</svg>`;
  return svg;
}

// --- Initialize header and footer on page load ---
document.addEventListener('DOMContentLoaded', function() {
  renderHeader();
  renderFooter();
});

// --- Helper: get URL query parameter ---
function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

// --- Helper: format date string ---
function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
