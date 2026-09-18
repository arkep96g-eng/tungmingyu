#!/usr/bin/env python3
"""Build the static portfolio site from data/*.json.

    python build.py                      -> writes index.html, itri.html, publications.html,
                                            somnics.html, style.css, app.js next to this file
    python build.py --artifact --out DIR -> same pages, CSS/JS inlined, no <html>/<head> wrapper
                                            (the format the Claude Artifact publisher expects)

No third-party dependencies.
"""
import argparse
import datetime as dt
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"


def esc(s):
    return html.escape(str(s), quote=True)


def bi(en, zh):
    """Bilingual span pair; CSS shows one of them depending on <html data-lang>."""
    if en == zh:
        return esc(en)
    return f'<span class="en">{esc(en)}</span><span class="zh">{esc(zh)}</span>'


# --------------------------------------------------------------------------- CSS / JS

CSS_QUIET = """
:root{
  --bg:#F4F6F5; --surface:#FFFFFF; --ink:#172326; --muted:#5B6B6E; --line:#D6DDDC;
  --accent:#176F6A; --accent-ink:#0F4E4A; --accent-soft:#E1EFEC; --mono-bg:#EEF2F1;
  --shadow:0 1px 2px rgba(23,35,38,.06);
  --font-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI","Noto Sans TC","PingFang TC",sans-serif;
  --font-display:"Familjen Grotesk","IBM Plex Sans",system-ui,"Noto Sans TC",sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0F1718; --surface:#162022; --ink:#E4EBE9; --muted:#98A8A6; --line:#263335;
    --accent:#55BDB3; --accent-ink:#8FD8D0; --accent-soft:#163330; --mono-bg:#1C282A;
    --shadow:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  --bg:#0F1718; --surface:#162022; --ink:#E4EBE9; --muted:#98A8A6; --line:#263335;
  --accent:#55BDB3; --accent-ink:#8FD8D0; --accent-soft:#163330; --mono-bg:#1C282A;
  --shadow:0 1px 2px rgba(0,0,0,.4);
}
*{box-sizing:border-box}
html{color-scheme:light dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-size:16px;line-height:1.55;
  -webkit-font-smoothing:antialiased}
:root:not([data-lang="zh"]) .zh{display:none}
:root[data-lang="zh"] .en{display:none}
:root[data-lang="zh"] body{font-size:16.5px}
a{color:var(--accent-ink);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
.wrap{max-width:960px;margin:0 auto;padding-block:0 64px;padding-inline:20px}
h1,h2,h3{font-family:var(--font-display);text-wrap:balance;margin:0;line-height:1.15;letter-spacing:-.01em}
h1{font-size:clamp(30px,5vw,42px);font-weight:700}
h2{font-size:22px;font-weight:700;margin-top:48px;margin-bottom:16px}
h3{font-size:18px;font-weight:600}
p{margin:0}
.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}
.muted{color:var(--muted)}
.mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums}

/* header */
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;
  padding-block:18px;border-bottom:1px solid var(--line);margin-bottom:40px}
.brand{font-family:var(--font-display);font-weight:700;font-size:17px;color:var(--ink)}
.brand .zh-name{font-family:var(--font-body);font-weight:500;color:var(--muted);margin-left:8px}
.nav{display:flex;gap:4px 18px;align-items:center;flex-wrap:wrap;font-size:14px}
.nav a{color:var(--muted);padding:4px 0}
.nav a[aria-current="page"]{color:var(--ink);font-weight:600;border-bottom:2px solid var(--accent)}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:999px;overflow:hidden;margin-left:8px}
.lang button{font:inherit;font-size:12.5px;font-weight:600;padding:4px 10px;border:0;background:transparent;color:var(--muted);cursor:pointer}
.lang button[aria-pressed="true"]{background:var(--accent);color:var(--bg)}

/* hero */
.hero{display:grid;gap:14px;max-width:70ch}
.hero h1 .zh-name{font-family:var(--font-body);font-weight:500;font-size:.6em;color:var(--muted)}
.hero .tag{font-size:15px;color:var(--accent-ink);font-weight:600}
.hero p.intro{font-size:17px;color:var(--ink);max-width:65ch}
.figures{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:28px;padding-block:18px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.figures div{display:flex;flex-direction:column;gap:2px}
.figures b{font-family:var(--font-display);font-size:24px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
.figures span{font-size:12.5px;color:var(--muted)}

/* eras */
.eras{display:grid;gap:0;border-top:1px solid var(--line)}
.era{display:grid;grid-template-columns:120px 1fr auto;gap:8px 20px;align-items:baseline;padding-block:16px;border-bottom:1px solid var(--line)}
.era .years{font-family:var(--font-mono);font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.era .org{font-weight:600}
.era .role{font-size:14.5px;color:var(--muted)}
.era .cta{font-size:14px;font-weight:600;white-space:nowrap}
@media (max-width:560px){.era{grid-template-columns:1fr}.era .cta{white-space:normal}}

.domains{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:500;padding:5px 11px;border-radius:999px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.chip.count{color:var(--muted)}
.chip .n{font-family:var(--font-mono);font-size:12px;color:var(--muted)}

/* filter bar */
.filter{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 20px}
.filter button{font:inherit;font-size:13px;font-weight:500;padding:5px 12px;border-radius:999px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);cursor:pointer}
.filter button[aria-pressed="true"]{background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);font-weight:600}

/* family cards */
.families{display:grid;gap:14px}
.fam{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:18px 20px;box-shadow:var(--shadow);scroll-margin-top:16px}
.fam[hidden]{display:none}
.fam header{display:grid;gap:6px;margin-bottom:10px}
.fam h3{font-size:17px}
.fam .alt{font-size:14.5px;color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;color:var(--muted);align-items:center}
.meta .role{color:var(--accent-ink);font-weight:600}
.meta .role.sole,.meta .role.first{background:var(--accent-soft);padding:1px 8px;border-radius:999px}
.fam .desc{font-size:15px;margin:8px 0 12px;max-width:70ch}
.pubs{display:grid;gap:4px;margin:0;padding:0;list-style:none}
.pubs li{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:10px;align-items:baseline;font-size:14px;padding:5px 0;border-top:1px dashed var(--line)}
.pubs li:first-child{border-top:0}
.cc{font-family:var(--font-mono);font-size:11.5px;font-weight:600;letter-spacing:.04em;color:var(--accent-ink);background:var(--mono-bg);padding:2px 0;border-radius:3px;text-align:center}
.pn{font-family:var(--font-mono);font-size:13.5px;font-variant-numeric:tabular-nums}
.pn .val{font-size:12px;color:var(--muted);margin-left:8px;font-family:var(--font-body)}
.pn .ptitle{display:block;font-family:var(--font-body);font-size:13px;color:var(--muted)}
.kd{font-size:12.5px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
@media (max-width:480px){.pubs li{grid-template-columns:34px 1fr}.kd{grid-column:2}}
.related{font-size:13px;color:var(--muted);margin-top:12px}
.related a{margin-right:10px}

/* publications */
.paper{display:grid;grid-template-columns:56px minmax(0,1fr);gap:12px 18px;padding-block:18px;border-top:1px solid var(--line);scroll-margin-top:16px}
.paper:last-child{border-bottom:1px solid var(--line)}
.paper .year{font-family:var(--font-mono);font-size:14px;color:var(--muted);padding-top:3px;font-variant-numeric:tabular-nums}
.paper h3{font-size:16.5px;font-weight:600;line-height:1.3}
.paper .authors{font-size:14px;color:var(--muted);margin-top:6px}
.paper .authors b{color:var(--ink);font-weight:600}
.paper .venue{font-size:14px;margin-top:4px}
.paper .venue i{font-style:italic}
.paper .summary{font-size:14.5px;margin-top:8px;max-width:68ch}
.paper .links{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:10px;font-size:13px;align-items:center}
.pill{display:inline-block;font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;background:var(--accent-soft);color:var(--accent-ink)}
.pill.quiet{background:var(--mono-bg);color:var(--muted);font-weight:500}
@media (max-width:480px){.paper{grid-template-columns:1fr}.paper .year{padding-top:0}}

.note{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:4px;padding:12px 16px;font-size:14px;max-width:72ch;margin-bottom:24px}
.lede{font-size:16px;max-width:68ch;margin-bottom:24px}

footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--line);font-size:13px;color:var(--muted);display:grid;gap:8px}
footer .ext{display:flex;flex-wrap:wrap;gap:6px 18px}
@media (prefers-reduced-motion:no-preference){.fam,.filter button{transition:background .15s,border-color .15s}}
"""

