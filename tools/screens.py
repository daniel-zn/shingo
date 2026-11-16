"""Regenerate the 02 · Screens grid inside web/gallery.src.html.

  python3 tools/screens.py && python3 tools/build.py

Utility screens are written against one template (header, hero, cut, slab;
see "screen grammar" in web/shingo.css), so they stay consistent. Poster-tier
screens (A, L, M) are composed by hand below. N (the lock-screen manifesto) is
kept as it is in the source file.
"""
import pathlib, re

SRC = pathlib.Path(__file__).resolve().parent.parent / 'web' / 'gallery.src.html'

SB = '<div class="sb"><span>9:41</span><span class="sb-r"><i class="sig"></i><i class="bat"></i></span></div><i class="island"></i>'


def tabbar(items, active):
    out = []
    for i, (glyph, label) in enumerate(items):
        cur = ' aria-current="page"' if i == active else ''
        out.append(f'<a{cur}><svg><use href="#g-{glyph}"/></svg>{label}</a>')
    return '<nav class="tabbar">' + ''.join(out) + '</nav>'


def header(title, sub, tag=''):
    return f'<header class="u-hd"><h3 class="u-title">{title}</h3><div class="u-sub">{sub}</div>{tag}</header>'


def jp_tag(text):
    return f'<div class="u-tag sg-jp-v">{text}</div>'


def meta_tag(text):
    return f'<div class="u-tag u-meta">{text}</div>'


def utility(body, home='ink', tab=''):
    hb = '<i class="home" style="--hb:var(--ink)"></i>' if home == 'ink' else '<i class="home"></i>'
    return f'<div class="phone"><div class="scr u tex">\n      {SB}\n      {body}\n      {tab}\n      {hb}\n    </div></div>'


def fig(letter, title, caption, phone, tier='utility'):
    return f'''
  <!-- {letter} · {title.lower()} -->
  <figure data-tier="{tier}">
    {phone}
    <figcaption><b>{letter} · {title}</b><span><em class="tier">{tier}</em> {caption}</span></figcaption>
  </figure>
'''


TAB_VPN = [('mark', 'home'), ('bars', 'stats'), ('disc', 'scan'), ('globe', 'servers')]
X = lambda kind, size, color: f'<svg width="{size}" height="{size}" style="color:var({color})"><use href="#g-x-{kind}"/></svg>'
PILL = lambda h, p, cls='pill--bleed-l', style='': (f'<div class="pill {cls}" style="--h:{h}px;{style}"><div class="pill__mid"><div class="pill__core">'
                                                   f'<i class="pill__slot" style="--p:{p}%"></i></div></div></div>')

screens = []

# ---------------------------------------------------------------- T template
screens.append(fig('T', 'Template', 'The shared skeleton every utility screen follows. Swap the contents, keep the zones.', utility(f'''
      <header class="u-hd zone" style="padding-bottom:14px"><h3 class="u-title">Title</h3><div class="u-sub">mono subline · <span class="sg-fr">aparté</span></div><div class="u-tag sg-jp-v">見出</div><span class="zl">header · title 28 · subline · one tag</span></header>
      <div class="u-hero zone" style="height:150px;box-sizing:border-box">{PILL(104, 70, style='width:300px')}<span class="zl">hero · one form</span></div>
      <i class="u-cut"></i>
      <section class="u-slab zone-slab">
        <span class="zl" style="top:30px;bottom:auto">cut · 28 pt rise · 12 pt coral edge</span>
        <div class="u-label"><span>group label</span><span>01</span></div>
        <div class="set"><span class="sg-label">Row label</span><input class="tgl" type="checkbox" id="t-1" checked aria-label="Example"></div>
        <div class="set"><span class="sg-label">Row label</span><span class="sg-mono u-dim">value</span></div>
        <button class="btn btn--block" type="button">One action</button>
        <span class="zl" style="bottom:118px">slab · 24 pt gutter · ink on sage</span>
      </section>''', tab=tabbar(TAB_VPN, 0))))

