/* ============================================
   VAYELLE — Product Data & Constants
   All sample product data, materials, soles,
   decorations, color palette, community designs,
   and size chart data.
   ============================================ */

// --- Currency formatter for BDT ---
function bdt(amount) {
  return '৳' + Number(amount).toLocaleString('en-BD');
}

// --- Shoe Catalog (6 products) ---
const shoes = [
  {
    id: 'urban-runner',
    name: 'Urban Runner',
    type: 'Sneakers',
    gender: 'Unisex',
    price: 2500,
    style: 'streetwear',
    rating: 4.7,
    image: 'assets/images/shoe-black-runner.jpg',
    colors: ['#000000', '#FFFFFF', '#E55B3C'],
    description: 'High-performance street runner with breathable mesh and reinforced heel. Perfect for all-day comfort.'
  },
  {
    id: 'cloud-street',
    name: 'Cloud Street',
    type: 'Sneakers',
    gender: 'Unisex',
    price: 3200,
    style: 'casual',
    rating: 4.9,
    image: 'assets/images/shoe-white.jpg',
    colors: ['#FFFFFF', '#D4C5A9', '#87CEEB'],
    description: 'Cloud-like cushioning with clean minimal aesthetics. Walk on air every step of the way.'
  },
  {
    id: 'mono-classic',
    name: 'Mono Classic',
    type: 'Casual',
    gender: 'Men',
    price: 2800,
    style: 'streetwear',
    rating: 4.6,
    image: 'assets/images/shoe-black-beige.jpg',
    colors: ['#1A1A1A', '#F5F5DC', '#808080'],
    description: 'Timeless two-tone design blending refined and urban. A modern wardrobe essential.'
  },
  {
    id: 'retro-flex',
    name: 'Retro Flex',
    type: 'Sneakers',
    gender: 'Women',
    price: 3500,
    style: 'streetwear',
    rating: 4.8,
    image: 'assets/images/shoe-retro.jpg',
    colors: ['#D2691E', '#F5DEB3', '#8B4513'],
    description: 'Vintage-inspired flex sole meets modern materials. Stand out with retro charm.'
  },
  {
    id: 'urban-formal',
    name: 'Urban Formal',
    type: 'Formal',
    gender: 'Men',
    price: 4200,
    style: 'formal',
    rating: 4.5,
    image: 'assets/images/shoe-formal.jpg',
    colors: ['#000000', '#1A1A1A', '#333333'],
    description: 'Refined formal shoe with premium leather finish. Business elegance meets street-ready comfort.'
  },
  {
    id: 'daily-canvas',
    name: 'Daily Canvas',
    type: 'Casual',
    gender: 'Women',
    price: 1900,
    style: 'casual',
    rating: 4.4,
    image: 'assets/images/shoe-canvas.jpg',
    colors: ['#FAF0E6', '#DEB887', '#D2B48C'],
    description: 'Lightweight canvas slip-on for effortless everyday style. Breathable and easy-going.'
  }
];