CSS_BOLD = """
:root{
  --bg:#FFFFFF;--surface:#F5F5F5;--ink:#0A0A0A;--muted:#5A5A5A;
  --line:#E2E2E2;--accent:#1730D0;--accent-ink:#1228C0;--accent-soft:#EEF0FD;--mono-bg:#F2F2F2;
  --font-body:"Barlow",system-ui,-apple-system,"Noto Sans TC","PingFang TC",sans-serif;
  --font-display:"Barlow Condensed",var(--font-body);
  --font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#111111;--surface:#1C1C1C;--ink:#F0F0F0;--muted:#888;
    --line:#2C2C2C;--accent:#5B72F4;--accent-ink:#8FA4FF;--accent-soft:#13183A;--mono-bg:#222;
  }
}
:root[data-theme="dark"]{
  --bg:#111111;--surface:#1C1C1C;--ink:#F0F0F0;--muted:#888;
  --line:#2C2C2C;--accent:#5B72F4;--accent-ink:#8FA4FF;--accent-soft:#13183A;--mono-bg:#222;
}
*{box-sizing:border-box}
html{color-scheme:light dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
:root:not([data-lang="zh"]) .zh{display:none}
:root[data-lang="zh"] .en{display:none}
:root[data-lang="zh"] body{font-size:16.5px}
a{color:var(--accent-ink);text-decoration:none}
a:hover{text-decoration:underline;text-underline-offset:3px}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
.wrap{max-width:960px;margin:0 auto;padding-block:0 64px;padding-inline:20px}
h1,h2,h3{font-family:var(--font-display);text-wrap:balance;margin:0;line-height:1.1}
h1{font-size:clamp(36px,6vw,52px);font-weight:800;text-transform:uppercase;letter-spacing:.02em}
h2{font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;margin-top:48px;padding-bottom:10px;margin-bottom:16px;border-bottom:2px solid var(--ink)}
h3{font-size:17px;font-weight:600;line-height:1.3;font-family:var(--font-body);text-transform:none;letter-spacing:0}
p{margin:0}
.eyebrow{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700}
.muted{color:var(--muted)}
.mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums}

/* header */
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding-block:16px;border-bottom:2px solid var(--ink);margin-bottom:40px}
.brand{font-family:var(--font-display);font-weight:800;font-size:16px;color:var(--ink);letter-spacing:.06em;text-transform:uppercase}
.brand .zh-name{font-family:var(--font-body);font-weight:400;color:var(--muted);margin-left:8px;text-transform:none;letter-spacing:0;font-size:14px}
.nav{display:flex;gap:4px 18px;align-items:center;flex-wrap:wrap;font-size:13.5px}
.nav a{color:var(--muted);padding:4px 0}
.nav a[aria-current="page"]{color:var(--ink);font-weight:700;border-bottom:2px solid var(--accent)}
.lang{display:inline-flex;border:1px solid var(--line);border-radius:2px;overflow:hidden;margin-left:8px}
.lang button{font:inherit;font-size:12px;font-weight:700;padding:4px 10px;border:0;background:transparent;color:var(--muted);cursor:pointer;letter-spacing:.05em}
.lang button[aria-pressed="true"]{background:var(--accent);color:#fff}

/* hero */
.hero{display:grid;gap:14px;max-width:72ch}
.hero h1{font-size:clamp(52px,9vw,88px);line-height:.96}
.hero h1 .zh-name{display:block;font-size:.28em;font-weight:400;text-transform:none;color:var(--muted);letter-spacing:0;font-family:var(--font-body);margin-top:10px}
.hero .tag{font-size:13px;color:var(--muted);font-weight:600;letter-spacing:.06em;text-transform:uppercase}
.hero p.intro{font-size:17px;color:var(--ink);max-width:65ch}
.figures{display:flex;flex-wrap:wrap;gap:0;margin-top:32px;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}
.figures div{display:flex;flex-direction:column;gap:3px;padding:14px 24px 12px;border-right:1px solid var(--line)}
.figures div:first-child{padding-left:0}
.figures div:last-child{border-right:none}
.figures b{font-family:var(--font-display);font-size:42px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.figures span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:600}

/* eras */
.eras{display:grid;gap:0;margin-top:16px}
.era{display:grid;grid-template-columns:120px 1fr auto;gap:6px 20px;align-items:baseline;padding-block:18px;border-bottom:1px solid var(--line)}
.era:first-child{border-top:1px solid var(--line)}
.era .years{font-family:var(--font-mono);font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.era .org{font-family:var(--font-display);font-weight:700;font-size:18px;text-transform:uppercase;letter-spacing:.02em}
.era .role{font-size:14px;color:var(--muted);margin-top:3px}
.era .cta{font-size:12px;font-weight:700;white-space:nowrap;letter-spacing:.05em;text-transform:uppercase;color:var(--accent-ink)}
@media (max-width:560px){.era{grid-template-columns:1fr}.era .cta{white-space:normal}}
.domains{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;padding:5px 11px;border-radius:2px;border:1px solid var(--line);background:var(--surface);color:var(--ink);text-transform:uppercase;letter-spacing:.04em}
.chip .n{font-family:var(--font-mono);font-size:12px;color:var(--muted)}

/* filter bar */
.filter{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 20px}
.filter button{font:inherit;font-size:12px;font-weight:700;padding:5px 12px;border-radius:2px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;text-transform:uppercase;letter-spacing:.04em}
.filter button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}

/* family cards */
.families{display:grid;gap:1px;background:var(--line);margin-top:16px;border:1px solid var(--line)}
.fam{background:var(--bg);padding:20px 22px;scroll-margin-top:16px}
.fam[hidden]{display:none}
.fam header{display:grid;gap:6px;margin-bottom:12px}
.fam h3{font-size:16px;font-weight:600;line-height:1.3}
.fam .alt{font-size:14px;color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:var(--muted);align-items:center}
.meta .role{font-weight:700;padding:2px 8px;border-radius:2px;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.meta .role.sole,.meta .role.first{background:var(--accent);color:#fff}
.meta .role.co{border:1px solid var(--accent);color:var(--accent);background:transparent}
.fam .desc{font-size:15px;margin:8px 0 14px;max-width:70ch}
.pubs{display:grid;gap:0;margin:0;padding:0;list-style:none}
.pubs li{display:grid;grid-template-columns:34px minmax(0,1fr) auto;gap:10px;align-items:baseline;font-size:14px;padding:6px 0;border-top:1px solid var(--line)}
.pubs li:first-child{border-top:none}
.cc{font-family:var(--font-mono);font-size:11px;font-weight:700;letter-spacing:.05em;color:var(--accent);background:var(--accent-soft);padding:2px 0;border-radius:2px;text-align:center}
.pn{font-family:var(--font-mono);font-size:13px;font-variant-numeric:tabular-nums}
.pn .val{font-size:12px;color:var(--muted);margin-left:8px;font-family:var(--font-body)}
.pn .ptitle{display:block;font-family:var(--font-body);font-size:13px;color:var(--muted)}
.kd{font-size:12px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
@media (max-width:480px){.pubs li{grid-template-columns:34px 1fr}.kd{grid-column:2}}
.related{font-size:13px;color:var(--muted);margin-top:14px}
.related a{margin-right:10px}

/* publications */
.paper{display:grid;grid-template-columns:56px minmax(0,1fr);gap:12px 18px;padding-block:18px;border-top:1px solid var(--line);scroll-margin-top:16px}
.paper:last-child{border-bottom:1px solid var(--line)}
.paper .year{font-family:var(--font-display);font-size:16px;font-weight:800;color:var(--muted);padding-top:2px;font-variant-numeric:tabular-nums;letter-spacing:.02em}
.paper h3{font-size:16px;font-weight:600;line-height:1.3;font-family:var(--font-body)}
.paper .authors{font-size:14px;color:var(--muted);margin-top:6px}
.paper .authors b{color:var(--ink);font-weight:600}
.paper .venue{font-size:14px;margin-top:4px}
.paper .venue i{font-style:italic}
.paper .summary{font-size:14.5px;margin-top:8px;max-width:68ch}
.paper .links{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:10px;font-size:13px;align-items:center}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:2px;background:var(--accent-soft);color:var(--accent);text-transform:uppercase;letter-spacing:.04em}
.pill.quiet{background:var(--mono-bg);color:var(--muted);font-weight:600;text-transform:none;letter-spacing:0}
@media (max-width:480px){.paper{grid-template-columns:1fr}.paper .year{padding-top:0}}

.note{background:var(--surface);border:none;border-left:3px solid var(--ink);border-radius:0;padding:14px 18px;font-size:14px;max-width:72ch;margin-bottom:24px}
.lede{font-size:16px;max-width:68ch;margin-bottom:0;margin-top:12px}

footer{margin-top:64px;padding-top:20px;border-top:2px solid var(--ink);font-size:13px;color:var(--muted);display:grid;gap:8px}
footer .ext{display:flex;flex-wrap:wrap;gap:6px 18px}
@media (prefers-reduced-motion:no-preference){.fam,.filter button{transition:background .12s,border-color .12s,color .12s}}
"""