# ---------------------------------------------------------------- B passcode
keys = ''.join(f'<div class="key"><span class="sg-num">{n}</span><span class="sg-mono">{l or "&nbsp;"}</span></div>' for n, l in
               [(1, ''), (2, 'ABC'), (3, 'DEF'), (4, 'GHI'), (5, 'JKL'), (6, 'MNO'), (7, 'PQRS'), (8, 'TUV'), (9, 'WXYZ')])
keys += ('<div class="key key--flat"><span class="sg-mono">face id</span></div>'
         '<div class="key"><span class="sg-num">0</span><span class="sg-mono">&nbsp;</span></div>'
         '<div class="key key--flat"><svg width="24" height="24"><use href="#g-x-line"/></svg></div>')
dots = ''.join(X('solid', 30, '--ground-hi') for _ in range(2)) + X('solid', 30, '--coral') + ''.join(X('line', 30, '--ground-dim') for _ in range(3))
screens.append(fig('B', 'Passcode', 'Entry indicators are X marks: solid when entered, coral for the latest digit. The seal 認証 (authentication) is the header tag.', utility(f'''
      {header('Enter<br>passcode', 'attempt 1 of 5 · device lock armed', '<div class="u-tag hanko">認証</div>')}
      <div class="u-hero u-hero--pad" style="display:flex;gap:12px">{dots}</div>
      <i class="u-cut"></i>
      <section class="u-slab u-slab--end" style="align-items:center">
        <div class="keypad">{keys}</div>
        <div class="sg-mono" style="align-self:stretch;display:flex;justify-content:space-between;margin-top:auto"><span>cancel</span><span>forgot passcode</span></div>
      </section>''')))

# ---------------------------------------------------------------- C dashboard
screens.append(fig('C', 'Dashboard', 'Status as the title, uptime as the hero pill, then tiles and toggles on the slab. 保護中 means protected.', utility(f'''
      {header('Protected', 'since 08:14 · wireguard · lis-04', jp_tag('保護中'))}
      <div class="u-hero" style="display:flex;align-items:center;justify-content:space-between">{PILL(104, 82, style='width:280px')}<div class="sg-mono t-right" style="padding-right:24px;color:var(--ground-dim)">uptime<br><span class="sg-num" style="font-size:28px;color:var(--ground-hi)">82%</span></div></div>
      <i class="u-cut"></i>
      <section class="u-slab">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="chamfer" style="--fill:var(--sage-hi)"><div class="sg-mono u-dim">threats blocked</div><div class="sg-num" style="font-size:28px;margin:8px 0 14px">1,284</div><div class="barcode--v" style="height:22px"></div></div>
          <div class="chamfer" style="--fill:var(--sage-hi)"><div class="sg-mono u-dim">data routed</div><div class="sg-num" style="font-size:28px;margin:8px 0 22px">4.2<span class="sg-mono"> GB</span></div><div class="slot" style="--p:42%"></div></div>
        </div>
        <div>
          <div class="set"><span class="sg-label">Kill switch</span><input class="tgl" type="checkbox" id="c-ks" checked aria-label="Kill switch"></div>
          <div class="set"><span class="sg-label">Block trackers</span><input class="tgl" type="checkbox" id="c-bt" checked aria-label="Block trackers"></div>
        </div>
        <button class="btn btn--block" type="button">Disconnect</button>
      </section>''', tab=tabbar(TAB_VPN, 0))))

