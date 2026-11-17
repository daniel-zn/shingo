/* Shingō live layer: machine behaviour for the print system.
   - Scramble: titles resolve from glyph noise, stepped, once per reveal.
   - Live readouts: seven-segment counters and countdowns re-render in place.
   - Coordinates: the last digits of live coordinates drift.
   - Transitions: a hazard band wipes along the one diagonal between views.
   - HUD: a bracket reticle snaps to data under the pointer with a callout.
   Everything is stepped (no easing) and does nothing under reduced motion.
   Content is complete at rest: nothing is hidden waiting for script.
   Scope: .scr (phone screen), .con (console) or any element with data-sg-live.
   API: window.shingo.{telex(stack, state, msg, time), wipe(el, fn), scramble(el)}. */
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
    while (w.nextNode()) if (w.currentNode.nodeValue.trim()) nodes.push({ n: w.currentNode, src: w.currentNode.nodeValue });
    // each character locks at its own random moment; the whole title takes 320–720 ms
    var total = 320 + Math.random() * 400, t0 = performance.now();
    nodes.forEach(function (o) {
      o.lock = Array.prototype.map.call(o.src, function () { return total * (.15 + .85 * Math.pow(Math.random(), .8)); });
      o.cur = Array.prototype.map.call(o.src, function () { return NOISE[Math.floor(Math.random() * NOISE.length)]; });
    });
    function frame() {
      var t = performance.now() - t0, done = true;
      nodes.forEach(function (o) {
        var s = '';
        for (var k = 0; k < o.src.length; k++) {
          var c = o.src[k];
          if (c === ' ' || t >= o.lock[k]) { s += c; continue; }
          done = false;
          if (Math.random() < .45) o.cur[k] = NOISE[Math.floor(Math.random() * NOISE.length)];   // irregular flicker
          s += o.cur[k];
        }
        o.n.nodeValue = s;
      });
      if (done) { nodes.forEach(function (o) { o.n.nodeValue = o.src; }); el.__sc = 0; return; }
      setTimeout(frame, 28 + Math.random() * 52);   // uneven frame rate, 28–80 ms
    }
    frame();
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
  var HUD_T = '.stable tbody tr, .stats3 > div, .nframe, .zones > .cells, .row, .set, .dataplate, .ticket, .pcard, .chamfer.scope, .smx > div, .lamps, .keypad .key, .map';
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
      var r = t.getBoundingClientRect(), s = scr.getBoundingClientRect(), ph = scr.closest('.phone'), z = (ph && parseFloat(getComputedStyle(ph).zoom)) || 1;
      var x = (r.left - s.left) / z, y = (r.top - s.top) / z, w = r.width / z, h = r.height / z;
      box.style.cssText = 'left:' + (x - 4) + 'px;top:' + (y - 4) + 'px;width:' + (w + 8) + 'px;height:' + (h + 8) + 'px';
      box.querySelector('b').textContent = label(t);
      box.classList.toggle('flip', y < 120);
      box.hidden = false;
    }
    scr.addEventListener('pointermove', function (e) { var t = e.target.closest(HUD_T); show(t && scr.contains(t) ? t : null); });
    scr.addEventListener('pointerleave', function () { show(null); });
  }

  /* ---------- telex: type a notification in ---------- */
  function telex(stack, state, msg, time) {
    var t = document.createElement('div');
    t.className = 'telex' + (state === 'fault' ? ' telex--fault' : '');
    t.setAttribute('role', 'status');
    t.innerHTML = '<span class="state state--' + state + '">' + state.replace('ok', 'nominal') + '</span><span class="telex-m"></span><span class="telex-t">' + time + '</span>';
    stack.insertBefore(t, stack.firstChild);
    while (stack.children.length > 4) stack.lastChild.remove();
    var m = t.querySelector('.telex-m');
    if (reduce) { m.textContent = msg; return; }
    var i = 0;
    (function type() { m.textContent = msg.slice(0, ++i) + (i < msg.length ? '▮' : ''); if (i < msg.length) setTimeout(type, 14 + Math.random() * 30); })();
  }
  window.shingoTelex = telex;
  window.shingo = { telex: telex, wipe: function (el, fn) { wipe(el, fn); }, scramble: function (el) { scrambleScreen(el); }, reduce: reduce };
  var FEED = [['ok', 'Relay 04 sealed · keys rotated'], ['warn', 'Relay 03 latency 212 ms · rerouting'], ['ok', 'Unit AX-04 firmware 4.2.1 verified'],
              ['fault', 'Relay 07 lost · kill switch engaged'], ['ok', 'Relay 07 restored · 31 ms'], ['busy', 'Syncing ledger · 7 / 10 packets']];
  document.querySelectorAll('[data-telex-feed]').forEach(function (stack) {
    var k = 0, h = 9, mnt = 41;
    function next() { var f = FEED[k++ % FEED.length]; mnt = (mnt + 1 + Math.floor(Math.random() * 3)) % 60; telex(stack, f[0], f[1], '0' + h + ':' + (mnt < 10 ? '0' : '') + mnt); }
    next(); next();
    if (!reduce) setInterval(next, 3200);
  });
  document.querySelectorAll('[data-telex-send]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var stack = document.getElementById(btn.getAttribute('data-telex-send')), f = FEED[Math.floor(Math.random() * FEED.length)], d = new Date();
      telex(stack, f[0], f[1], (d.getHours() < 10 ? '0' : '') + d.getHours() + ':' + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes());
    });
  });
  /* steppers and spec-table selection */
  document.querySelectorAll('.stepper').forEach(function (st) {
    var out = st.querySelector('output'), b = st.querySelectorAll('button'), min = +(st.dataset.min || 0), max = +(st.dataset.max || 99);
    b[0].addEventListener('click', function () { out.value = out.textContent = Math.max(min, +out.textContent - 1); });
    b[1].addEventListener('click', function () { out.value = out.textContent = Math.min(max, +out.textContent + 1); });
  });
  document.querySelectorAll('.stable tbody').forEach(function (tb) {
    tb.addEventListener('click', function (e) { var r = e.target.closest('tr'); if (!r) return; tb.querySelectorAll('tr').forEach(function (x) { x.setAttribute('aria-selected', x === r ? 'true' : 'false'); }); });
  });

  /* ---------- wire up ---------- */
  document.querySelectorAll('.scr, .con, [data-sg-live]').forEach(function (scr) {
    hud(scr);
    scr.querySelectorAll('.tabbar a, .con-rail a').forEach(function (a) {
      a.addEventListener('click', function () {
        if (reduce) { scr.querySelectorAll('.tabbar a, .con-rail a').forEach(function (x) { x.toggleAttribute('aria-current', x === a); }); return; }
        wipe(scr, function () { scr.querySelectorAll('.tabbar a, .con-rail a').forEach(function (x) { x.toggleAttribute('aria-current', x === a); }); scrambleScreen(scr); });
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
    document.querySelectorAll('.scr, .con, [data-sg-live]').forEach(function (s) { io.observe(s); });
  }
})();