FONTS_BOLD = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
              '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800'
              '&family=Barlow:wght@400;500;600&display=swap">')

JS = """
(function(){
  var root=document.documentElement;
  function setLang(l,save){
    root.setAttribute('data-lang',l); root.setAttribute('lang', l==='zh'?'zh-Hant':'en');
    document.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed', b.dataset.lang===l?'true':'false');});
    if(save){ try{localStorage.setItem('lang',l);}catch(e){} }
  }
  var saved=null; try{saved=localStorage.getItem('lang');}catch(e){}
  setLang(saved==='zh'?'zh':'en',false);
  document.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.lang,true);});});

  var bar=document.querySelector('.filter');
  if(bar){
    var cards=document.querySelectorAll('.fam');
    bar.addEventListener('click',function(e){
      var b=e.target.closest('button'); if(!b) return;
      bar.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
      b.setAttribute('aria-pressed','true');
      var d=b.dataset.domain;
      cards.forEach(function(c){ c.hidden = !(d==='all' || c.dataset.domain===d); });
    });
  }
})();
"""

FONTS_QUIET = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
               '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@600;700'
               '&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">')

THEMES = {"bold": (CSS_BOLD, FONTS_BOLD), "quiet": (CSS_QUIET, FONTS_QUIET)}


# --------------------------------------------------------------------------- data

