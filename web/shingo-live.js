/* Shingō live layer: machine behaviour for the print system.
   - Decode: text resolves from glyph noise when it arrives, changes or is touched;
     titles slowest, then labels, then data, staggered down the screen.
   - Live readouts: seven-segment counters and countdowns re-render in place.
   - Coordinates: the last digits of live coordinates drift.
   - Transitions: a hazard band wipes along the one diagonal between views.
   - HUD: a bracket reticle snaps to data under the pointer with a callout.
   Nothing eases: slides (wipe) are linear, state changes are stepped; all off under reduced motion.
   Content is complete at rest: nothing is hidden waiting for script.
   Scope: .scr (phone screen), .con (console) or any element with data-sg-live.
   Decode: regions decode on arrival (.scr, .con, [data-sg-live], [data-decode-view]); controls on hover;
   values on change ([data-decode-change]); opt a node out with [data-no-decode].
   API: window.shingo.{telex(stack, state, msg, time), wipe(el, fn), scramble(region), decode(el, weight), decodeOnChange(el)}. */
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

  /* ---------- decode ----------
     Information decodes when it ARRIVES (reveal), CHANGES (new value) or is TOUCHED (hover, select).
     Three weights, so the screen reads in order: titles slowest, then labels, then data.
     Noise keeps each character's class (digits flicker through digits, letters through hard
     capitals, kanji through kanji) so widths and structure hold; punctuation never scrambles.
     Each character locks at its own random moment; frames land unevenly (28–80 ms). */
  var NZ = { d: '0123456789', a: 'XKZNRVHEW#/', l: 'xkznrvhew#/', j: '信号経路保護暗中封鎖', o: '' };
  function cls(c) {
    if (c >= '0' && c <= '9') return 'd';
    if (/[A-ZÀ-Þ]/.test(c)) return 'a';
    if (/[a-zß-ÿ]/.test(c)) return 'l';
    if (/[぀-ヿ一-鿿]/.test(c)) return 'j';
    return 'o';
  }
  function noise(c) { var s = NZ[cls(c)]; return s ? s[Math.floor(Math.random() * s.length)] : c; }
  var SKIP = 'svg, input, textarea, select, option, script, style, .ticker, .telex-m, .live-coord, [data-no-decode]';
  // weight → total duration range (ms)
  var WEIGHT = { title: [320, 720], label: [160, 380], data: [200, 520], touch: [120, 260] };
  function scramble(el, weight, delay) {
    if (reduce) return;
    var w = WEIGHT[weight || 'title'], nodes = [], tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) {
      var n = tw.currentNode;
      if (n.__sc || !n.nodeValue.trim() || (n.parentElement && n.parentElement.closest(SKIP))) continue;
      n.__sc = 1; nodes.push({ n: n, src: n.nodeValue });
    }
    if (!nodes.length) return;
    var total = w[0] + Math.random() * (w[1] - w[0]);
    nodes.forEach(function (o) {
      o.lock = Array.prototype.map.call(o.src, function () { return total * (.15 + .85 * Math.pow(Math.random(), .8)); });
      o.cur = Array.prototype.map.call(o.src, noise);
    });
    var t0;
    function frame() {
      var t = performance.now() - t0, done = true;
      nodes.forEach(function (o) {
        var s = '';
        for (var k = 0; k < o.src.length; k++) {
          var c = o.src[k];
          if (t >= o.lock[k] || cls(c) === 'o') { s += c; continue; }
          done = false;
          if (Math.random() < .45) o.cur[k] = noise(c);   // irregular flicker
          s += o.cur[k];
        }
        o.n.nodeValue = s;
      });
      if (done) { nodes.forEach(function (o) { o.n.nodeValue = o.src; o.n.__sc = 0; }); return; }
      setTimeout(frame, 28 + Math.random() * 52);
    }
    // hold the noise during the stagger delay, so nothing shows clear text and then breaks up
    nodes.forEach(function (o) { o.n.nodeValue = o.cur.join(''); });
    setTimeout(function () { t0 = performance.now(); frame(); }, delay || 0);
  }
  var DECODE = [
    ['title', '.u-title, .sg-display, .sec-h h2'],
    ['label', '.u-label > span, .nframe > b, .smx b, .u-code, .stable th, .u-foot b, .tabbar a, .con-rail a span, .inst h3 > span:first-child, .alpha-h .sg-cap, .sec-h .sg-num, .optrow, .btn, .keycap > span, [data-decode="label"]'],
    ['data', '.sec-h > .sg-mono, .alpha-h > .sg-mono, .inst h3 > span:last-child, .u-span > span, .u-meta, .spec > span, .stable td.n, .stable td b, .stable td .sg-mono, .smx span, .u-foot span, .state, .nframe .sg-num, [data-decode="data"]']
  ];
  // decode everything in a region on arrival, top to bottom, staggered by weight then document order
  function scrambleScreen(scr) {
    var i = 0;
    DECODE.forEach(function (d, wi) {
      scr.querySelectorAll(d[1]).forEach(function (el) {
        scramble(el, d[0], Math.min(wi * 90 + i++ * 18, 700));
      });
    });
  }
  // values that change decode their new state
  // (the decoder's own writes land on locked nodes, so they never retrigger it)
  function decodeOnChange(el, weight) {
    if (reduce || !('MutationObserver' in window)) return;
    new MutationObserver(function () { scramble(el, weight || 'touch'); }).observe(el, { childList: true, characterData: true, subtree: true });
  }

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
      box.querySelector('b').textContent = label(t); scramble(box.querySelector('b'), 'touch');
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
    scramble(t.querySelector('.state'), 'touch');
    (function type() { m.textContent = msg.slice(0, ++i) + (i < msg.length ? '▮' : ''); if (i < msg.length) setTimeout(type, 14 + Math.random() * 30); else scramble(t.querySelector('.telex-t'), 'data'); })();
  }
  window.shingoTelex = telex;
  window.shingo = { telex: telex, wipe: function (el, fn) { wipe(el, fn); }, scramble: function (el) { scrambleScreen(el); },
    decode: function (el, weight) { scramble(el, weight); }, decodeOnChange: decodeOnChange, reduce: reduce };
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
    var v = +out.textContent;   // the true value; the text may be mid-decode
    function set(n) { v = n; out.textContent = n; scramble(out, 'touch'); }
    b[0].addEventListener('click', function () { set(Math.max(min, v - 1)); });
    b[1].addEventListener('click', function () { set(Math.min(max, v + 1)); });
  });
  document.querySelectorAll('.stable tbody').forEach(function (tb) {
    tb.addEventListener('click', function (e) { var r = e.target.closest('tr'); if (!r) return; if (r.getAttribute('aria-selected') === 'true') return; tb.querySelectorAll('tr').forEach(function (x) { x.setAttribute('aria-selected', x === r ? 'true' : 'false'); }); scramble(r, 'touch'); });
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
  /* touch: controls re-decode their label under a fine pointer; values marked data-decode-change decode when they change */
  if (window.matchMedia && window.matchMedia('(hover: hover)').matches) {
    document.addEventListener('pointerover', function (e) {
      var el = e.target.closest && e.target.closest('.btn, .keycap, .tabbar a, .con-rail a, .chip, .seg button');
      if (el && !(e.relatedTarget && el.contains(e.relatedTarget))) scramble(el, 'touch');
    });
  }
  document.querySelectorAll('[data-decode-change]').forEach(function (el) { decodeOnChange(el, el.getAttribute('data-decode-change') || 'touch'); });
  document.querySelectorAll('.mo-wipe').forEach(function (box) {
    var views = box.querySelectorAll('.mo-view'), i = 0;
    if (reduce) return;
    setInterval(function () { wipe(box, function () { views[i].hidden = true; i = (i + 1) % views.length; views[i].hidden = false; scrambleScreen(box); }); }, 2600);
  });
  if (reduce) return;
  liveReadouts();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { scrambleScreen(e.target); io.unobserve(e.target); } }); }, { threshold: .5 });
    document.querySelectorAll('.scr, .con, [data-sg-live], [data-decode-view]').forEach(function (s) { io.observe(s); });
  }
})();