# ---------------------------------------------------------------- D fitness
days = [('solid', '--ground-hi'), ('line', '--ground-dim'), ('solid', '--ground-hi'), ('solid', '--ground-hi'), ('line', '--ground-dim'), ('solid', '--ground-hi'), ('solid', '--coral')]
dayrow = ''.join(f'<span>{X(k, 32, c)}<i class="sg-mono">{d}</i></span>' for (k, c), d in zip(days, 'mtwtfss'))
zones = ''.join(f'<span class="sg-mono">{z}</span><i class="slot" style="--p:{p}%;{"" if z == "z3" else "background:linear-gradient(90deg,var(--ink) var(--p),var(--sage-lo) 0)"}"></i><span class="sg-mono t-right">{t}</span>'
                for z, p, t in [('z1', 18, '0:40'), ('z2', 64, '2:21'), ('z3', 22, '0:31'), ('z4', 6, '0:09')])
screens.append(fig('D', 'Fitness', 'One giant number as the hero, X marks for run and rest days, and slot bars for heart-rate zones. French in the subline.', utility(f'''
      {header('Run log', '<span class="sg-fr">journal de course</span> · week 46', meta_tag('10–16<br>nov'))}
      <div class="u-hero u-hero--pad"><div style="display:flex;align-items:baseline;gap:8px"><span class="sg-num" style="font-size:88px;letter-spacing:-.05em;color:var(--ground-hi)">42.6</span><span class="sg-mono" style="font-size:13px">km</span></div>
        <div class="dayrow">{dayrow}</div></div>
      <i class="u-cut"></i>
      <section class="u-slab">
        <div class="stats3"><div><span class="sg-mono u-dim">avg pace</span><b class="sg-num">5'12"</b></div><div><span class="sg-mono u-dim">moving</span><b class="sg-num">3:41:08</b></div><div><span class="sg-mono u-dim">elevation</span><b class="sg-num">+412 m</b></div></div>
        <div class="u-label"><span>time in zone</span><span>hr</span></div>
        <div class="zones">{zones}</div>
      </section>''', tab=tabbar([('mark', 'today'), ('bars', 'log'), ('globe', 'routes'), ('user', 'me')], 1))))

# ---------------------------------------------------------------- E wallet
screens.append(fig('E', 'Wallet', 'The card is the hero: a nested stadium whose slot is the magnetic stripe. 財布 (wallet) is the header tag.', utility(f'''
      {header('Wallet', 'main account · eur', jp_tag('財布'))}
      <div class="u-hero u-hero--pad"><div class="scard"><div><span class="sg-wordmark" style="font-size:15px">AXIOM</span><span class="sg-mono" style="float:right">debit</span><i></i><span class="sg-mono">•••• 4417 · 09/29</span></div></div></div>
      <i class="u-cut"></i>
      <section class="u-slab">
        <div><div class="sg-mono u-dim">available balance</div><div class="sg-num" style="font-size:40px;margin-top:6px">€8,214.60</div></div>
        <div class="seg"><button type="button">week</button><button type="button" aria-pressed="true">month</button><button type="button">year</button></div>
        <div>
          <div class="row"><svg width="20" height="20" style="color:var(--coral)"><use href="#g-arrow"/></svg><span><span class="sg-label" style="display:block">Night Train Co.</span><span class="sg-mono">travel · 14:02</span></span><span class="sg-num" style="font-size:15px">−€118.00</span></div>
          <div class="row"><svg width="20" height="20" style="transform:rotate(180deg)"><use href="#g-arrow"/></svg><span><span class="sg-label" style="display:block">Salary · Nov</span><span class="sg-mono">income · 09:00</span></span><span class="sg-num" style="font-size:15px">+€3,940.00</span></div>
        </div>
      </section>''', tab=tabbar([('mark', 'wallet'), ('bars', 'spend'), ('arrow', 'send'), ('user', 'me')], 0))))

