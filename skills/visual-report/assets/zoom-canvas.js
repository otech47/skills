(function () {
  document.querySelectorAll('.zoom').forEach(function (z) {
    var view = z.querySelector('.zoom-view'), inner = z.querySelector('.zoom-inner');
    var W = +z.dataset.w, H = +z.dataset.h, MAX = +(z.dataset.max || 4), MIN = +(z.dataset.min || 0.2), PAD = +(z.dataset.pad || 14);
    var s = 1, tx = 0, ty = 0, fitS = 1, atFit = true, liveT = 0, raf = 0, box = null;
    var fitBtn = z.querySelector('[data-z="fit"]'), level = z.querySelector('.zoom-level');
    if (!view.hasAttribute('tabindex')) view.tabIndex = 0;
    if (!view.hasAttribute('aria-label')) view.setAttribute('aria-label', 'diagram, drag to pan, arrow keys pan, plus and minus zoom, 0 fits');
    function rect() { if (!box) box = view.getBoundingClientRect(); return box; }
    function vw() { return rect().width; }
    function vh() { return rect().height; }
    // content may leave the box, but a quarter of the box always stays covered
    function clampAxis(t, size, len) {
      var m = len * 0.75, a = len - m, b = m - size;
      return Math.min(Math.max(a, b), Math.max(Math.min(a, b), t));
    }
    function paint() {
      raf = 0;
      inner.style.transform = 'translate3d(' + tx.toFixed(2) + 'px,' + ty.toFixed(2) + 'px,0) scale(' + s.toFixed(4) + ')';
      if (fitBtn) fitBtn.setAttribute('aria-pressed', atFit ? 'true' : 'false');
      if (level) level.textContent = Math.round(s * 100) + '%';
      view.style.touchAction = fits() ? 'auto' : 'none';
    }
    function apply() {
      tx = clampAxis(tx, W * s, vw()); ty = clampAxis(ty, H * s, vh());
      if (!raf) raf = requestAnimationFrame(paint);
    }
    function live() {
      view.classList.add('live'); clearTimeout(liveT);
      liveT = setTimeout(function () { view.classList.remove('live'); }, 160);
    }
    function fit() {
      box = null;
      var w = view.clientWidth;
      var floor = +(z.dataset.minFit || (w < 700 ? 0.6 : 0));
      fitS = Math.max(MIN, Math.min(1, Math.max((w - 2 * PAD) / W, floor)));
      view.style.height = Math.round(H * fitS + 2 * PAD) + 'px';
      box = null;
      s = fitS; tx = Math.max(PAD, (vw() - W * s) / 2); ty = PAD; atFit = true; apply();
    }
    function zoomAt(f, cx, cy) {
      var ns = Math.max(MIN, Math.min(MAX, s * f));
      if (Math.abs(ns - s) < 1e-6) return false;
      tx = cx - (cx - tx) * ns / s; ty = cy - (cy - ty) * ns / s; s = ns; atFit = false; apply(); return true;
    }
    function panBy(dx, dy) {
      var ox = tx, oy = ty; tx += dx; ty += dy; atFit = false; apply();
      return Math.abs(tx - ox) > 0.5 || Math.abs(ty - oy) > 0.5;
    }
    function fits() { return W * s <= vw() + 0.5 && H * s <= vh() + 0.5; }
    function local(e) { var r = rect(); return [e.clientX - r.left, e.clientY - r.top]; }
    z.querySelectorAll('button[data-z]').forEach(function (b) {
      b.addEventListener('click', function () {
        box = null;
        if (b.dataset.z === 'fit') fit(); else zoomAt(b.dataset.z === 'in' ? 1.25 : 0.8, vw() / 2, vh() / 2);
      });
    });
    view.addEventListener('wheel', function (e) {
      if (!(e.ctrlKey || e.metaKey)) return;
      box = null; var q = local(e);
      e.preventDefault(); live(); zoomAt(Math.exp(-Math.max(-40, Math.min(40, e.deltaY)) * 0.01), q[0], q[1]);
    }, { passive: false });
    view.addEventListener('dblclick', function (e) {
      box = null; var p = local(e);
      if (e.shiftKey) { if (!zoomAt(0.5, p[0], p[1])) fit(); } else if (s >= MAX * 0.99) fit(); else zoomAt(2, p[0], p[1]);
    });
    view.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 240 : 60, k = e.key, done = true;
      box = null;
      if (k === 'ArrowLeft') panBy(step, 0); else if (k === 'ArrowRight') panBy(-step, 0);
      else if (k === 'ArrowUp') panBy(0, step); else if (k === 'ArrowDown') panBy(0, -step);
      else if (k === '+' || k === '=') zoomAt(1.25, vw() / 2, vh() / 2);
      else if (k === '-' || k === '_') zoomAt(0.8, vw() / 2, vh() / 2);
      else if (k === '0') fit(); else done = false;
      if (done) e.preventDefault();
    });
    var pts = new Map(), last = null;
    function gesture() {
      var a = Array.from(pts.values()), c = a.length;
      var mx = a.reduce(function (t, p) { return t + p[0]; }, 0) / c, my = a.reduce(function (t, p) { return t + p[1]; }, 0) / c;
      return { x: mx, y: my, d: c > 1 ? Math.hypot(a[0][0] - a[1][0], a[0][1] - a[1][1]) : 0 };
    }
    view.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      e.preventDefault(); box = null;
      try { view.setPointerCapture(e.pointerId); } catch (err) {}
      pts.set(e.pointerId, local(e)); last = gesture();
      view.classList.add('drag', 'live');
    });
    view.addEventListener('pointermove', function (e) {
      if (!pts.has(e.pointerId)) return;
      pts.set(e.pointerId, local(e)); var g = gesture();
      if (g.d && last.d) zoomAt(g.d / last.d, g.x, g.y);
      panBy(g.x - last.x, g.y - last.y); last = g;
    });
    function up(e) {
      if (!pts.delete(e.pointerId)) return;
      if (pts.size) last = gesture(); else { last = null; view.classList.remove('drag', 'live'); }
    }
    view.addEventListener('pointerup', up); view.addEventListener('pointercancel', up); view.addEventListener('lostpointercapture', up);
    var gs = 1;
    view.addEventListener('gesturestart', function (e) { if (!pts.size) { e.preventDefault(); gs = e.scale; } });
    view.addEventListener('gesturechange', function (e) {
      if (pts.size) return;
      e.preventDefault(); live(); var p = local(e); zoomAt(e.scale / gs, p[0], p[1]); gs = e.scale;
    });
    view.addEventListener('gestureend', function (e) { e.preventDefault(); });
    function refit() { box = null; if (atFit) fit(); else apply(); }
    window.addEventListener('resize', refit);
    if (window.ResizeObserver) { var lastW = 0; new ResizeObserver(function () { var w = view.clientWidth; if (w && w !== lastW) { lastW = w; refit(); } }).observe(view); }
    window.addEventListener('scroll', function () { box = null; }, { passive: true });
    fit();
  });
})();
