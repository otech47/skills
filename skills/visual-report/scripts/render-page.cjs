module.exports = function inspectPage({ geometry }) {
  const checks = [];
  const add = (name, status, detail, extra = {}) => checks.push({ name, status, detail, ...extra });
  const visible = e => {
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    return s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) !== 0 && r.width > 0 && r.height > 0 && !e.closest('defs, [hidden]') && e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
  };
  const rect = e => {
    const r = e.getBoundingClientRect();
    return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height };
  };
  const label = e => e.id ? `#${e.id}` : `${e.tagName.toLowerCase()} ${JSON.stringify((e.textContent || '').trim().slice(0, 70))}`;
  const pageWidth = document.documentElement.scrollWidth;
  const pageHeight = document.documentElement.scrollHeight;
  const width = document.documentElement.clientWidth;
  if (!Number.isFinite(width) || width <= 0 || !Number.isFinite(pageHeight) || pageHeight <= 0) throw new Error('invalid or missing page dimensions');
  add('page-overflow', pageWidth > width + 1 ? 'fail' : 'pass', `page ${pageWidth}px, viewport ${width}px`);
  const dash = String.fromCodePoint(8211, 8212);
  add('rendered-dashes', [...dash].some(c => document.documentElement.textContent.includes(c)) ? 'fail' : 'pass', 'decoded page text checked for forbidden dashes');

  const assets = new Set();
  const external = value => value && !/^(data:|blob:|#)/i.test(value.trim());
  const attributes = [['script[src]', 'src'], ['link[rel~="stylesheet"],link[rel~="preload"],link[rel~="modulepreload"],link[rel~="icon"]', 'href'], ['img[src],source[src],audio[src],video[src],iframe[src],embed[src],input[type="image"][src]', 'src'], ['video[poster]', 'poster'], ['object[data]', 'data'], ['svg image,svg use', 'href']];
  for (const [selector, attribute] of attributes) for (const e of document.querySelectorAll(selector)) {
    const value = e.getAttribute(attribute) || e.getAttribute(`xlink:${attribute}`);
    if (external(value)) assets.add(value);
  }
  for (const e of document.querySelectorAll('[srcset]')) {
    const values = e.getAttribute('srcset').match(/(?:^|\s|,)((?:https?:|file:|\/|\.\/|\.\.\/)[^\s,]+|[^\s,:]+\.(?:png|jpe?g|webp|avif|svg|gif))(?:\s|,|$)/gi) || [];
    for (const value of values) assets.add(value.trim().replace(/,$/, ''));
    if (e.currentSrc && external(e.currentSrc)) assets.add(e.currentSrc);
  }
  const cssUrls = text => {
    for (const match of text.matchAll(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)/gi)) {
      const value = (match[1] || match[2] || match[3] || '').trim();
      if (external(value)) assets.add(value);
    }
  };
  const rules = sheet => {
    let list;
    try { list = sheet.cssRules; } catch { return; }
    for (const rule of list || []) {
      if (rule.href && external(rule.href)) assets.add(rule.href);
      cssUrls(rule.style ? rule.style.cssText : rule.cssText);
      if (rule.cssRules) rules(rule);
    }
  };
  for (const sheet of document.styleSheets) rules(sheet);
  for (const e of document.querySelectorAll('[style]')) cssUrls(e.style.cssText);
  add('inline-assets', assets.size ? 'fail' : 'pass', assets.size ? [...assets].join('\n') : 'no non-inline assets referenced');
  const brokenImages = [...document.images].filter(e => !e.complete || !e.naturalWidth).map(label);
  add('images', brokenImages.length ? 'fail' : 'pass', brokenImages.length ? brokenImages.join(', ') : 'images decoded');
  const brokenFonts = [...document.fonts].filter(f => f.status === 'error').map(f => f.family);
  add('fonts', brokenFonts.length ? 'fail' : 'pass', brokenFonts.length ? brokenFonts.join(', ') : 'requested fonts loaded');

  for (const svg of document.querySelectorAll('.hero svg')) {
    if (!visible(svg) || svg.matches('[aria-hidden="true"]')) continue;
    const texts = [...svg.querySelectorAll('text')].filter(visible);
    const small = texts.filter(e => {
      const m = e.getScreenCTM();
      return m && parseFloat(getComputedStyle(e).fontSize) * Math.hypot(m.c, m.d) < 11;
    });
    add('hero-label-size', small.length ? 'warn' : 'pass', small.length ? `${small.map(label).join(', ')} renders below 11px` : 'hero label sizes checked', small.length ? { region: rect(svg) } : {});
  }

  const scrollables = [];
  for (const e of document.querySelectorAll('body *')) {
    if (!visible(e) || e instanceof SVGElement) continue;
    const s = getComputedStyle(e);
    const horizontal = /auto|scroll/.test(s.overflowX) && e.scrollWidth > e.clientWidth + 1;
    const vertical = /auto|scroll/.test(s.overflowY) && e.scrollHeight > e.clientHeight + 1;
    if (!horizontal && !vertical) continue;
    const index = scrollables.length;
    e.setAttribute('data-render-scroll-index', String(index));
    scrollables.push({ index, element: label(e), width: e.clientWidth, height: e.clientHeight, scrollWidth: e.scrollWidth, scrollHeight: e.scrollHeight, horizontal, vertical });
  }

  if (geometry) {
    const overlaps = (a, b) => a.x < b.x + b.width - 1 && a.x + a.width > b.x + 1 && a.y < b.y + b.height - 1 && a.y + a.height > b.y + 1;
    const ignored = e => e.closest('[data-render-ignore]')?.getAttribute('data-render-ignore')?.trim();
    const transform = (m, x, y) => ({ x: m.a * x + m.c * y + m.e + scrollX, y: m.b * x + m.d * y + m.f + scrollY });
    const intersects = (a, b, r) => {
      let low = 0, high = 1;
      for (const [origin, delta, min, max] of [[a.x, b.x - a.x, r.x, r.x + r.width], [a.y, b.y - a.y, r.y, r.y + r.height]]) {
        if (Math.abs(delta) < 1e-9) { if (origin < min || origin > max) return false; }
        else { const first = (min - origin) / delta, last = (max - origin) / delta; low = Math.max(low, Math.min(first, last)); high = Math.min(high, Math.max(first, last)); }
      }
      return low <= high;
    };
    const segments = e => {
      if (e.tagName === 'line') return [[{ x: e.x1.baseVal.value, y: e.y1.baseVal.value }, { x: e.x2.baseVal.value, y: e.y2.baseVal.value }]];
      if (e.tagName === 'polyline' || e.tagName === 'polygon') {
        const points = [...Array(e.points.numberOfItems)].map((_, i) => e.points.getItem(i));
        if (e.tagName === 'polygon' && points.length) points.push(points[0]);
        return points.slice(1).map((p, i) => [points[i], p]);
      }
      const d = e.getAttribute('d') || '';
      const commands = d.replace(/[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:e[-+]?\d+)?/gi, '').replace(/[\s,]/g, '');
      if (/[^mlhvz]/i.test(commands)) return null;
      const tokens = d.match(/[mlhvz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:e[-+]?\d+)?/gi) || [];
      let i = 0, command, point = { x: 0, y: 0 }, start = point;
      const out = [];
      while (i < tokens.length) {
        if (/^[a-z]$/i.test(tokens[i])) command = tokens[i++];
        if (!command) return null;
        const relative = command === command.toLowerCase(), op = command.toUpperCase();
        if (op === 'Z') { out.push([point, start]); point = start; command = null; continue; }
        const count = op === 'M' || op === 'L' ? 2 : 1;
        const values = tokens.slice(i, i + count).map(Number);
        if (values.length !== count || values.some(v => !Number.isFinite(v))) return null;
        i += count;
        const next = { ...point };
        if (op === 'H') next.x = values[0] + (relative ? point.x : 0);
        else if (op === 'V') next.y = values[0] + (relative ? point.y : 0);
        else { next.x = values[0] + (relative ? point.x : 0); next.y = values[1] + (relative ? point.y : 0); }
        if (op !== 'M') out.push([point, next]);
        else { start = next; command = relative ? 'l' : 'L'; }
        point = next;
      }
      return out;
    };
    for (const svg of document.querySelectorAll('svg')) {
      if (!visible(svg) || svg.closest('[aria-hidden="true"]') || ignored(svg)) continue;
      const texts = [...svg.querySelectorAll('text')].filter(e => e.ownerSVGElement === svg && visible(e) && !ignored(e) && e.textContent.trim());
      if (!texts.length) continue;
      const bounds = rect(svg);
      for (const text of texts) {
        const r = rect(text);
        if (r.x < bounds.x - 1 || r.y < bounds.y - 1 || r.x + r.width > bounds.x + bounds.width + 1 || r.y + r.height > bounds.y + bounds.height + 1) add('svg-text-clipping', 'warn', `${label(text)} extends outside its SVG viewport`, { elements: [label(text)], region: bounds, geometry: r });
      }
      for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
        const a = rect(texts[i]), b = rect(texts[j]);
        if (overlaps(a, b)) add('svg-label-overlap', 'warn', `${label(texts[i])} overlaps ${label(texts[j])}`, { elements: [label(texts[i]), label(texts[j])], region: bounds, geometry: [a, b] });
      }
      for (const edge of svg.querySelectorAll('line,polyline,polygon,path')) {
        if (edge.ownerSVGElement !== svg || edge.closest('defs,marker,clipPath,mask') || ignored(edge) || getComputedStyle(edge).stroke === 'none' || !edge.getScreenCTM()) continue;
        if (!edge.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) continue;
        const parsed = segments(edge);
        if (!parsed) { add('svg-edge-geometry', 'unsupported', `${label(edge)} has curved or unsupported path geometry`, { elements: [label(edge)] }); continue; }
        const m = edge.getScreenCTM(), margin = parseFloat(getComputedStyle(edge).strokeWidth) * Math.max(Math.hypot(m.a, m.b), Math.hypot(m.c, m.d)) / 2;
        for (const text of texts) {
          const r = rect(text), padded = { x: r.x - margin, y: r.y - margin, width: r.width + 2 * margin, height: r.height + 2 * margin };
          if (parsed.some(([a, b]) => intersects(transform(m, a.x, a.y), transform(m, b.x, b.y), padded))) add('svg-edge-crossing', 'warn', `${label(edge)} crosses ${label(text)}`, { elements: [label(edge), label(text)], region: bounds, geometry: padded });
        }
      }
    }
  } else add('svg-geometry', 'unsupported', 'experimental geometry checks require --geometry');
  const layout = [...document.querySelectorAll('main,h1,h2,h3,p,li,table,details,summary,svg:not([aria-hidden="true"]),svg text')].filter(visible).map(e => [e.tagName, ...Object.values(rect(e)).map(n => Math.round(n * 100) / 100)]);
  return { width, height: innerHeight, pageWidth, pageHeight, layout, theme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light', checks, scrollables };
};
