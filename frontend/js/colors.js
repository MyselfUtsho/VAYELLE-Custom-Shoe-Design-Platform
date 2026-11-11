/* ============================================
   VAYELLE — Color Utility Functions
   Complementary, analogous, and triadic color
   harmony calculations + dominant color extraction.
   ============================================ */

// --- Convert hex to RGB ---
function hexToRgb(hex) {
  hex = hex.replace('#', '');
  return {
    r: parseInt(hex.substring(0, 2), 16),
    g: parseInt(hex.substring(2, 4), 16),
    b: parseInt(hex.substring(4, 6), 16)
  };
}

// --- Convert RGB to hex ---
function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v =>
    Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')
  ).join('');
}

// --- Convert RGB to HSL ---
function rgbToHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return { h: h * 360, s: s * 100, l: l * 100 };
}

// --- Convert HSL to RGB ---
function hslToRgb(h, s, l) {
  h /= 360; s /= 100; l /= 100;

  if (s === 0) {
    const val = Math.round(l * 255);
    return { r: val, g: val, b: val };
  }

  function hue2rgb(p, q, t) {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  }

  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;

  return {
    r: Math.round(hue2rgb(p, q, h + 1/3) * 255),
    g: Math.round(hue2rgb(p, q, h) * 255),
    b: Math.round(hue2rgb(p, q, h - 1/3) * 255)
  };
}

// --- Get the complementary color (opposite on color wheel) ---
function getComplementary(hex) {
  const rgb = hexToRgb(hex);
  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
  hsl.h = (hsl.h + 180) % 360;
  const comp = hslToRgb(hsl.h, hsl.s, hsl.l);
  return rgbToHex(comp.r, comp.g, comp.b);
}

// --- Get analogous colors (±30° on color wheel) ---
function getAnalogous(hex) {
  const rgb = hexToRgb(hex);
  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);

  const c1 = hslToRgb((hsl.h + 30) % 360, hsl.s, hsl.l);
  const c2 = hslToRgb((hsl.h + 330) % 360, hsl.s, hsl.l);

  return [
    rgbToHex(c1.r, c1.g, c1.b),
    rgbToHex(c2.r, c2.g, c2.b)
  ];
}

// --- Get triadic colors (±120° on color wheel) ---
function getTriadic(hex) {
  const rgb = hexToRgb(hex);
  const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);

  const c1 = hslToRgb((hsl.h + 120) % 360, hsl.s, hsl.l);
  const c2 = hslToRgb((hsl.h + 240) % 360, hsl.s, hsl.l);

  return [
    rgbToHex(c1.r, c1.g, c1.b),
    rgbToHex(c2.r, c2.g, c2.b)
  ];
}

// --- Determine if a color is light or dark (for text contrast) ---
function isLightColor(hex) {
  const rgb = hexToRgb(hex);
  const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
  return brightness > 128;
}

// --- Extract dominant colors from an image using canvas ---
// Returns top N hex colors by pixel frequency
function extractDominantColors(imgSrc, n, callback) {
  n = n || 5;
  const img = new Image();
  img.crossOrigin = 'anonymous';

  img.onload = function() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    // Resize to small for faster processing
    const w = 80;
    const h = Math.round((img.height / img.width) * w);
    canvas.width = w;
    canvas.height = h;
    ctx.drawImage(img, 0, 0, w, h);

    const imageData = ctx.getImageData(0, 0, w, h).data;
    const buckets = {};

    // Quantize each pixel to 5-bit color and count
    for (let i = 0; i < imageData.length; i += 4) {
      const r = imageData[i] & 0xF8;
      const g = imageData[i + 1] & 0xF8;
      const b = imageData[i + 2] & 0xF8;
      const key = rgbToHex(r, g, b);
      buckets[key] = (buckets[key] || 0) + 1;
    }

    // Sort by frequency and return top N
    const sorted = Object.entries(buckets)
      .sort((a, b) => b[1] - a[1])
      .slice(0, n)
      .map(entry => entry[0]);

    callback(sorted);
  };

  img.onerror = function() {
    // Fallback colors if image can't be loaded
    callback(['#D9C7A8', '#3A3A3A', '#6B6B3A', '#F2EFE8', '#8A8A8A']);
  };

  img.src = imgSrc;
}

// --- Classify outfit style from dominant colors ---
// Uses average saturation and luminance to determine style category
function classifyStyle(hexColors) {
  let totalSat = 0, totalLum = 0;

  for (const hex of hexColors) {
    const rgb = hexToRgb(hex);
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    totalSat += hsl.s;
    totalLum += hsl.l;
  }

  const avgSat = totalSat / hexColors.length;
  const avgLum = totalLum / hexColors.length;

  if (avgLum < 35 && avgSat < 30) return 'Formal';
  if (avgSat > 50) return 'Streetwear';
  return 'Casual';
}

// --- Generate shoe color recommendations based on outfit colors ---
function getShoeRecommendations(outfitColors) {
  const recommendations = [];

  for (const color of outfitColors.slice(0, 3)) {
    const comp = getComplementary(color);
    const analogous = getAnalogous(color);
    recommendations.push({
      outfitColor: color,
      suggested: [comp, analogous[0], analogous[1]]
    });
  }

  return recommendations;
}
