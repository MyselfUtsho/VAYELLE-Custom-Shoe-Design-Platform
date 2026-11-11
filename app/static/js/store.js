/* ============================================
   VAYELLE — State Management (localStorage)
   Replaces Zustand with a simple pub/sub store
   that persists state to localStorage.
   ============================================ */

const STORE_KEY = 'vayelle-state-v1';

// --- Default state shape ---
const defaultState = {
  current: {
    shoeId: null,
    materialId: null,
    soleId: null,
    decos: [],            // Array of { uid, id, x, y, scale }
    colors: { ...defaultColors },
    hidden: {}            // { layerName: true } to hide layers
  },
  saved: [],              // Array of saved designs
  favorites: [],          // Array of shoe IDs
  likes: [],              // Array of community design IDs
  orders: [],             // Array of demo orders
  user: null,             // { name, email } or null
  usualSize: null,        // Saved preferred shoe size (EU)
  outfit: null            // Base64 string of uploaded outfit image
};

// --- Load state from localStorage or use defaults ---
function loadState() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      // Merge with defaults so new keys are added on updates
      return deepMerge(defaultState, parsed);
    }
  } catch (e) {
    console.warn('VAYELLE: Could not load saved state, using defaults.');
  }
  return JSON.parse(JSON.stringify(defaultState));
}

// --- Simple deep merge (target values take priority if they exist) ---
function deepMerge(defaults, overrides) {
  const result = { ...defaults };
  for (const key of Object.keys(overrides)) {
    if (
      overrides[key] !== null &&
      typeof overrides[key] === 'object' &&
      !Array.isArray(overrides[key]) &&
      typeof defaults[key] === 'object' &&
      !Array.isArray(defaults[key])
    ) {
      result[key] = deepMerge(defaults[key], overrides[key]);
    } else {
      result[key] = overrides[key];
    }
  }
  return result;
}

// --- The store object (module-scoped singleton) ---
let state = loadState();
let listeners = [];

// --- Save state to localStorage ---
function saveState() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn('VAYELLE: Could not save state to localStorage.');
  }
}

// --- Get the full current state ---
function getState() {
  return state;
}

// --- Get the current design being edited ---
function getCurrentDesign() {
  return state.current;
}

// --- Update state with partial changes and save ---
function setState(partial) {
  state = { ...state, ...partial };
  saveState();
  notifyListeners();
}

// --- Update the current design with partial changes ---
function updateDesign(partial) {
  state.current = { ...state.current, ...partial };
  saveState();
  notifyListeners();
}

// --- Update a specific color on the current design ---
function setColor(part, hex) {
  state.current.colors = { ...state.current.colors, [part]: hex };
  saveState();
  notifyListeners();
}

// --- Set the selected shoe ---
function selectShoe(shoeId) {
  state.current.shoeId = shoeId;
  saveState();
  notifyListeners();
}

// --- Set the selected material ---
function selectMaterial(materialId) {
  state.current.materialId = materialId;
  saveState();
  notifyListeners();
}

// --- Set the selected sole ---
function selectSole(soleId) {
  state.current.soleId = soleId;
  saveState();
  notifyListeners();
}

// --- Add a decoration to the current design ---
function addDecoration(decoId) {
  const uid = 'deco-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  state.current.decos = [
    ...state.current.decos,
    { uid, id: decoId, x: 30 + Math.random() * 40, y: 20 + Math.random() * 40, scale: 1 }
  ];
  saveState();
  notifyListeners();
}

// --- Remove a decoration by unique ID ---
function removeDecoration(uid) {
  state.current.decos = state.current.decos.filter(d => d.uid !== uid);
  saveState();
  notifyListeners();
}

// --- Toggle a layer's visibility ---
function toggleLayer(layerName) {
  const hidden = { ...state.current.hidden };
  hidden[layerName] = !hidden[layerName];
  state.current.hidden = hidden;
  saveState();
  notifyListeners();
}