# ---------------------------------------------------------------- F player
screens.append(fig('F', 'Music player', 'The record is the only hero. The slab carries the title, a slot scrubber and one coral action.', utility(f'''
      {header('Now playing', 'side a · 24-bit / 96 khz', meta_tag('03<br>/ 12'))}
      <div class="u-hero" style="height:300px;box-sizing:content-box;padding-bottom:4px"><div class="vinyl"><svg><use href="#g-disc"/></svg><span></span></div></div>
      <i class="u-cut"></i>
      <section class="u-slab u-slab--end">
        <div><h3 class="sg-wordmark" style="margin:0;font-size:28px">Night transit</h3><div class="sg-mono u-dim" style="margin-top:6px">Low Orbit Choir — Signal Fade</div></div>
        <div><div class="slot" style="--p:38%"></div><div class="sg-mono" style="display:flex;justify-content:space-between;margin-top:8px"><span>1:42</span><span>−2:51</span></div></div>
        <div style="display:flex;justify-content:center;align-items:center;gap:28px">
          <button class="btn btn--sage btn--icon" type="button" aria-label="Previous"><svg style="transform:scaleX(-1)"><use href="#g-skip"/></svg></button>
          <button class="btn btn--coral" type="button" aria-label="Play" style="width:76px;height:76px;padding:0"><svg style="width:28px;height:28px"><use href="#g-play"/></svg></button>
          <button class="btn btn--sage btn--icon" type="button" aria-label="Next"><svg><use href="#g-skip"/></svg></button>
        </div>
      </section>''')))

# ---------------------------------------------------------------- G radar
screens.append(fig('G', 'Radar scan', 'A chamfer frame is the hero scope. Only the device you can act on is coral.', utility(f'''
      {header('Nearby', '<span class="sg-fr">balayage en cours</span> · 6 found', meta_tag('2.4 / 5<br>ghz'))}
      <div class="u-hero u-hero--pad"><div class="chamfer scope" style="--fill:var(--ground);--c:26px">
        <i class="scope-rings"></i><i class="scope-sweep"></i>
        <svg style="left:50%;top:50%;width:18px;height:18px;margin:-9px;color:var(--ground-hi)"><use href="#g-plus"/></svg>
        <svg style="left:64%;top:26%;width:18px;height:18px;color:var(--coral)"><use href="#g-mark"/></svg>
        <svg style="left:30%;top:64%;width:14px;height:14px;color:var(--ground-hi)"><use href="#g-mark"/></svg>
        <svg style="left:68%;top:72%;width:14px;height:14px;color:var(--ground-hi)"><use href="#g-mark"/></svg>
      </div></div>
      <i class="u-cut"></i>
      <section class="u-slab">
        <div>
          <div class="row"><svg width="20" height="20" style="color:var(--coral)"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">AX-04 router</span><span class="sg-mono">ax:04:e1:9c · 2 m</span></span><i class="barcode--v" style="width:30px;height:16px"></i></div>
          <div class="row"><svg width="20" height="20"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">TV room</span><span class="sg-mono">5c:11:a0:3f · 6 m</span></span><i class="barcode--v" style="width:20px;height:16px"></i></div>
          <div class="row"><svg width="20" height="20"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">Unknown device</span><span class="sg-mono">f2:88:07:d4 · 11 m</span></span><i class="barcode--v" style="width:10px;height:16px"></i></div>
        </div>
      </section>''', tab=tabbar(TAB_VPN, 2))))

# ---------------------------------------------------------------- H inbox
rows = [('LS', 'Lena Sato', 'route map for friday is attached', '09:12', True, ''), ('OP', 'Ops desk', 'key rotation complete · 3 devices', '08:40', True, ''),
        ('RK', 'Rui Kemp', 'ok — see you at the north gate', 'mon', False, ''), ('09', 'Unit 09', 'weekly report · 14 pages', 'sun', False, ' av--ink'),
        ('AM', 'Ada Mensah', 'photos from the field trip', 'sat', False, '')]
rowhtml = ''.join(f'<div class="row"><span class="av{c}">{i}</span><span><span class="sg-label" style="display:block">{n}</span><span class="sg-mono">{m}</span></span>'
                  f'<span style="display:grid;justify-items:end;gap:6px"><span class="sg-mono">{t}</span>{"<i class=unread></i>" if u else ""}</span></div>' for i, n, m, t, u, c in rows)
