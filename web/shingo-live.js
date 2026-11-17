/* Shingō live layer: machine behaviour for the print system.
   - Scramble: titles resolve from glyph noise, stepped, once per reveal.
   - Live readouts: seven-segment counters and countdowns re-render in place.
   - Coordinates: the last digits of live coordinates drift.
   - Transitions: a hazard band wipes along the one diagonal between views.
   - HUD: a bracket reticle snaps to data under the pointer with a callout.
   Everything is stepped (no easing) and does nothing under reduced motion.
   Content is complete at rest: nothing is hidden waiting for script. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- seven-segment geometry (mirrors tools/build.py seg7) ---------- */
  var SEG = { '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg', '-': 'g', ' ': '' };
  var W = 44, H = 60, T = 5.6, G = 1.3, GAP = 9;
  function hseg(x0, x1, yc) { return [[x0, yc], [x0 + T / 2, yc - T / 2], [x1 - T / 2, yc - T / 2], [x1, yc], [x1 - T / 2, yc + T / 2], [x0 + T / 2, yc + T / 2]]; }
  function vseg(xc, y0, y1) { return [[xc, y0], [xc + T / 2, y0 + T / 2], [xc + T / 2, y1 - T / 2], [xc, y1], [xc - T / 2, y1 - T / 2], [xc - T / 2, y0 + T / 2]]; }
  var x0 = T / 2 + G, x1 = W - T / 2 - G, m = H / 2;
  var S = { a: hseg(x0, x1, T / 2), g: hseg(x0, x1, m), d: hseg(x0, x1, H - T / 2), f: vseg(T / 2, T / 2 + G, m - G), b: vseg(W - T / 2, T / 2 + G, m - G), e: vseg(T / 2, m + G, H - T / 2 - G), c: vseg(W - T / 2, m + G, H - T / 2 - G) };
  function segInner(text, hot) {
    var out = '', x = 0;
    for (var i = 0; i < text.length; i++) {
      var ch = text[i], cls = hot.indexOf(i) >= 0 ? 'hot' : 'on';
      if (ch === '.') { out += '<rect class="' + cls + '" x="' + x + '" y="' + (H - 7) + '" width="7" height="7"/>'; x += 7 + GAP; continue; }
      if (ch === ':') { out += '<rect class="' + cls + '" x="' + x + '" y="' + (H * .28).toFixed(1) + '" width="7" height="7"/><rect class="' + cls + '" x="' + x + '" y="' + (H * .64).toFixed(1) + '" width="7" height="7"/>'; x += 7 + GAP; continue; }
      var lit = SEG[ch] || '';
      for (var k in S) if (lit.indexOf(k) >= 0) out += '<polygon class="' + cls + '" points="' + S[k].map(function (p) { return (p[0] + x).toFixed(2) + ',' + p[1].toFixed(2); }).join(' ') + '"/>';
      x += W + GAP;
    }
    return out;
  }
  function setSeg(svg, text) {
    var hot = (svg.getAttribute('data-hot') || '').split(',').filter(Boolean).map(Number);
    svg.querySelector('g').innerHTML = segInner(text, hot);
    svg.setAttribute('aria-label', text);
  }

  /* ---------- live readouts ---------- */
  function pad(n, w) { n = String(n); while (n.length < w) n = '0' + n; return n; }
  function liveReadouts() {
    document.querySelectorAll('svg.seg7.live-down').forEach(function (svg) {
      var start = svg.getAttribute('aria-label'), p = start.split(':'), t = (+p[0]) * 60 + (+p[1]), t0 = t;
      setInterval(function () { t = t > 0 ? t - 1 : t0; setSeg(svg, pad(Math.floor(t / 60), 2) + ':' + pad(t % 60, 2)); }, 1000);
    });
    document.querySelectorAll('svg.seg7.live-up').forEach(function (svg) {
      var v = parseInt(svg.getAttribute('aria-label'), 10), len = String(v).length;
      setInterval(function () { if (Math.random() < .5) { v += 1 + Math.floor(Math.random() * 3); setSeg(svg, pad(v % Math.pow(10, len), len)); } }, 1400);
    });
    document.querySelectorAll('.live-coord').forEach(function (el) {
      var base = el.textContent;
      setInterval(function () {
        el.textContent = base.replace(/(\d+\.)(\d)(\d)/g, function (_, a, b, c) { return a + b + ((+c + Math.floor(Math.random() * 3) + 9) % 10); });
      }, 1600);
    });
  }

  /* ---------- scramble ---------- */
  var NOISE = '/X#▮▚09-+';
  function scramble(el) {
    if (el.__sc) return; el.__sc = 1;
    var nodes = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (w.nextNode()) if (w.currentNode.nodeValue.trim()) nodes.push([w.currentNode, w.currentNode.nodeValue]);
    var steps = 9, i = 0;
    var id = setInterval(function () {
      i++;
      nodes.forEach(function (n) {
        var src = n[1], keep = Math.floor(src.length * i / steps), s = '';
        for (var k = 0; k < src.length; k++) s += (k < keep || src[k] === ' ') ? src[k] : NOISE[(k * 7 + i * 3) % NOISE.length];
        n[0].nodeValue = s;
      });
      if (i >= steps) { clearInterval(id); nodes.forEach(function (n) { n[0].nodeValue = n[1]; }); el.__sc = 0; }
    }, 45);
  }
  function scrambleScreen(scr) { scr.querySelectorAll('.u-title, .sg-display').forEach(scramble); }

  /* ---------- transition: hazard wipe ---------- */
  function wipe(scr, mid) {
    var band = document.createElement('i'); band.className = 'sg-wipe'; band.setAttribute('aria-hidden', 'true');
    scr.appendChild(band);
    setTimeout(function () { if (mid) mid(); }, 240);
    setTimeout(function () { band.remove(); }, 520);
  }

  /* ---------- HUD reticle ---------- */
  var HUD_T = '.stats3 > div, .nframe, .zones > .cells, .row, .set, .dataplate, .ticket, .pcard, .chamfer.scope, .smx > div, .lamps, .keypad .key, .map';
  function label(el) {
    var t = (el.getAttribute('data-hud') || el.innerText || '').replace(/\s+/g, ' ').trim().toUpperCase();
    return t.length > 34 ? t.slice(0, 33) + '…' : t;
  }
  function hud(scr) {
    var box = document.createElement('div'); box.className = 'sg-hud'; box.hidden = true; box.setAttribute('aria-hidden', 'true');
    box.innerHTML = '<i class="sg-hud-r brackets"></i><b class="sg-hud-l"></b>';
    scr.appendChild(box);
    var cur = null;
    function show(t) {
      if (t === cur) return; cur = t;
      if (!t) { box.hidden = true; return; }
      var r = t.getBoundingClientRect(), s = scr.getBoundingClientRect(), z = parseFloat(getComputedStyle(scr.closest('.phone')).zoom) || 1;
      var x = (r.left - s.left) / z, y = (r.top - s.top) / z, w = r.width / z, h = r.height / z;
      box.style.cssText = 'left:' + (x - 4) + 'px;top:' + (y - 4) + 'px;width:' + (w + 8) + 'px;height:' + (h + 8) + 'px';
      box.querySelector('b').textContent = label(t);
      box.classList.toggle('flip', y < 120);
      box.hidden = false;
    }
    scr.addEventListener('pointermove', function (e) { var t = e.target.closest(HUD_T); show(t && scr.contains(t) ? t : null); });
    scr.addEventListener('pointerleave', function () { show(null); });
  }

  /* ---------- wire up ---------- */
  document.querySelectorAll('.scr').forEach(function (scr) {
    hud(scr);
    scr.querySelectorAll('.tabbar a').forEach(function (a) {
      a.addEventListener('click', function () {
        if (reduce) { scr.querySelectorAll('.tabbar a').forEach(function (x) { x.toggleAttribute('aria-current', x === a); }); return; }
        wipe(scr, function () { scr.querySelectorAll('.tabbar a').forEach(function (x) { x.toggleAttribute('aria-current', x === a); }); scrambleScreen(scr); });
      });
    });
  });
  document.querySelectorAll('.mo-wipe').forEach(function (box) {
    var views = box.querySelectorAll('.mo-view'), i = 0;
    if (reduce) return;
    setInterval(function () { wipe(box, function () { views[i].hidden = true; i = (i + 1) % views.length; views[i].hidden = false; scrambleScreen(box); }); }, 2600);
  });
  if (reduce) return;
  liveReadouts();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { scrambleScreen(e.target); io.unobserve(e.target); } }); }, { threshold: .5 });
    document.querySelectorAll('.scr').forEach(function (s) { io.observe(s); });
  }
})();