site = json.loads((DATA / "site.json").read_text("utf-8"))
patents = json.loads((DATA / "patents.json").read_text("utf-8"))
papers = json.loads((DATA / "publications.json").read_text("utf-8"))
ALL_PAPERS = papers["journal"] + papers["conference"]
PAPER_BY_ID = {p["id"]: p for p in ALL_PAPERS}
FAMILY_BY_ID = {f["id"]: (grp, f) for grp in ("itri", "somnics") for f in patents[grp]["families"]}
TODAY = dt.date.today().isoformat()
THEME = site.get("theme", "bold")            # "bold" (Barlow, black rules, blue) or "quiet" (IBM Plex, teal)
CSS, FONTS = THEMES.get(THEME, THEMES["bold"])


def stats():
    fams = patents["itri"]["families"] + patents["somnics"]["families"]
    pubs = [p for f in fams for p in f["pubs"]]
    juris = set()
    for p in pubs:
        juris.add(p["cc"])
        juris.update(p.get("validated", []))
    juris.discard("WO")
    return {
        "families": len(fams),
        "pubs": len(pubs),
        "juris": len(juris),
        "papers": len(ALL_PAPERS),
        "first_author": sum(1 for p in ALL_PAPERS if p["me"] == 1),
        "citations": sum(p.get("citations", 0) for p in ALL_PAPERS),
    }