screens.append(fig('H', 'Inbox', 'No hero, so the header tag is the compose action and the filter sits on the ground. Coral only marks unread.', utility(f'''
      {header('Inbox', '12 unread · end-to-end', '<button class="u-tag-btn btn btn--sage btn--icon" type="button" aria-label="New message"><svg><use href="#g-plus"/></svg></button>')}
      <div class="u-hero u-hero--pad"><div class="seg seg--ink"><button type="button" aria-pressed="true">all</button><button type="button">flagged</button><button type="button">sealed</button></div></div>
      <i class="u-cut"></i>
      <section class="u-slab"><div>{rowhtml}</div></section>''', tab=tabbar([('mark', 'inbox'), ('x-line', 'spam'), ('globe', 'contacts'), ('user', 'me')], 0))))

# ---------------------------------------------------------------- I settings
def group(label, n, rows_):
    return f'<div><div class="u-label"><span>{label}</span><span>{n}</span></div>{rows_}</div>'
tg = lambda id_, label, small, on: f'<div class="set"><span><span class="sg-label">{label}</span>{f"<small>{small}</small>" if small else ""}</span><input class="tgl" type="checkbox" id="{id_}"{" checked" if on else ""} aria-label="{label}"></div>'
nav = lambda label, val: f'<div class="set"><span class="sg-label">{label}</span><span class="sg-mono u-dim" style="display:flex;gap:6px;align-items:center">{val} <svg width="11" height="11"><use href="#g-chev"/></svg></span></div>'
screens.append(fig('I', 'Settings', 'No hero, so the slab starts right under the header. Plain grouped rows with numbered labels. 設定 means settings.', utility(f'''
      {header('Settings', 'v 4.2 · build 2611', jp_tag('設定'))}
      <i class="u-cut" style="margin-top:20px"></i>
      <section class="u-slab u-slab--end" style="gap:20px">
        {group('privacy', '01', tg('s-ks', 'Kill switch', 'pause traffic if the tunnel drops', True) + tg('s-bt', 'Block trackers', '1,284 blocked this week', True) + tg('s-ln', 'Allow local network', 'printers, casting, smart home', False))}
        {group('network', '02', nav('Protocol', 'wireguard') + nav('Server', 'lisbon-04'))}
        {group('display', '03', tg('s-st', 'Stripe texture', '', True) + tg('s-rm', 'Reduce motion', '', False))}
      </section>''')))

# ---------------------------------------------------------------- J credential
screens.append(fig('J', 'ID credential', 'The badge is the hero: topo avatar, name, fields and barcode. 身分証明書 (ID certificate) runs down its edge.', utility(f'''
      {header('Credential', '<span class="sg-fr">carte de membre</span> · axiom', meta_tag('valid<br>2028'))}
      <div class="u-hero u-hero--pad"><div class="chamfer badge" style="--fill:var(--sage-hi);--c:30px">
        <span class="badge-av"><svg><use href="#g-topo"/></svg></span>
        <div class="badge-num"><span class="sg-num">09</span><span class="sg-mono">clearance</span></div>
        <h3 class="sg-wordmark">Mira<br>Okafor</h3>
        <div class="sg-mono badge-f">unit&nbsp;&nbsp;&nbsp; field ops<br>id&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; AX-0917-c53<br>issued&nbsp; 2026-03-02</div>
        <span class="sg-jp-v badge-jp">身分証明書</span>
        <i class="barcode--v badge-bc"></i>
      </div></div>
      <i class="u-cut"></i>
      <section class="u-slab u-slab--end"><div style="display:grid;grid-template-columns:1fr auto;gap:12px"><button class="btn" type="button">Add to wallet</button><button class="btn btn--ghost" type="button">Show QR</button></div></section>''')))