// --- Calculate total price of the current design ---
function calculatePrice() {
  const design = state.current;
  let total = 0;

  // Base shoe price
  if (design.shoeId) {
    const shoe = getShoe(design.shoeId);
    if (shoe) total += shoe.price;
  }

  // Material cost
  if (design.materialId) {
    const mat = getMaterial(design.materialId);
    if (mat) total += mat.price;
  }

  // Sole cost
  if (design.soleId) {
    const sole = getSole(design.soleId);
    if (sole) total += sole.price;
  }

  // Decoration costs
  if (design.decos && design.decos.length > 0) {
    const uniqueDecoIds = [...new Set(design.decos.map(d => d.id))];
    for (const decoId of uniqueDecoIds) {
      const deco = getDecoration(decoId);
      if (deco) total += deco.price;
    }
  }

  return total;
}

// --- Save the current design to the saved list ---
function saveCurrentDesign(name) {
  const design = {
    id: 'design-' + Date.now(),
    name: name || 'Design #' + (state.saved.length + 1),
    date: new Date().toISOString(),
    shoeId: state.current.shoeId,
    materialId: state.current.materialId,
    soleId: state.current.soleId,
    decos: [...state.current.decos],
    colors: { ...state.current.colors },
    totalPrice: calculatePrice()
  };
  state.saved = [design, ...state.saved];
  saveState();
  notifyListeners();
  return design;
}

// --- Remove a saved design ---
function removeSavedDesign(designId) {
  state.saved = state.saved.filter(d => d.id !== designId);
  saveState();
  notifyListeners();
}

// --- Load a saved design into the current editor ---
function loadSavedDesign(designId) {
  const design = state.saved.find(d => d.id === designId);
  if (design) {
    state.current = {
      shoeId: design.shoeId,
      materialId: design.materialId,
      soleId: design.soleId,
      decos: [...design.decos],
      colors: { ...design.colors },
      hidden: {}
    };
    saveState();
    notifyListeners();
  }
}

// --- Toggle a shoe as favorite ---
function toggleFavorite(shoeId) {
  if (state.favorites.includes(shoeId)) {
    state.favorites = state.favorites.filter(id => id !== shoeId);
  } else {
    state.favorites = [...state.favorites, shoeId];
  }
  saveState();
  notifyListeners();
}

// --- Check if a shoe is a favorite ---
function isFavorite(shoeId) {
  return state.favorites.includes(shoeId);
}

// --- Toggle a community design like ---
function toggleLike(designId) {
  if (state.likes.includes(designId)) {
    state.likes = state.likes.filter(id => id !== designId);
  } else {
    state.likes = [...state.likes, designId];
  }
  saveState();
  notifyListeners();
}

// --- Check if a community design is liked ---
function isLiked(designId) {
  return state.likes.includes(designId);
}

// --- Set the uploaded outfit image (base64) ---
function setOutfitImage(base64) {
  state.outfit = base64;
  saveState();
  notifyListeners();
}

// --- Set the user's usual size ---
function setUsualSize(euSize) {
  state.usualSize = euSize;
  saveState();
  notifyListeners();
}

// --- Add a demo order ---
function addOrder(order) {
  state.orders = [order, ...state.orders];
  saveState();
  notifyListeners();
}

// --- Set the user (demo login) ---
function setUser(user) {
  state.user = user;
  saveState();
  notifyListeners();
}

// --- Logout ---
function logoutUser() {
  state.user = null;
  saveState();
  notifyListeners();
}

// --- Reset the current design ---
function resetDesign() {
  state.current = JSON.parse(JSON.stringify(defaultState.current));
  saveState();
  notifyListeners();
}

// --- Pub/Sub: subscribe to state changes ---
function subscribe(listener) {
  listeners.push(listener);
  // Return an unsubscribe function
  return function unsubscribe() {
    listeners = listeners.filter(l => l !== listener);
  };
}

// --- Notify all listeners ---
function notifyListeners() {
  for (const listener of listeners) {
    try { listener(state); } catch (e) { console.error('Listener error:', e); }
  }
}