STATS = stats()


# --------------------------------------------------------------------------- components

def header(current):
    items = [("index.html", "Home", "首頁"), ("itri.html", "ITRI patents", "工研院專利"),
             ("publications.html", "Publications", "論文")]
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == current else ""}>{bi(en, zh)}</a>'
        for h, en, zh in items)
    return f"""
<div class="top">
  <a class="brand" href="index.html">{esc(site["name_en"])}<span class="zh-name">{esc(site["name_zh"])}</span></a>
  <nav class="nav" aria-label="Site">{nav}
    <span class="lang" role="group" aria-label="Language">
      <button type="button" id="lang-en" data-lang="en" aria-pressed="true">EN</button>
      <button type="button" id="lang-zh" data-lang="zh" aria-pressed="false">中文</button>
    </span>
  </nav>
</div>"""


def footer(current):
    links = site.get("links", {})
    ext = []
    if links.get("linkedin"):
        ext.append(f'<a href="{esc(links["linkedin"])}" rel="me">LinkedIn</a>')
    if links.get("scholar"):
        ext.append(f'<a href="{esc(links["scholar"])}">Google Scholar</a>')
    if links.get("orcid"):
        ext.append(f'<a href="{esc(links["orcid"])}">ORCID</a>')
    if current != "somnics.html":
        ext.append(f'<a href="somnics.html">{bi("Somnics inventions (public record)", "Somnics 發明（公開紀錄）")}</a>')
    ext.append(f'<a href="https://patents.google.com/?inventor=%22Tung-Ming+Yu%22">{bi("Google Patents inventor search", "Google Patents 發明人檢索")}</a>')
    return f"""
<footer>
  <div class="ext">{"".join(ext)}</div>
  <div>{bi("Bibliographic data verified against Google Patents and Crossref; last updated " + TODAY + ".",
            "書目資料已與 Google Patents 及 Crossref 核對；最後更新 " + TODAY + "。")}</div>
</footer>"""