# ---------------------------------------------------------------- K alert
screens.append(fig('K', 'Alert sheet', 'Interruptions get the coral surface, with the same 28 pt cut as its top edge. Nothing else on the sheet competes.', f'''<div class="phone"><div class="scr u tex">
      {SB}
      {header('Protected', 'since 08:14 · wireguard · lis-04', jp_tag('保護中'))}
      <div class="u-hero">{PILL(104, 30, style='width:280px')}</div>
      <i class="u-cut"></i>
      <section class="u-slab"></section>
      <i class="dim" style="position:absolute;inset:0;z-index:5"></i>
      <div class="u-sheet" style="z-index:10">
        <div style="display:flex;justify-content:space-between;align-items:center"><svg width="48" height="48"><use href="#g-x-solid"/></svg><span class="sg-mono t-right">err 0x09<br>14:22:07</span></div>
        <h3 class="sg-wordmark" style="margin:0;font-size:28px">Connection<br>dropped</h3>
        <p class="sg-mono" style="margin:0;font-size:12px;line-height:1.5">Lisbon-04 stopped responding. The kill switch has paused all traffic until you reconnect or pick another server.</p>
        <button class="btn btn--block" type="button" style="background:#0c0c0a;color:#c3c6bd">Reconnect</button>
        <button class="btn btn--ghost btn--block" type="button" style="color:#0c0c0a">Choose another server</button>
      </div>
      <i class="home" style="--hb:#0c0c0a;z-index:40"></i>
    </div></div>'''))

# ---------------------------------------------------------------- O editorial
screens.append(fig('O', 'Long read', 'The headline is the hero, set at display size. A French pull quote is the one ornament in the body.', utility(f'''
      {header('Field notes', 'nº 09 · Lena Sato · 6 min read', jp_tag('第九号'))}
      <div class="u-hero u-hero--pad"><h3 class="sg-wordmark" style="margin:0;font-size:44px;color:var(--ground-hi)">The quiet<br>network</h3></div>
      <i class="u-cut"></i>
      <section class="u-slab u-slab--end" style="gap:18px">
        <p class="sg-label" style="margin:0;font-size:15px;line-height:1.55;letter-spacing:-.01em">Most of what keeps you safe online is invisible. Packets leave your phone, cross three relays and arrive without anyone reading them.</p>
        <blockquote style="margin:0;padding-left:16px;border-left:3px solid var(--coral)"><div class="sg-fr" style="font-size:20px;line-height:1.2">« Le réseau le plus sûr est celui qu'on n'entend pas. »</div><div class="sg-mono u-dim" style="margin-top:8px">the safest network is the one you can't hear</div></blockquote>
        <p class="sg-label" style="margin:0;font-size:15px;line-height:1.55;letter-spacing:-.01em">That is the brief for AXIOM 4.2: fewer alerts, faster tunnels, and a kill switch you never think about.</p>
        <div style="margin-top:auto"><div class="slot" style="--p:38%"></div><div class="sg-mono u-dim" style="display:flex;justify-content:space-between;margin-top:8px"><span>read 38%</span><span>02 / 05</span></div></div>
      </section>''')))

# ---------------------------------------------------------------- P paywall
screens.append(fig('P', 'Paywall', 'The chevron print is the hero. Plans, benefits and one coral action sit on the slab, with French fine print.', utility(f'''
      {header('Axiom pro', 'every relay · every device', '<div class="u-tag hanko">認定</div>')}
      <div class="u-hero u-hero--pad" style="display:flex;justify-content:flex-end"><svg viewBox="0 0 300 230" style="width:250px;height:auto;color:var(--ground-hi)"><use href="#g-chevrons"/></svg></div>
      <i class="u-cut"></i>
      <section class="u-slab u-slab--end">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="chamfer" style="--fill:var(--sage)"><div class="sg-mono u-dim">monthly</div><div class="sg-num" style="font-size:28px;margin-top:8px">€4.99</div><div class="sg-mono u-dim" style="margin-top:4px">per month</div></div>
          <div class="chamfer" style="--fill:var(--sage-hi);--line:var(--ink)"><div class="sg-mono u-dim">yearly · save 35%</div><div class="sg-num" style="font-size:28px;margin-top:8px">€39.00</div><div class="sg-mono u-dim" style="margin-top:4px">€3.25 / month</div></div>
        </div>
        <div class="sg-mono" style="display:grid;gap:6px"><span>10 devices · 60 relay cities · priority tunnels</span></div>
        <button class="btn btn--coral btn--block" type="button">Start 7-day free trial</button>
        <div class="sg-fr u-dim" style="text-align:center;font-size:11.5px">Résiliable à tout moment · paiement via l'App Store</div>
      </section>''')))

