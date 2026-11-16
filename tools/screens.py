"""Regenerate the 02 · Screens grid inside web/gallery.src.html.

  python3 tools/screens.py && python3 tools/build.py

Utility screens follow one grammar (see "screen grammar" in web/shingo.css):
masthead (code + title + one tag + span rule) -> one hero -> hazard bar -> body.
Poster-tier screens (A, L, M, N) are composed by hand below.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build import seg7  # noqa: E402

SRC = pathlib.Path(__file__).resolve().parent.parent / 'web' / 'gallery.src.html'

SB = '<div class="sb"><span>9:41</span><span class="sb-r"><i class="sig"></i><i class="bat"></i></span></div><i class="island"></i>'
DIV = '<div class="u-div hazard"></div>'


def cells(n, on, hot=-1, tall=False):
    return f'<div class="cells{" cells--tall" if tall else ""}">' + ''.join(
        f'<i class="{"hot" if i == hot else ("on" if i < on else "")}"></i>' for i in range(n)) + '</div>'


TICKER = ('<div class="ticker"><span>' + ' ◆ LIS-04 · 23 MS · <b>AES-256</b> · 1,284 BLOCKED · UPTIME 82% · RELAY 3/3 · ' * 2 + '</span></div>')


def tabbar(items, active):
    out = []
    for i, (glyph, label) in enumerate(items):
        cur = ' aria-current="page"' if i == active else ''
        out.append(f'<a{cur}><svg><use href="#g-{glyph}"/></svg>{label}</a>')
    return '<nav class="tabbar chamfer">' + ''.join(out) + '</nav>'


def mast(title, left, right, tag='', code='AX·09', extra=''):
    return (f'<header class="u-hd"{extra}><span class="u-code">{code}</span><h3 class="u-title">{title}</h3>{tag}'
            f'<div class="u-span"><span>{left}</span><i></i><span>{right}</span></div></header>')


jp = lambda t: f'<div class="u-tag sg-jp-v">{t}</div>'
meta = lambda t: f'<div class="u-tag u-meta">{t}</div>'
seal = lambda t: f'<div class="u-tag hanko">{t}</div>'
X = lambda kind, size, color: f'<svg width="{size}" height="{size}" style="color:var({color})"><use href="#g-x-{kind}"/></svg>'


def BAR(h, p, cls='', style=''):
    return (f'<div class="bar {cls}" style="--h:{h}px;{style}"><div class="bar__mid"><div class="bar__core">'
            f'<i class="bar__slot" style="--p:{p}%"></i></div></div></div>')


def utility(body, tab=''):
    return f'<div class="phone"><div class="scr u tex">\n      {SB}\n      {body}\n      {tab}\n      <i class="home"></i>\n    </div></div>'


def fig(letter, title, caption, phone, tier='utility'):
    return f'''
  <!-- {letter} · {title.lower()} -->
  <figure data-tier="{tier}">
    {phone}
    <figcaption><b>{letter} · {title}</b><span><em class="tier">{tier}</em> {caption}</span></figcaption>
  </figure>
'''


TAB_VPN = [('mark', 'home'), ('signal', 'stats'), ('reticle', 'scan'), ('grid', 'servers')]
S = {}

# ---------------------------------------------------------------- T template
S['T'] = fig('T', 'Template', 'The grammar every utility screen follows: masthead, one hero, hazard bar, body. Swap the contents, keep the zones.', utility(f'''
      {mast('Title', 'value · <span class="sg-fr">aparté</span>', 'value', jp('見出'), extra=' class="u-hd zone" style="padding-bottom:12px"').replace('class="u-hd"', '')}
      <div class="u-hero u-hero--pad zone" style="height:140px;box-sizing:border-box">{BAR(96, 70, style='margin-left:-24px;width:300px')}<span class="zl">hero · one form</span></div>
      <div class="u-div hazard"></div>
      <section class="u-body zone">
        <div class="u-label"><span>Group label</span><span>01</span></div>
        <div class="set"><span class="sg-label">Row label</span><input class="tgl" type="checkbox" id="t-1" checked aria-label="Example"></div>
        <div class="set"><span class="sg-label">Row label</span><span class="sg-mono u-dim">VALUE</span></div>
        <button class="btn btn--block" type="button">One action</button>
        <span class="zl" style="bottom:112px">body · 24 pt gutter · print on ground</span>
      </section>''', tab=tabbar(TAB_VPN, 0)))

# ---------------------------------------------------------------- B passcode
keys = ''.join(f'<div class="key"><span class="sg-num">{n}</span><span class="sg-mono">{l or "&nbsp;"}</span></div>' for n, l in
               [(1, ''), (2, 'ABC'), (3, 'DEF'), (4, 'GHI'), (5, 'JKL'), (6, 'MNO'), (7, 'PQRS'), (8, 'TUV'), (9, 'WXYZ')])
keys += ('<div class="key key--flat"><svg width="26" height="26"><use href="#g-reticle"/></svg><span class="sg-mono">FACE ID</span></div>'
         '<div class="key"><span class="sg-num">0</span><span class="sg-mono">&nbsp;</span></div>'
         '<div class="key key--flat"><svg width="22" height="22"><use href="#g-x-line"/></svg><span class="sg-mono">DEL</span></div>')
dots = ''.join(X('solid', 28, '--ground-hi') for _ in range(2)) + X('solid', 28, '--coral') + ''.join(X('line', 28, '--ground-dim') for _ in range(3))
S['B'] = fig('B', 'Passcode', 'Entry indicators are hard X marks, with coral for the latest digit. Keys are cut plates. The seal 認証 means authentication.', utility(f'''
      {mast('Enter<br>passcode', 'attempt 1', '5 max', seal('認証'))}
      <div class="u-hero u-hero--pad" style="display:flex;gap:14px">{dots}</div>
      {DIV}
      <section class="u-body u-body--end">
        <div class="keypad">{keys}</div>
        <div class="sg-mono u-dim" style="display:flex;justify-content:space-between;margin-top:auto"><span>CANCEL</span><span>FORGOT PASSCODE</span></div>
      </section>'''))

# ---------------------------------------------------------------- C dashboard
S['C'] = fig('C', 'Dashboard', 'Status as the title and uptime as the hero bar. The body prints frames, toggles and one action. 保護中 means protected.', utility(f'''
      {mast('Protected', 'since 08:14', 'lis-04', jp('保護中'))}
      <div class="u-hero" style="display:flex;align-items:center;justify-content:space-between">{BAR(100, 82, style='width:270px')}<div class="t-right" style="padding-right:24px"><div class="sg-cap" style="font-size:11px;color:var(--ground-dim)">Uptime</div><div class="sg-num" style="font-size:28px;color:var(--ground-hi);margin-top:4px">82%</div></div></div>
      {DIV}
      <section class="u-body">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="chamfer"><div class="sg-cap" style="font-size:11px;color:var(--ground-dim)">Threats blocked</div><div style="margin:10px 0 2px">{seg7("1284", 30)}</div></div>
          <div class="chamfer"><div class="sg-cap" style="font-size:11px;color:var(--ground-dim)">Data routed</div><div class="sg-num" style="font-size:24px;margin:8px 0 12px;color:var(--ground-hi)">4.2<span class="sg-mono"> / 10 GB</span></div>{cells(10, 4)}</div>
        </div>
        <div>
          <div class="set"><span class="sg-label">Kill switch</span><input class="tgl" type="checkbox" id="c-ks" checked aria-label="Kill switch"></div>
          <div class="set"><span class="sg-label">Block trackers</span><input class="tgl" type="checkbox" id="c-bt" checked aria-label="Block trackers"></div>
        </div>
        <button class="btn btn--block" type="button">Disconnect<svg><use href="#g-x-solid"/></svg></button>
        {TICKER}
      </section>''', tab=tabbar(TAB_VPN, 0)))

# ---------------------------------------------------------------- D fitness
days = [('solid', '--ground-hi'), ('line', '--ground-dim'), ('solid', '--ground-hi'), ('solid', '--ground-hi'), ('line', '--ground-dim'), ('solid', '--ground-hi'), ('solid', '--coral')]
dayrow = ''.join(f'<span>{X(k, 30, c)}<i>{d}</i></span>' for (k, c), d in zip(days, 'mtwtfss'))
zones = ''.join(f'<span class="sg-mono">{z.upper()}</span>{cells(12, n, hot=(n - 1 if z == "z3" else -1))}<span class="sg-mono t-right">{t}</span>'
                for z, n, t in [('z1', 2, '0:40'), ('z2', 8, '2:21'), ('z3', 3, '0:31'), ('z4', 1, '0:09')])
S['D'] = fig('D', 'Fitness', 'One giant number as the hero and hard X marks for run and rest days. Zones print as bars. French sits in the span rule.', utility(f'''
      {mast('Run log', '<span class="sg-fr">journal de course</span>', 'W46', meta('10–16<br>NOV'))}
      <div class="u-hero u-hero--pad"><div style="display:flex;align-items:flex-end;gap:10px">{seg7("42.6", 76)}<span class="sg-cap" style="font-size:14px;padding-bottom:2px">km</span></div>
        <div class="dayrow">{dayrow}</div></div>
      {DIV}
      <section class="u-body">
        <div class="stats3"><div><span class="sg-cap" style="font-size:10px;color:var(--ground-dim)">Avg pace</span><b class="sg-num">5'12"</b></div><div><span class="sg-cap" style="font-size:10px;color:var(--ground-dim)">Moving</span><b class="sg-num">3:41:08</b></div><div><span class="sg-cap" style="font-size:10px;color:var(--ground-dim)">Elevation</span><b class="sg-num">+412</b></div></div>
        <div class="u-label"><span>Time in zone</span><span>HR</span></div>
        <div class="zones">{zones}</div>
      </section>''', tab=tabbar([('mark', 'today'), ('signal', 'log'), ('grid', 'routes'), ('head', 'me')], 1)))

# ---------------------------------------------------------------- E wallet
S['E'] = fig('E', 'Wallet', 'The card is the one plate on the screen: a cut slab with a contact pad and a coral strip. 財布 means wallet.', utility(f'''
      {mast('Wallet', 'main', 'eur', jp('財布'))}
      <div class="u-hero u-hero--pad"><div class="pcard plate cut" style="--c:24px">
        <div class="pcard-top"><span class="sg-wordmark" style="font-size:15px">AXIOM</span><span class="sg-mono">DEBIT · 09</span></div>
        <i class="pcard-pad"></i>
        <div><div class="slab-cut" style="height:8px;margin-bottom:12px"></div><div class="pcard-foot"><span class="sg-mono" style="font-size:12px">•••• 4417</span><span class="sg-mono">EXP 09/29</span></div></div>
      </div></div>
      {DIV}
      <section class="u-body">
        <div><div class="sg-cap" style="font-size:11px;color:var(--ground-dim)">Available balance</div><div class="sg-num" style="font-size:40px;margin-top:6px;color:var(--ground-hi)">€8,214.60</div></div>
        <div class="itabs"><button type="button">Week</button><button type="button" aria-pressed="true">Month</button><button type="button">Year</button></div>
        <div>
          <div class="row"><svg width="18" height="18" style="color:var(--coral)"><use href="#g-arrow"/></svg><span><span class="sg-label" style="display:block">Night Train Co.</span><span class="sg-mono">TRAVEL · 14:02</span></span><span class="sg-num" style="font-size:15px;color:var(--ground-hi)">−€118.00</span></div>
          <div class="row"><svg width="18" height="18" style="transform:rotate(180deg);color:var(--ground-hi)"><use href="#g-arrow"/></svg><span><span class="sg-label" style="display:block">Salary · Nov</span><span class="sg-mono">INCOME · 09:00</span></span><span class="sg-num" style="font-size:15px;color:var(--ground-hi)">+€3,940.00</span></div>
        </div>
      </section>''', tab=tabbar([('mark', 'wallet'), ('signal', 'spend'), ('arrow', 'send'), ('head', 'me')], 0)))

# ---------------------------------------------------------------- F player
S['F'] = fig('F', 'Music player', 'A printed spectrum in a cut frame is the hero, with a coral playhead. The coral action is play.', utility(f'''
      {mast('Now playing', 'side a', '24-bit · 96 khz', meta('03<br>/ 12'))}
      <div class="u-hero u-hero--pad"><div class="chamfer brackets specframe" style="--c:24px">
        <svg viewBox="0 0 240 80" preserveAspectRatio="none"><use href="#g-spectrum"/></svg><i class="playhead"></i>
        <div class="sg-mono u-dim" style="display:flex;justify-content:space-between"><span>1:42</span><span>L · R</span><span>−2:51</span></div>
      </div></div>
      {DIV}
      <section class="u-body u-body--end">
        <div><h3 class="sg-wordmark" style="margin:0;font-size:22px;color:var(--ground-hi)">Night transit</h3><div class="sg-mono u-dim" style="margin-top:6px">LOW ORBIT CHOIR — SIGNAL FADE</div></div>
        <div class="slot" style="--p:38%"></div>
        <div style="display:flex;justify-content:center;align-items:center;gap:22px;margin-top:6px">
          <button class="btn btn--ghost btn--icon" type="button" aria-label="Previous"><svg style="transform:scaleX(-1)"><use href="#g-skip"/></svg></button>
          <button class="btn btn--coral" type="button" aria-label="Play" style="width:72px;height:72px;padding:0;--c:16px"><svg style="width:26px;height:26px"><use href="#g-play"/></svg></button>
          <button class="btn btn--ghost btn--icon" type="button" aria-label="Next"><svg><use href="#g-skip"/></svg></button>
        </div>
        <div class="ruler" style="--v:70%"><div class="ruler-ticks"></div><div class="ruler-labels"><span>VOL</span><span>20</span><span>40</span><span>60</span><span>80</span><span>100</span></div></div>
      </section>'''))

# ---------------------------------------------------------------- G radar
S['G'] = fig('G', 'Radar scan', 'An octagonal scope in a cut frame is the hero. Only the device you can act on is coral.', utility(f'''
      {mast('Nearby', '<span class="sg-fr">balayage en cours</span>', '6 found', meta('2.4 / 5<br>GHZ'))}
      <div class="u-hero u-hero--pad"><div class="chamfer brackets scope" style="--c:24px">
        <svg><use href="#g-scope"/></svg>
        <svg class="blip" style="left:63%;top:24%;color:var(--coral)"><use href="#g-mark"/></svg>
        <div class="callout" style="left:calc(63% + 7px);top:calc(24% + 7px);--d:30px"><i></i><b></b><span>AX-04 · 2 M</span></div>
        <svg class="blip" style="left:31%;top:62%"><use href="#g-mark"/></svg>
        <svg class="blip" style="left:66%;top:71%"><use href="#g-mark"/></svg>
      </div></div>
      {DIV}
      <section class="u-body">
        <div>
          <div class="row"><svg width="16" height="16" style="color:var(--coral)"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">AX-04 router</span><span class="sg-mono">AX:04:E1:9C · 2 M</span></span><svg width="20" height="20" style="color:var(--ground-hi)"><use href="#g-signal"/></svg></div>
          <div class="row"><svg width="16" height="16" style="color:var(--ground-hi)"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">TV room</span><span class="sg-mono">5C:11:A0:3F · 6 M</span></span><svg width="20" height="20" style="color:var(--ground-dim)"><use href="#g-signal"/></svg></div>
          <div class="row"><svg width="16" height="16" style="color:var(--ground-hi)"><use href="#g-mark"/></svg><span><span class="sg-label" style="display:block">Unknown device</span><span class="sg-mono">F2:88:07:D4 · 11 M</span></span><svg width="20" height="20" style="color:var(--ground-3)"><use href="#g-signal"/></svg></div>
        </div>
      </section>''', tab=tabbar(TAB_VPN, 2)))

# ---------------------------------------------------------------- H inbox
rows = [('LS', 'Lena Sato', 'ROUTE MAP FOR FRIDAY IS ATTACHED', '09:12', True, ''), ('OP', 'Ops desk', 'KEY ROTATION COMPLETE · 3 DEVICES', '08:40', True, ''),
        ('RK', 'Rui Kemp', 'OK — SEE YOU AT THE NORTH GATE', 'MON', False, ''), ('09', 'Unit 09', 'WEEKLY REPORT · 14 PAGES', 'SUN', False, ' av--line'),
        ('AM', 'Ada Mensah', 'PHOTOS FROM THE FIELD TRIP', 'SAT', False, '')]
rowhtml = ''.join(f'<div class="row"><span class="av{c}">{i}</span><span><span class="sg-label" style="display:block">{n}</span><span class="sg-mono">{m}</span></span>'
                  f'<span style="display:grid;justify-items:end;gap:6px"><span class="sg-mono">{t}</span>{"<i class=unread></i>" if u else ""}</span></div>' for i, n, m, t, u, c in rows)
S['H'] = fig('H', 'Inbox', 'No hero form, so the filter takes the hero slot and the compose action is the masthead tag. Coral only marks unread.', utility(f'''
      {mast('Inbox', '12 unread', 'end-to-end', '<button class="u-tag-btn btn btn--plate btn--icon" type="button" aria-label="New message"><svg><use href="#g-plus"/></svg></button>')}
      <div class="u-hero u-hero--pad"><div class="seg"><button type="button" aria-pressed="true">all</button><button type="button">flagged</button><button type="button">sealed</button></div></div>
      {DIV}
      <section class="u-body"><div>{rowhtml}</div></section>''', tab=tabbar([('mark', 'inbox'), ('x-line', 'spam'), ('grid', 'contacts'), ('head', 'me')], 0)))


# ---------------------------------------------------------------- I settings
def group(label, n, rows_):
    return f'<div><div class="u-label"><span>{label}</span><span>{n}</span></div>{rows_}</div>'


tg = lambda id_, label, small, on: f'<div class="set"><span><span class="sg-label">{label}</span>{f"<small>{small}</small>" if small else ""}</span><input class="tgl" type="checkbox" id="{id_}"{" checked" if on else ""} aria-label="{label}"></div>'
nav = lambda label, val: f'<div class="set"><span class="sg-label">{label}</span><span class="sg-mono u-dim" style="display:flex;gap:6px;align-items:center">{val} <svg width="10" height="10"><use href="#g-chev"/></svg></span></div>'
S['I'] = fig('I', 'Settings', 'No hero, so the hazard bar follows the masthead directly. Groups are condensed-caps labels over printed rows. 設定 means settings.', utility(f'''
      {mast('Settings', 'v 4.2', 'build 2611', jp('設定'))}
      <div class="u-div hazard" style="margin-top:20px"></div>
      <section class="u-body u-body--end" style="gap:18px">
        {group('Privacy', '01', tg('s-ks', 'Kill switch', 'PAUSE TRAFFIC IF THE TUNNEL DROPS', True) + tg('s-bt', 'Block trackers', '1,284 BLOCKED THIS WEEK', True) + tg('s-ln', 'Allow local network', 'PRINTERS · CASTING · SMART HOME', False))}
        {group('Network', '02', nav('Protocol', 'WIREGUARD') + nav('Server', 'LISBON-04'))}
        {group('Display', '03', tg('s-st', 'Stripe texture', '', True) + tg('s-rm', 'Reduce motion', '', False))}
      </section>'''))

# ---------------------------------------------------------------- J credential
S['J'] = fig('J', 'ID credential', 'The badge is the hero plate, with the line-art head in brackets, a coral strip and a barcode. 身分証明書 means ID certificate.', utility(f'''
      {mast('Credential', '<span class="sg-fr">carte de membre</span>', 'axiom', meta('VALID<br>2028'))}
      <div class="u-hero u-hero--pad"><div class="badge plate cut">
        <i class="badge-strip"></i>
        <span class="badge-av brackets"><svg><use href="#g-head"/></svg></span>
        <div class="badge-num"><span class="sg-num">09</span><span class="sg-cap" style="font-size:10px">Clearance</span></div>
        <h3 class="sg-wordmark">Mira<br>Okafor</h3>
        <div class="sg-mono badge-f">UNIT&nbsp;&nbsp;&nbsp; FIELD OPS<br>ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; AX-0917-C53<br>ISSUED&nbsp; 2026-03-02</div>
        <span class="sg-jp-v badge-jp">身分証明書</span>
        <svg class="badge-bc" viewBox="0 0 21 21" style="width:62px;height:62px;color:var(--ink)"><use href="#g-matrix"/></svg>
      </div></div>
      {DIV}
      <section class="u-body u-body--end"><div style="display:grid;grid-template-columns:1fr auto;gap:12px"><button class="btn" type="button">Add to wallet</button><button class="btn btn--ghost" type="button">Show QR</button></div></section>'''))

# ---------------------------------------------------------------- K alert
S['K'] = fig('K', 'Alert sheet', 'Interruptions get the only large coral surface: a sheet with a 45° cut corner and a hazard strip. Nothing else competes.', f'''<div class="phone"><div class="scr u tex">
      {SB}
      {mast('Protected', 'since 08:14', 'lis-04', jp('保護中'))}
      <div class="u-hero">{BAR(100, 30, style='width:270px')}</div>
      {DIV}
      <section class="u-body"></section>
      <i class="dim" style="position:absolute;inset:0;z-index:5"></i>
      <div class="u-sheet" style="z-index:10">
        <div class="hazard" style="--hz:#0c0c0a;margin-right:40px"></div>
        <div style="display:flex;justify-content:space-between;align-items:center"><svg width="44" height="44"><use href="#g-warn"/></svg><span class="sg-mono t-right">ERR 0X09<br>14:22:07</span></div>
        <h3 class="sg-wordmark" style="margin:0;font-size:22px">Connection<br>dropped</h3>
        <p class="sg-mono" style="margin:0;font-size:12px;line-height:1.5">LISBON-04 STOPPED RESPONDING. THE KILL SWITCH HAS PAUSED ALL TRAFFIC UNTIL YOU RECONNECT OR PICK ANOTHER SERVER.</p>
        <button class="btn btn--ink btn--block" type="button">Reconnect</button>
        <button class="btn btn--ghost btn--block" type="button" style="--btn-line:#0c0c0a;--btn-fill:var(--coral)">Choose another server</button>
      </div>
      <i class="home" style="--hb:#0c0c0a;z-index:40"></i>
    </div></div>''')

# ---------------------------------------------------------------- O editorial
S['O'] = fig('O', 'Long read', 'The headline is the hero, set at display size. A French pull quote with a coral rule is the one ornament in the body.', utility(f'''
      {mast('Field notes', 'nº 09 · lena sato', '6 min', jp('第九号'))}
      <div class="u-hero u-hero--pad"><h3 class="sg-display" style="margin:0;font-size:34px;color:var(--ground-hi)">The quiet<br>network</h3></div>
      {DIV}
      <section class="u-body u-body--end" style="gap:18px">
        <p class="sg-label" style="margin:0;font-size:15px;line-height:1.55">Most of what keeps you safe online is invisible. Packets leave your phone, cross three relays and arrive without anyone reading them.</p>
        <blockquote style="margin:0;padding-left:16px;border-left:4px solid var(--coral)"><div class="sg-fr" style="font-size:20px;line-height:1.2;color:var(--ground-hi)">« Le réseau le plus sûr est celui qu'on n'entend pas. »</div><div class="sg-mono u-dim" style="margin-top:8px">THE SAFEST NETWORK IS THE ONE YOU CAN'T HEAR</div></blockquote>
        <p class="sg-label" style="margin:0;font-size:15px;line-height:1.55">That is the brief for AXIOM 4.2: fewer alerts, faster tunnels, and a kill switch you never think about.</p>
        <div style="margin-top:auto"><div class="slot" style="--p:38%"></div><div class="sg-mono u-dim" style="display:flex;justify-content:space-between;margin-top:8px"><span>READ 38%</span><span>02 / 05</span></div></div>
      </section>'''))

# ---------------------------------------------------------------- P paywall
S['P'] = fig('P', 'Paywall', 'The chevron print is the hero. Plans print as frames with the chosen one as a plate. One coral action, with French fine print.', utility(f'''
      {mast('Axiom pro', 'every relay', 'every device', seal('認定'))}
      <div class="u-hero u-hero--pad" style="display:flex;justify-content:flex-end"><svg viewBox="0 0 300 230" style="width:220px;height:auto;color:var(--ground-hi)"><use href="#g-chevrons"/></svg></div>
      {DIV}
      <section class="u-body u-body--end">
        <div class="ticket" style="--stub:84px"><div><div class="sg-cap" style="font-size:11px">Monthly</div><div class="sg-num" style="font-size:24px;margin-top:4px">€4.99</div></div><div><span class="sg-mono">PER</span><span class="sg-stencil" style="font-size:22px">MO</span></div></div>
        <div class="ticket" style="--stub:84px;position:relative;background:var(--ground-hi);color:var(--ground)"><div><div class="sg-cap" style="font-size:11px">Yearly</div><div class="sg-num" style="font-size:24px;margin-top:4px">€39.00</div></div><div style="border-left-color:var(--ground-dim)"><span class="sg-mono">PER</span><span class="sg-stencil" style="font-size:22px">YR</span></div><span class="stamp" style="position:absolute;right:98px;top:16px;font-size:14px;--gap:var(--ground-hi)">Save 35%</span></div>
        <div class="sg-mono" style="color:var(--ground-hi)">10 DEVICES · 60 RELAY CITIES · PRIORITY TUNNELS</div>
        <button class="btn btn--coral btn--block" type="button">Start 7-day free trial</button>
        <div class="sg-fr u-dim" style="text-align:center;font-size:11.5px">Résiliable à tout moment · paiement via l'App Store</div>
      </section>'''))

# ---------------------------------------------------------------- poster tier
S['A'] = fig('A', 'Launch', 'Reference 1 made industrial: two cut bars, the 45° coral band, a hard X and right-aligned telemetry. The bar slot is the boot progress.', f'''<div class="phone"><div class="scr tex">
      <i class="facet" style="clip-path:polygon(0 0,100% 0,100% 6%,0 34%)"></i>
      {SB}
      <div style="top:64px;left:22px;display:flex;align-items:flex-end;gap:8px;color:var(--ground-hi)"><span class="u-code" style="position:static">SK·09·LIS</span><span class="sg-display" style="font-size:40px">AXIOM</span></div>
      <div class="sg-cap" style="top:116px;left:42px;font-size:12px;color:var(--ground-dim)">Secure workspace</div>
      <i class="band" style="top:56px;right:0;width:120px;height:120px;clip-path:polygon(100% 0,100% 100%,0 100%)"></i>
      <svg style="top:150px;right:20px;width:84px;height:84px;color:var(--ground-hi)"><use href="#g-x-line"/></svg>
      {BAR(104, 100, style='top:164px;left:0;width:260px')}
      <div class="sg-jp-v" style="top:296px;left:28px;color:var(--ground-dim)">安全な作業空間</div>
      {BAR(104, 58, cls='bar--bleed-r', style='top:290px;left:72px;right:0')}
      <i class="band" style="top:420px;left:0;width:240px;height:240px;clip-path:polygon(150px 0,240px 0,0 240px,0 150px)"></i>
      <div class="t-right" style="top:430px;right:24px;color:var(--ground-hi)"><div class="sg-num" style="font-size:28px">09</div><div class="sg-mono" style="margin-top:8px;font-size:12px;line-height:1.5">REF:<br>OPSEC/AHI<br>SP C53</div></div>
      <div class="barcode" style="top:548px;right:24px;width:96px;height:72px;--bc:var(--ground-hi)"></div>
      <div class="bootlog" style="top:668px;left:24px;right:24px"><span>Keys verified</span><span>Relays 3 / 3</span><span class="run">Sealing tunnel · 64%<i class="caret"></i></span></div>
      <div class="hazard hazard--run" style="top:740px;left:24px;right:24px"></div>
      <div class="slot slot--signal" style="top:780px;left:24px;right:24px;--p:64%"></div>
      <i class="home"></i>
    </div></div>''', tier='poster')

S['L'] = fig('L', 'Empty state', 'Two hard X outlines make the illustration, and 圏外 (out of range) is what Japanese phones show. The coral wedge is the 45° motif.', f'''<div class="phone"><div class="scr tex">
      {SB}
      <svg style="top:96px;left:-36px;width:310px;height:310px;color:var(--ground-3)"><use href="#g-x-line"/></svg>
      <svg style="top:250px;left:196px;width:150px;height:150px;color:var(--ground-hi)"><use href="#g-x-line"/></svg>
      <div class="sg-mono" style="top:70px;right:24px;color:var(--ground-dim)">ERR 0X09</div>
      <h3 class="sg-display" style="margin:0;top:446px;left:24px;font-size:40px;color:var(--ground-hi)">No<br>signal</h3>
      <div class="sg-jp" style="top:444px;right:24px;font-size:40px;line-height:1.05;writing-mode:vertical-rl;color:var(--ground-hi)">圏外</div>
      <div class="caution" style="top:544px;left:24px;right:24px"><div><svg><use href="#g-warn"/></svg><b>Out of range</b><p>WE COULDN'T REACH THE NETWORK. CHECK WI-FI OR MOBILE DATA.</p></div></div>
      <div style="top:652px;left:24px;right:24px;display:grid;gap:10px"><button class="btn btn--block" type="button">Try again</button><button class="btn btn--ghost btn--block" type="button">Open offline files</button></div>
      <i class="band" style="right:0;bottom:0;width:110px;height:110px;clip-path:polygon(100% 0,100% 100%,0 100%)"></i>
      <i class="home"></i>
    </div></div>''', tier='poster')

S['M'] = fig('M', 'Onboarding', 'Three cut bars in alternating directions, then the hazard bar and a display headline with French above it.', f'''<div class="phone"><div class="scr tex">
      {SB}
      <div class="sg-mono" style="top:70px;left:24px;color:var(--ground-dim)">STEP 02 / 03</div>
      <div class="sg-mono t-right" style="top:70px;right:24px;color:var(--ground-hi)">SKIP</div>
      {BAR(88, 100, style='top:110px;left:0;width:300px')}
      {BAR(88, 66, cls='bar--bleed-r', style='top:212px;left:44px;right:0')}
      {BAR(88, 20, style='top:314px;left:0;width:240px')}
      <svg style="top:318px;right:24px;width:80px;height:80px;color:var(--ground-hi)"><use href="#g-x-solid"/></svg>
      <div class="hazard" style="top:440px;left:24px;right:24px"></div>
      <div style="top:490px;left:24px;right:24px;color:var(--ground-hi)"><div class="sg-fr" style="font-size:13px">acheminer chaque paquet</div><h3 class="sg-display" style="margin:10px 0 0;font-size:40px">Route<br>every<br>packet</h3><p class="sg-mono" style="margin:14px 0 0;font-size:12px;color:var(--on-ground)">THREE RELAYS · TWO KEYS · ZERO LOGS</p></div>
      <ol class="steps" style="top:761px;left:24px;width:200px"><li class="done">Scan</li><li class="on">Keys</li><li>Seal</li></ol>
      <button class="btn" type="button" style="top:752px;right:24px">Next<svg><use href="#g-arrow"/></svg></button>
      <i class="home"></i>
    </div></div>''', tier='poster')

S['N'] = fig('N', 'Lock screen', 'The manifesto, after reference 2: the only place all three languages stack, with chevrons, hazard bar and a worn screen-print filter.', f'''<div class="phone"><div class="scr tex">
      {SB}
      <div style="top:64px;left:28px;right:28px;display:flex;flex-direction:column;gap:11px;color:var(--ground-hi)">
        <div style="display:flex;align-items:flex-end;gap:8px"><span class="u-code" style="position:static">SK·09·LIS</span><span class="sg-display wear" style="font-size:46px">AXIOM</span></div>
        <div style="display:flex;justify-content:space-between;align-items:baseline"><span class="sg-fr" style="font-size:14px">lundi 16 novembre</span><span class="sg-num" style="font-size:14px">9:41</span></div>
        <div style="display:flex;gap:14px;align-items:center"><div class="slab-cut wear" style="flex:1;height:56px"></div><svg width="58" height="58"><use href="#g-head"/></svg></div>
        <div class="yearspan sg-num" style="font-size:21px">20<i></i>26</div>
        <div style="display:grid;gap:3px">
          <div class="sg-wordmark" style="font-size:20px">Signal engineering</div>
          <div class="sg-jp sg-justify" style="font-size:22px">信号工学</div>
          <div class="sg-wordmark" style="font-size:20px">Ingénierie du signal</div>
        </div>
        <svg class="wear" viewBox="0 0 300 230" style="width:84%;height:auto;align-self:center;margin-top:2px"><use href="#g-chevrons"/></svg>
        <div class="hazard wear"></div>
        <div class="sg-wordmark" style="font-size:15px">Axiom signal systems</div>
        <div><div class="barcode--v" style="height:30px;--bc:var(--ground-hi)"></div><div class="sg-mono" style="display:flex;justify-content:space-between;font-size:9px;margin-top:4px"><span>4</span><span>902609</span><span>260911</span><span>9</span></div></div>
      </div>
      <span class="cut" style="bottom:40px;left:44px;width:50px;height:50px;--c:10px;background:color-mix(in srgb, var(--ground-hi) 14%, transparent);display:grid;place-items:center"><svg width="20" height="20" style="color:var(--ground-hi)"><use href="#g-plus"/></svg></span>
      <span class="cut" style="bottom:40px;right:44px;width:50px;height:50px;--c:10px;background:color-mix(in srgb, var(--ground-hi) 14%, transparent);display:grid;place-items:center"><svg width="22" height="22" style="color:var(--ground-hi)"><use href="#g-reticle"/></svg></span>
      <i class="home"></i>
    </div></div>''', tier='poster')


# ---------------------------------------------------------------- Q device
S['Q'] = fig('Q', 'Device info', 'A riveted data plate inside crop marks is the hero. The body has a caution tag, a rocker switch and the palette calibration strip.', utility(f"""
      {mast('Device', 'unit ax-04', 'rev 2.6', meta('SN<br>0917'))}
      <div class="u-hero u-hero--pad" style="padding-top:30px"><div class="marks"><div class="dataplate">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px"><span class="sg-wordmark" style="font-size:15px">AXIOM</span><span class="sg-stencil" style="font-size:26px">AX-04</span></div>
        <div style="display:grid;grid-template-columns:1fr 70px;gap:16px;align-items:end"><div class="spec"><span>Serial</span><i></i><span>0917-C53</span><span>Firmware</span><i></i><span>4.2.0</span><span>Relay</span><i></i><span>LIS-04</span><span>Uptime</span><i></i><span>41 D</span></div>
        <svg viewBox="0 0 21 21" width="70" height="70" style="color:var(--ink)"><use href="#g-matrix"/></svg></div>
      </div></div></div>
      {DIV}
      <section class="u-body u-body--end">
        <div class="caution"><div><svg><use href="#g-warn"/></svg><b>Firmware 4.2.1</b><p>REBOOT REQUIRED. THE TUNNEL PAUSES FOR 40 S.</p></div></div>
        <div class="set"><span><span class="sg-label">Maintenance mode</span><small>ROUTE AROUND THIS UNIT</small></span><input class="rocker" type="checkbox" id="q-m" aria-label="Maintenance mode"></div>
        <button class="btn btn--block" type="button">Install update</button>
        <div class="colorbar" style="margin-top:auto"><span style="--k:var(--ground)">gnd</span><span style="--k:var(--ground-3)">g-3</span><span style="--k:var(--ground-hi)">print</span><span style="--k:var(--sage)">sage</span><span style="--k:var(--sage-hi)">plate</span><span style="--k:var(--ink)">ink</span><span style="--k:var(--coral)">coral</span></div>
      </section>"""))

# ---------------------------------------------------------------- R interval timer
S['R'] = fig('R', 'Interval timer', 'A seven-segment clock with a coral colon is the hero. Rounds print as a cell meter and intensity as a ruler. The one action is a keycap. 計時 means timekeeping.', utility(f"""
      {mast('Interval', 'round 3', 'of 8', jp('計時'))}
      <div class="u-hero u-hero--pad" style="display:grid;justify-items:center;gap:10px">{seg7("02:47", 92, "2")}<div class="sg-mono u-dim">WORK 45 S · REST 15 S · NEXT: REST</div></div>
      {DIV}
      <section class="u-body u-body--end" style="gap:16px">
        <div><div class="u-label" style="margin-bottom:10px"><span>Rounds</span><span>3 / 8</span></div>{cells(8, 2, hot=2, tall=True)}</div>
        <div><div class="u-label" style="margin-bottom:4px"><span>Intensity</span><span>7</span></div><div class="ruler" style="--v:70%"><div class="ruler-ticks"></div><div class="ruler-labels"><span>0</span><span>2</span><span>4</span><span>6</span><span>8</span><span>10</span></div></div></div>
        <button class="keycap" type="button" style="margin-top:6px"><span>Pause</span><small>HOLD 1 S TO END</small><i class="led"></i></button>
      </section>"""))

# ---------------------------------------------------------------- S transfer
S['S'] = fig('S', 'Transfer', 'Chevron steps are the hero. The transfer prints as a ticket stub with a worn stamp, and sending is a keycap. 確認 means confirm. French fine print.', utility(f"""
      {mast('Transfer', 'step 2', 'of 3', seal('確認'))}
      <div class="u-hero u-hero--pad"><ol class="steps"><li class="done">Amount</li><li class="on">Confirm</li><li>Sent</li></ol></div>
      {DIV}
      <section class="u-body u-body--end" style="gap:16px">
        <div class="ticket" style="position:relative"><div><div class="sg-cap" style="font-size:11px">To · Lena Sato</div><div class="sg-num" style="font-size:30px;margin-top:6px">€240.00</div><div class="sg-mono" style="margin-top:6px">FRIDAY ROUTE</div></div><div><span class="sg-mono">Nº</span><span class="sg-stencil" style="font-size:26px">0917</span></div>
          <span class="stamp" style="position:absolute;right:104px;bottom:14px;font-size:14px;--gap:var(--sage-hi)">Verified</span></div>
        <div class="spec spec--ground"><span>From</span><i></i><span>Main ·· 4417</span><span>Arrives</span><i></i><span>Instantly</span><span>Fee</span><i></i><span>€0.00</span></div>
        <button class="keycap" type="button" style="margin-top:6px"><span>Send €240</span><small>HOLD 1 S</small><i class="led"></i></button>
        <div class="sg-fr u-dim" style="text-align:center;font-size:12px">virement instantané · sans frais</div>
      </section>"""))

ORDER = 'T A B C D E F G H I J K L M N O P Q R S'.split()
grid = '\n'.join(S[k] for k in ORDER)
src = SRC.read_text()
a = src.index('<div class="screens">') + len('<div class="screens">')
b = src.index('  </div>\n</section>', a)
SRC.write_text(src[:a] + '\n' + grid + '\n' + src[b:])
print('screens:', grid.count('<figure'))