def role_tag(role):
    r = patents["roles"][role]
    return f'<span class="role {role}">{bi(r["en"], r["zh"])}</span>'


def pub_row(p):
    cc = p["cc"]
    j = patents["jurisdictions"].get(cc, {"en": cc, "zh": cc})
    pn = esc(p["pn"])
    link = p.get("link", True)
    num = (f'<a class="pn" href="https://patents.google.com/patent/{pn}" target="_blank" rel="noopener">{pn}</a>'
           if link else f'<span class="pn">{pn}</span>')
    extra = ""
    if p.get("validated"):
        extra += f'<span class="val">{bi("validated in", "生效國")} {", ".join(p["validated"])}</span>'
    if p.get("title_en"):
        extra += f'<span class="ptitle">{bi(p["title_en"], p["title_zh"])}</span>'
    return (f'<li><span class="cc" title="{esc(j["en"])}">{esc(cc)}</span>'
            f'<span>{num}{extra}</span>'
            f'<span class="kd">{bi(p["kind_en"], p["kind_zh"])} · {esc(p["date"])}</span></li>')


def family_card(f, grp, show_desc):
    d = patents["domains"][f["domain"]]
    related = ""
    if show_desc and f.get("related_pubs"):
        links = "".join(f'<a href="publications.html#{esc(pid)}">{esc(PAPER_BY_ID[pid]["venue"])} {PAPER_BY_ID[pid]["year"]}</a>'
                        for pid in f["related_pubs"] if pid in PAPER_BY_ID)
        related = f'<div class="related">{bi("Related publications:", "相關論文：")} {links}</div>'
    desc = f'<p class="desc">{bi(f["desc_en"], f["desc_zh"])}</p>' if show_desc and f.get("desc_en") else ""
    n = len(f["pubs"])
    return f"""
<article class="fam" id="{esc(f["id"])}" data-domain="{esc(f["domain"])}">
  <header>
    <h3>{bi(f["title_en"], f["title_zh"])}</h3>
    <p class="alt">{bi(f["title_zh"], f["title_en"])}</p>
    <div class="meta">{role_tag(f["role"])}<span>{bi(d["en"], d["zh"])}</span>
      <span>{bi("Filed", "申請")} {esc(f["filed"])}</span>
      <span>{n} {bi("publication" if n == 1 else "publications", "件公告")}</span></div>
  </header>
  {desc}
  <ul class="pubs">{"".join(pub_row(p) for p in f["pubs"])}</ul>
  {related}
</article>"""


def filter_bar(families):
    counts = {}
    for f in families:
        counts[f["domain"]] = counts.get(f["domain"], 0) + 1
    btns = [f'<button type="button" data-domain="all" aria-pressed="true">{bi("All", "全部")} <span class="n">{len(families)}</span></button>']
    for k, d in patents["domains"].items():
        if k in counts:
            btns.append(f'<button type="button" data-domain="{k}" aria-pressed="false">{bi(d["en"], d["zh"])} <span class="n">{counts[k]}</span></button>')
    return f'<div class="filter" role="group" aria-label="Filter by domain">{"".join(btns)}</div>'


def paper_row(p):
    authors = ", ".join(f"<b>{esc(a)}</b>" if i + 1 == p["me"] else esc(a) for i, a in enumerate(p["authors"]))
    pills = []
    if p["me"] == 1:
        pills.append(f'<span class="pill">{bi("First author", "第一作者")}</span>')
    if p.get("citations"):
        pills.append(f'<span class="pill quiet">{p["citations"]} {bi("citations (Crossref)", "次引用（Crossref）")}</span>')
    doi = (f'<a class="mono" href="https://doi.org/{esc(p["doi"])}" target="_blank" rel="noopener">doi:{esc(p["doi"])}</a>'
           if p.get("doi") else f'<span class="mono muted">{bi("no DOI (proceedings)", "無 DOI（論文集）")}</span>')
    rel = ""
    if p.get("related_patents"):
        links = "".join(f'<a href="itri.html#{esc(fid)}">{bi(FAMILY_BY_ID[fid][1]["title_en"], FAMILY_BY_ID[fid][1]["title_zh"])}</a>'
                        for fid in p["related_patents"] if fid in FAMILY_BY_ID)
        rel = f'<div class="related">{bi("Related patents:", "相關專利：")} {links}</div>'
    return f"""
<article class="paper" id="{esc(p["id"])}">
  <div class="year">{p["year"]}</div>
  <div>
    <h3>{esc(p["title"])}</h3>
    <p class="authors">{authors}</p>
    <p class="venue"><i>{esc(p["venue"])}</i>, {esc(p["cite"])}</p>
    <p class="summary">{bi(p["summary_en"], p["summary_zh"])}</p>
    <div class="links">{doi}{"".join(pills)}</div>
    {rel}
  </div>
</article>"""