# ---------------------------------------------------------------- poster tier
POSTER = {}
POSTER['A'] = fig('A', 'Launch', 'The full poster homage: stacked pills, the 45° coral band and the wordmark at display size. The pill slot is the boot progress.', f'''<div class="phone"><div class="scr tex" style="--a:-38deg">
      <i class="facet" style="--a:-18deg;clip-path:polygon(0 0,100% 0,100% 3%,0 28%)"></i>
      {SB}
      <div style="top:68px;left:24px;display:flex;gap:9px;align-items:center"><svg width="18" height="18" style="color:var(--coral)"><use href="#g-mark"/></svg><span class="sg-wordmark" style="font-size:15px;color:var(--ground-hi)">AXIOM</span></div>
      <i class="band" style="top:60px;right:0;width:150px;height:150px;clip-path:polygon(100% 0,100% 100%,0 100%)"></i>
      <svg style="top:52px;right:14px;width:104px;height:104px;color:var(--ground-hi)"><use href="#g-x-line"/></svg>
      {PILL(118, 100, style='top:118px;left:0;width:252px')}
      <div class="sg-jp-v" style="top:262px;left:30px;color:var(--ground-dim)">安全な作業空間</div>
      {PILL(118, 58, cls='pill--bleed-r', style='top:262px;left:84px;right:0')}
      <i class="band" style="top:360px;left:0;width:240px;height:240px;clip-path:polygon(150px 0,240px 0,0 240px,0 150px)"></i>
      <i class="slab" style="top:374px;left:0;right:0;bottom:0;clip-path:polygon(226px 0,100% 0,100% 100%,0 100%,0 226px)"></i>
      <div class="t-right" style="top:430px;right:24px;color:var(--ink)"><div class="sg-wordmark" style="font-size:44px">AXIOM</div><div class="sg-mono" style="margin-top:10px">secure workspace</div></div>
      <div style="top:680px;left:150px;right:24px;color:var(--ink)"><div class="sg-mono t-right" style="margin-bottom:10px">sealing tunnel · 64%</div><div class="slot" style="--p:64%"></div></div>
      <i class="home" style="--hb:var(--ink)"></i>
    </div></div>''', tier='poster')

POSTER['L'] = fig('L', 'Empty state', 'Two X outlines make the illustration, and 圏外 (out of range) is what Japanese phones show. The coral wedge is the 45° motif.', '''<div class="phone"><div class="scr" style="background:var(--sage);--sb:var(--ink)">
      <div class="sb"><span>9:41</span><span class="sb-r"><i class="sig" style="opacity:.3"></i><i class="bat"></i></span></div><i class="island"></i>
      <svg style="top:110px;left:-30px;width:300px;height:300px;color:var(--sage-hi)"><use href="#g-x-line"/></svg>
      <svg style="top:250px;left:190px;width:150px;height:150px;color:var(--ink)"><use href="#g-x-line"/></svg>
      <h3 class="sg-wordmark" style="margin:0;top:446px;left:24px;font-size:44px;color:var(--ink)">No<br>signal</h3>
      <div class="sg-jp" style="top:444px;right:24px;font-size:40px;line-height:1.05;writing-mode:vertical-rl;color:var(--ink)">圏外</div>
      <p class="sg-mono" style="margin:0;top:548px;left:24px;right:70px;font-size:12px;line-height:1.5;color:var(--ink)">We couldn't reach the network. Check Wi-Fi or mobile data, then try again.</p>
      <div style="top:630px;left:24px;right:24px;display:grid;gap:10px"><button class="btn btn--block" type="button">Try again</button><button class="btn btn--ghost btn--block" type="button" style="color:var(--ink)">Open offline files</button></div>
      <i class="band" style="right:0;bottom:0;width:120px;height:120px;clip-path:polygon(100% 0,100% 100%,0 100%)"></i>
      <i class="home" style="--hb:var(--ink)"></i>
    </div></div>''', tier='poster')