// --- Materials (5 options) ---
const materials = [
  { id: 'leather',   name: 'Leather',   price: 900, durability: 5, available: true,  suits: ['formal', 'streetwear'], description: 'Premium genuine leather — smooth, breathable, ages beautifully.', image: 'https://images.unsplash.com/photo-1585435557343-3b348031a6e3?w=400&h=300&fit=crop' },
  { id: 'suede',     name: 'Suede',     price: 700, durability: 3, available: true,  suits: ['casual', 'streetwear'], description: 'Soft napped finish with a luxurious textured surface.', image: 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=300&fit=crop' },
  { id: 'mesh',      name: 'Mesh',      price: 400, durability: 3, available: true,  suits: ['casual', 'streetwear'], description: 'Lightweight breathable mesh for maximum airflow and comfort.', image: 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=300&fit=crop' },
  { id: 'canvas',    name: 'Canvas',    price: 250, durability: 2, available: true,  suits: ['casual'],              description: 'Classic woven fabric — lightweight, flexible, and easy to style.', image: 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=300&fit=crop' },
  { id: 'synthetic', name: 'Synthetic', price: 350, durability: 4, available: false, suits: ['streetwear'],           description: 'Engineered synthetic leather for weather resistance and durability.', image: 'https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=300&fit=crop' }
];

// --- Soles (5 options) ---
const soles = [
  { id: 'flat',       name: 'Flat',             price: 0,   height: 10, description: 'Ultra-thin low-profile sole for a grounded feel.' },
  { id: 'chunky',     name: 'Chunky',           price: 600, height: 26, description: 'Bold thick platform sole for maximum presence.' },
  { id: 'foam',       name: 'Lightweight Foam',  price: 400, height: 16, description: 'Cloud-soft EVA foam for all-day walking comfort.' },
  { id: 'cupsole',    name: 'Cupsole',           price: 300, height: 14, description: 'Wrapped rubber cupsole for skateboard-inspired support.' },
  { id: 'sport',      name: 'Sport',             price: 500, height: 20, description: 'Responsive sport sole with energy-return cushioning.' }
];

// --- Decorations (10 elements) ---
const decorations = [
  { id: 'racing-stripe',   name: 'Racing Stripe',      kind: 'Stripes',    price: 150, glyph: '═' },
  { id: 'pinstripe',       name: 'Pinstripe',           kind: 'Stripes',    price: 120, glyph: '║' },
  { id: 'camo',            name: 'Camo Pattern',        kind: 'Patterns',   price: 200, glyph: '◆' },
  { id: 'checker',         name: 'Checkerboard',        kind: 'Patterns',   price: 180, glyph: '▣' },
  { id: 'star-patch',      name: 'Star Patch',          kind: 'Patches',    price: 220, glyph: '★' },
  { id: 'lightning-patch',  name: 'Lightning Bolt',     kind: 'Patches',    price: 200, glyph: '⚡' },
  { id: 'crown',           name: 'Crown Icon',          kind: 'Icons',      price: 180, glyph: '♛' },
  { id: 'flame',           name: 'Flame Icon',          kind: 'Icons',      price: 160, glyph: '🔥' },
  { id: 'triangle',        name: 'Triangle Geo',        kind: 'Geometric',  price: 140, glyph: '△' },
  { id: 'hexagon',         name: 'Hexagon Geo',         kind: 'Geometric',  price: 160, glyph: '⬡' }
];

// --- Color Palette (20 swatches in 5 groups) ---
const colorPalette = [
  // Neutrals
  { name: 'Chalk',     hex: '#F8F7F3', group: 'Neutrals' },
  { name: 'Bone',      hex: '#E9E2D4', group: 'Neutrals' },
  { name: 'Graphite',  hex: '#3A3A3A', group: 'Neutrals' },
  { name: 'Onyx',      hex: '#171717', group: 'Neutrals' },
  // Warm
  { name: 'VAYELLE Orange', hex: '#F36B38', group: 'Warm' },
  { name: 'Saffron',   hex: '#F2B33D', group: 'Warm' },
  { name: 'Brick',     hex: '#B5452B', group: 'Warm' },
  { name: 'Blush',     hex: '#EFB7A8', group: 'Warm' },
  // Cool
  { name: 'Glacier',   hex: '#BFD7E6', group: 'Cool' },
  { name: 'Cobalt',    hex: '#2F55A4', group: 'Cool' },
  { name: 'Navy',      hex: '#1D2A44', group: 'Cool' },
  { name: 'Mint',      hex: '#A9D8C0', group: 'Cool' },
  // Earth
  { name: 'Olive',     hex: '#6B6B3A', group: 'Earth' },
  { name: 'Tan',       hex: '#C9A877', group: 'Earth' },
  { name: 'Cocoa',     hex: '#4A2C1D', group: 'Earth' },
  { name: 'Sage',      hex: '#9DAE8F', group: 'Earth' },
  // Bold
  { name: 'Volt',      hex: '#D7F23D', group: 'Bold' },
  { name: 'Cherry',    hex: '#C8102E', group: 'Bold' },
  { name: 'Ultra',     hex: '#5B3FD9', group: 'Bold' },
  { name: 'Teal',      hex: '#0E8C8C', group: 'Bold' }
];

// --- Accessible Palette (8 Okabe–Ito colors for color-blind users) ---
const accessiblePalette = [
  { name: 'Black',      hex: '#000000', pattern: 'solid',    icon: '■' },
  { name: 'Orange',     hex: '#E69F00', pattern: 'stripes',  icon: '◐' },
  { name: 'Sky Blue',   hex: '#56B4E9', pattern: 'dots',     icon: '○' },
  { name: 'Bluish Green', hex: '#009E73', pattern: 'grid',   icon: '◇' },
  { name: 'Yellow',     hex: '#F0E442', pattern: 'zigzag',   icon: '△' },
  { name: 'Blue',       hex: '#0072B2', pattern: 'cross',    icon: '✦' },
  { name: 'Vermillion', hex: '#D55E00', pattern: 'waves',    icon: '◈' },
  { name: 'Reddish Purple', hex: '#CC79A7', pattern: 'rings', icon: '◎' }
];

// --- Default Shoe Part Colors ---
const defaultColors = {
  upper:  '#F8F7F3',
  toe:    '#E9E2D4',
  heel:   '#F36B38',
  sole:   '#FFFFFF',
  laces:  '#F8F7F3',
  stripe: '#171717'
};

// --- Community Designs (sample data) ---
const communityDesigns = [
  { id: 'dhaka-dusk',    name: 'Dhaka Dusk',    creator: 'Athoy R.',    likes: 142, shoe: 'urban-runner',  colors: { upper: '#1D2A44', toe: '#F36B38', heel: '#F2B33D', sole: '#171717', laces: '#F8F7F3', stripe: '#F36B38' }, material: 'leather', sole: 'chunky', decos: ['star-patch'], remixOf: null },
  { id: 'tea-garden',    name: 'Tea Garden',    creator: 'Miftahul P.', likes: 98,  shoe: 'cloud-street',  colors: { upper: '#9DAE8F', toe: '#E9E2D4', heel: '#6B6B3A', sole: '#F8F7F3', laces: '#E9E2D4', stripe: '#4A2C1D' }, material: 'canvas', sole: 'flat', decos: [], remixOf: null },
  { id: 'glacier-run',   name: 'Glacier Run',   creator: 'Diya Z.',     likes: 176, shoe: 'cloud-street',  colors: { upper: '#BFD7E6', toe: '#F8F7F3', heel: '#2F55A4', sole: '#F8F7F3', laces: '#BFD7E6', stripe: '#0E8C8C' }, material: 'mesh', sole: 'sport', decos: ['racing-stripe'], remixOf: null },
  { id: 'volt-rush',     name: 'Volt Rush',     creator: 'Khairul B.',  likes: 215, shoe: 'retro-flex',    colors: { upper: '#171717', toe: '#D7F23D', heel: '#D7F23D', sole: '#171717', laces: '#D7F23D', stripe: '#D7F23D' }, material: 'synthetic', sole: 'sport', decos: ['lightning-patch', 'racing-stripe'], remixOf: null },
  { id: 'cocoa-office',  name: 'Cocoa Office',  creator: 'Athoy R.',    likes: 87,  shoe: 'urban-formal',  colors: { upper: '#4A2C1D', toe: '#4A2C1D', heel: '#C9A877', sole: '#171717', laces: '#4A2C1D', stripe: '#C9A877' }, material: 'leather', sole: 'flat', decos: [], remixOf: null },
  { id: 'cherry-pop',    name: 'Cherry Pop',    creator: 'Diya Z.',     likes: 163, shoe: 'mono-classic',  colors: { upper: '#C8102E', toe: '#171717', heel: '#F8F7F3', sole: '#171717', laces: '#F8F7F3', stripe: '#C8102E' }, material: 'suede', sole: 'cupsole', decos: ['star-patch', 'checker'], remixOf: null }
];

// --- Size Chart (EU / UK / US / cm) ---
const sizeChart = [
  { eu: 36, uk: 3.5, us: 5,   cm: 22.5 },
  { eu: 37, uk: 4,   us: 5.5, cm: 23   },
  { eu: 38, uk: 5,   us: 6.5, cm: 24   },
  { eu: 39, uk: 5.5, us: 7,   cm: 24.5 },
  { eu: 40, uk: 6.5, us: 7.5, cm: 25.5 },
  { eu: 41, uk: 7,   us: 8,   cm: 26   },
  { eu: 42, uk: 8,   us: 9,   cm: 27   },
  { eu: 43, uk: 8.5, us: 9.5, cm: 27.5 },
  { eu: 44, uk: 9.5, us: 10.5, cm: 28.5 },
  { eu: 45, uk: 10,  us: 11,  cm: 29   },
  { eu: 46, uk: 11,  us: 12,  cm: 29.5 }
];

// --- Helper: Look up a shoe by ID ---
function getShoe(id) {
  return shoes.find(s => s.id === id) || null;
}

// --- Helper: Look up a material by ID ---
function getMaterial(id) {
  return materials.find(m => m.id === id) || null;
}

// --- Helper: Look up a sole by ID ---
function getSole(id) {
  return soles.find(s => s.id === id) || null;
}

// --- Helper: Look up a decoration by ID ---
function getDecoration(id) {
  return decorations.find(d => d.id === id) || null;
}

// --- Helper: Estimate shoe size from foot length (cm) ---
function estimateSize(footLengthCm) {
  let closest = sizeChart[0];
  let minDiff = Math.abs(footLengthCm - closest.cm);
  for (const row of sizeChart) {
    const diff = Math.abs(footLengthCm - row.cm);
    if (diff < minDiff) {
      minDiff = diff;
      closest = row;
    }
  }
  return closest;
}