# --------------------------------------------------------------------------- pages

def page_home():
    s = STATS
    eras = ""
    for e in site["timeline"]:
        eras += f"""
<div class="era">
  <div class="years">{esc(e["years"])}</div>
  <div><div class="org">{bi(e["org_en"], e["org_zh"])}</div><div class="role">{bi(e["role_en"], e["role_zh"])}</div></div>
  <a class="cta" href="{esc(e["page"])}">{bi(e["cta_en"], e["cta_zh"])} →</a>
</div>"""
    fams = patents["itri"]["families"] + patents["somnics"]["families"]
    dom_counts = {}
    for f in fams:
        dom_counts[f["domain"]] = dom_counts.get(f["domain"], 0) + 1
    chips = "".join(f'<span class="chip">{bi(d["en"], d["zh"])} <span class="n">{dom_counts[k]}</span></span>'
                    for k, d in patents["domains"].items() if k in dom_counts)
    chips += f'<span class="chip">{bi("Optoelectronic microfluidics (papers)", "光電微流體（論文）")} <span class="n">{s["papers"]}</span></span>'
    return f"""
<section class="hero">
  <p class="eyebrow">{bi("Inventor portfolio", "發明人作品集")}</p>
  <h1>{esc(site["name_en"])} <span class="zh-name">{esc(site["name_zh"])}</span></h1>
  <p class="tag">{bi(site["tagline_en"], site["tagline_zh"])}</p>
  <p class="intro">{bi(site["intro_en"], site["intro_zh"])}</p>
</section>
<div class="figures">
  <div><b>{s["families"]}</b><span>{bi("patent families", "專利家族")}</span></div>
  <div><b>{s["pubs"]}</b><span>{bi("granted or published items", "核准／公開件數")}</span></div>
  <div><b>{s["juris"]}</b><span>{bi("jurisdictions", "國家／地區")}</span></div>
  <div><b>{s["papers"]}</b><span>{bi("peer-reviewed papers", "論文")}</span></div>
  <div><b>{s["citations"]}</b><span>{bi("citations (Crossref)", "引用次數（Crossref）")}</span></div>
</div>
<h2>{bi("Where the work was done", "工作歷程")}</h2>
<div class="eras">{eras}</div>
<h2>{bi("Technical domains", "技術領域")}</h2>
<div class="domains">{chips}</div>
"""


def page_itri():
    g = patents["itri"]
    fams = g["families"]
    n_pub = sum(len(f["pubs"]) for f in fams)
    return f"""
<p class="eyebrow">2003 – 2010 · {bi(g["assignee_en"], g["assignee_zh"])}</p>
<h1>{bi("ITRI patents", "工研院時期專利")}</h1>
<p class="lede" style="margin-top:12px">{bi(
    f"{len(fams)} patent families and {n_pub} granted or published items from research engineering at ITRI's biomedical division: "
    "negative-pressure wound care, an oral appliance for sleep apnea, and a run of microfluidic separation and positioning devices.",
    f"工研院生醫領域研發期間的 {len(fams)} 個專利家族、{n_pub} 件核准或公開案：負壓創傷照護、睡眠呼吸中止口腔裝置，以及一系列微流體分離與定位裝置。")}</p>
{filter_bar(fams)}
<div class="families">{"".join(family_card(f, "itri", True) for f in fams)}</div>
"""