POSTER['M'] = fig('M', 'Onboarding', 'Stacked pills on the ground, then the standard cut. The headline is set at display size, with French above it.', f'''<div class="phone"><div class="scr tex" style="--a:-38deg">
      {SB}
      <div class="sg-mono" style="top:70px;left:24px;color:var(--ground-dim)">step 2 of 3</div>
      <div class="sg-mono t-right" style="top:70px;right:24px;color:var(--on-ground)">skip</div>
      {PILL(96, 100, style='top:112px;left:0;width:300px')}
      {PILL(96, 66, cls='pill--bleed-r', style='top:222px;left:40px;right:0')}
      {PILL(96, 20, style='top:332px;left:0;width:240px')}
      <i class="u-cut" style="position:absolute;top:452px;left:0;right:0;margin:0"></i>
      <i class="slab" style="top:464px;left:0;right:0;bottom:0;clip-path:polygon(0 28px,100% 0,100% 100%,0 100%)"></i>
      <div class="t-right" style="top:516px;right:24px;left:24px;color:var(--ink)"><div class="sg-fr" style="font-size:13px">acheminer chaque paquet</div><h3 class="sg-wordmark" style="margin:10px 0 0;font-size:44px">Route<br>every packet</h3><p class="sg-mono" style="margin:14px 0 0;font-size:12px">Three relays, two keys, zero logs.</p></div>
      <div style="top:762px;left:24px;display:flex;gap:6px;align-items:center"><i class="slot" style="width:14px;background:var(--sage-lo)"></i><i class="slot" style="width:44px;--p:100%"></i><i class="slot" style="width:14px;background:var(--sage-lo)"></i></div>
      <button class="btn" type="button" style="top:744px;right:24px">Next<svg><use href="#g-arrow"/></svg></button>
      <i class="home" style="--hb:var(--ink)"></i>
    </div></div>''', tier='poster')

src = SRC.read_text()
# keep N (manifesto) as is, but at the display size
n_start = src.index('  <!-- N · lock screen manifesto -->'); n_end = src.index('  <!-- O · ', n_start)
N = src[n_start:n_end].replace('<span class="sg-wordmark wear" style="font-size:54px">AXIOM</span>', '<span class="sg-wordmark wear" style="font-size:44px">AXIOM</span>')
N = N.replace('<figure>', '<figure data-tier="poster">', 1).replace('<figcaption><b>N · Lock screen / manifesto</b><span>', '<figcaption><b>N · Lock screen</b><span><em class="tier">poster</em> ')
N = N.replace('The one place all three languages stack, like the shirt. The print gets a worn screen-print filter, and the date is in French.',
              'The manifesto: the only place all three languages stack, with the chevron print, hazard bar and worn screen-print filter.')

order = [screens[0]]                       # T
order += [POSTER['A']] + screens[1:2]      # A, B
order += screens[2:9]                      # C D E F G H I
order += screens[9:11]                     # J K
order += [POSTER['L'], POSTER['M'], N]     # L M N
order += screens[11:13]                    # O P
grid = '\n'.join(order)

a = src.index('<div class="screens">') + len('<div class="screens">')
b = src.index('  </div>\n</section>', a)
src = src[:a] + '\n' + grid + '\n' + src[b:]
SRC.write_text(src)
print('screens:', grid.count('<figure'))