def page_publications():
    s = STATS
    return f"""
<p class="eyebrow">2007 – 2013 · {bi("National Yang Ming Chiao Tung University", "國立陽明交通大學")}</p>
<h1>{bi("Publications", "論文著作")}</h1>
<p class="lede" style="margin-top:12px">{bi(
    "Doctoral research on optoelectronic tweezers, optoelectrowetting and PEGDA microfluidics — moving cells, particles, bubbles and droplets with projected light on organic photoconductor chips.",
    "博士研究：光電鑷夾、光電濕潤與 PEGDA 微流道——在有機光導晶片上以投影光操控細胞、微粒、氣泡與液滴。")}</p>
<div class="figures" style="margin-top:0">
  <div><b>{len(papers["journal"])}</b><span>{bi("journal articles", "期刊論文")}</span></div>
  <div><b>{len(papers["conference"])}</b><span>{bi("conference papers", "研討會論文")}</span></div>
  <div><b>{s["first_author"]}</b><span>{bi("first-author", "第一作者")}</span></div>
  <div><b>{s["citations"]}</b><span>{bi("citations (Crossref)", "引用次數（Crossref）")}</span></div>
</div>
<h2>{bi("Journal articles", "期刊論文")}</h2>
<div>{"".join(paper_row(p) for p in papers["journal"])}</div>
<h2>{bi("Conference papers", "研討會論文")}</h2>
<div>{"".join(paper_row(p) for p in papers["conference"])}</div>
"""


def page_somnics():
    g = patents["somnics"]
    fams = g["families"]
    n_pub = sum(len(f["pubs"]) for f in fams)
    return f"""
<p class="eyebrow">2011 – {bi("present", "至今")} · {bi(g["assignee_en"], g["assignee_zh"])}</p>
<h1>{bi("Inventions at Somnics", "Somnics 時期發明")}</h1>
<div class="note" style="margin-top:16px">{bi(
    "Public record only. This page lists granted and published patents on which Tung-Ming Yu is a named inventor, "
    "exactly as published by the patent offices — number, title, dates and assignee. It is not a company portfolio and carries no unpublished information.",
    "僅限公開紀錄。本頁列出余東銘為掛名發明人之已核准／已公開專利，內容與各國專利局公開資料一致——號碼、名稱、日期與專利權人。本頁不是公司專利組合，亦不含任何未公開資訊。")}</div>
<p class="lede">{bi(f"{len(fams)} patent families · {n_pub} granted or published items · oral negative-pressure therapy for obstructive sleep apnea.",
                     f"{len(fams)} 個專利家族 · {n_pub} 件核准／公開案 · 阻塞型睡眠呼吸中止之口腔負壓治療。")}</p>
<div class="families">{"".join(family_card(f, "somnics", False) for f in fams)}</div>
"""


PAGES = {
    "index.html": ("Tung-Ming Yu", "Inventor portfolio of Tung-Ming Yu — patents and publications", page_home),
    "itri.html": ("ITRI Patents", "Patent families from ITRI, 2003–2010", page_itri),
    "publications.html": ("Publications", "Journal and conference papers, 2010–2013", page_publications),
    "somnics.html": ("Somnics Inventions", "Publicly recorded patents as a named inventor at Somnics", page_somnics),
}


def render(fname, artifact):
    title, desc, fn = PAGES[fname]
    body = f'<div class="wrap">{header(fname)}<main>{fn()}</main>{footer(fname)}</div>'
    if artifact:
        return (f"<title>{esc(title)}</title>\n{FONTS}\n<style>{CSS}</style>\n{body}\n<script>{JS}</script>\n")
    full_title = f"{title} — Inventor portfolio" if fname == "index.html" else f"{title} — {site['name_en']}"
    base = site.get("base_url", "")
    og_extra = ""
    if base:
        page_url = base if fname == "index.html" else base + fname
        og_extra = (f'<link rel="canonical" href="{esc(page_url)}">\n<meta property="og:url" content="{esc(page_url)}">\n')
        if (ROOT / "assets" / "og.png").exists():
            og_extra += (f'<meta property="og:image" content="{esc(base)}assets/og.png">\n'
                         '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
                         '<meta name="twitter:card" content="summary_large_image">\n')
    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
{og_extra}{FONTS}
<link rel="stylesheet" href="style.css">
</head>
<body>
{body}
<script src="app.js"></script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", action="store_true", help="inline CSS/JS, omit document wrapper")
    ap.add_argument("--out", default=None, help="output directory (default: next to build.py)")
    a = ap.parse_args()
    out = pathlib.Path(a.out) if a.out else ROOT
    out.mkdir(parents=True, exist_ok=True)
    for fname in PAGES:
        (out / fname).write_text(render(fname, a.artifact), "utf-8")
    if not a.artifact:
        (out / "style.css").write_text(CSS.strip() + "\n", "utf-8")
        (out / "app.js").write_text(JS.strip() + "\n", "utf-8")
    print(f"built {len(PAGES)} pages -> {out}  | families={STATS['families']} items={STATS['pubs']} "
          f"jurisdictions={STATS['juris']} papers={STATS['papers']} citations={STATS['citations']}")


if __name__ == "__main__":
    main()
