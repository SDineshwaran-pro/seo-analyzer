import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from collections import Counter
import textstat
import json
from datetime import datetime

st.set_page_config(
    page_title="SEO Analyser",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Layout fix ── */
.block-container { padding: 12px 12px 40px !important; max-width: 100% !important; }
section[data-testid="stMain"] > div { padding: 0 !important; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg,#1a1f2e,#0f3460);
  border: 1px solid #2d3748; border-radius: 14px;
  padding: 24px 16px; margin-bottom: 18px; text-align: center;
}
.hero h1 { color: #e2e8f0; font-size: clamp(1.2rem,4vw,2rem); font-weight:700; margin:0 0 6px; }
.hero p  { color: #94a3b8; font-size: clamp(.78rem,2.5vw,.95rem); margin:0; word-break:break-all; }
.hero .brand { color: #38bdf8; font-weight:700; }

/* ── Input row ── */
.input-row {
  display: flex; flex-wrap: wrap; gap: 10px;
  background: #1e2533; border:1px solid #2d3748;
  border-radius:14px; padding:16px; margin-bottom:18px;
  align-items: flex-end;
}
.input-row > div { flex: 1 1 200px; min-width: 0; }

/* ── Score grid ── */
.score-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px; margin-bottom: 18px;
}
.score-card {
  background:#1e2533; border:1px solid #2d3748;
  border-radius:12px; padding:14px 8px; text-align:center;
}
.score-num  { font-size: clamp(1.6rem,5vw,2.4rem); font-weight:700; line-height:1; }
.score-lbl  { color:#94a3b8; font-size:.72rem; margin-top:5px; font-weight:600;
              text-transform:uppercase; letter-spacing:.4px; }
.c-green  { color:#22c55e; }
.c-lime   { color:#84cc16; }
.c-amber  { color:#f59e0b; }
.c-red    { color:#ef4444; }

/* ── Section card ── */
.scard {
  background:#1e2533; border:1px solid #2d3748;
  border-radius:12px; padding:16px; margin-bottom:16px;
}
.stitle { color:#e2e8f0; font-size:.95rem; font-weight:600;
          margin-bottom:12px; display:flex; align-items:center; gap:6px; }

/* ── Metric row ── */
.mrow {
  display:flex; justify-content:space-between; align-items:flex-start;
  padding:8px 0; border-bottom:1px solid #232b3a; gap:8px; flex-wrap:wrap;
}
.mrow:last-child { border-bottom:none; }
.mname { color:#94a3b8; font-size:.82rem; flex-shrink:0; min-width:120px; }
.mval  { color:#e2e8f0; font-size:.82rem; font-weight:500;
         text-align:right; word-break:break-word; flex:1; }

/* ── Check items ── */
.chk { display:flex; gap:9px; padding:8px 0; border-bottom:1px solid #232b3a; align-items:flex-start; }
.chk:last-child { border-bottom:none; }
.dot { width:11px; height:11px; border-radius:50%; flex-shrink:0; margin-top:3px; }
.dg{background:#22c55e} .dy{background:#f59e0b} .dr{background:#ef4444}
.chktxt { color:#cbd5e1; font-size:.82rem; line-height:1.5; }

/* ── Insight boxes ── */
.ibox { border-left:3px solid; padding:9px 12px; border-radius:0 8px 8px 0; margin-bottom:8px; font-size:.82rem; }
.i-ok  { border-color:#22c55e; background:#0f2d1f; color:#86efac; }
.i-warn{ border-color:#f59e0b; background:#2d1f0f; color:#fcd34d; }
.i-err { border-color:#ef4444; background:#2d0f0f; color:#fca5a5; }
.i-inf { border-color:#3b82f6; background:#0f1f2d; color:#93c5fd; }

/* ── Headings ── */
.htag { display:inline-block; padding:2px 7px; border-radius:4px; font-size:.72rem;
        font-weight:700; margin-right:6px; min-width:28px; text-align:center; }
.h1t{background:#450a0a;color:#fca5a5} .h2t{background:#1e3a5f;color:#93c5fd}
.h3t{background:#14532d;color:#86efac} .h4t{background:#2d1f0f;color:#fcd34d}
.h5t{background:#1e1e40;color:#c4b5fd} .h6t{background:#2d2d2d;color:#9ca3af}
.hrow { display:flex; align-items:flex-start; padding:7px 0; border-bottom:1px solid #232b3a; gap:6px; }
.hrow:last-child{border-bottom:none}
.htxt { color:#cbd5e1; font-size:.82rem; flex:1; word-break:break-word; }

/* ── Links ── */
.lpill { background:#1a2235; border:1px solid #2d3748; border-radius:7px;
         padding:7px 10px; margin-bottom:7px; font-size:.76rem; word-break:break-all; }
.lanc  { color:#a78bfa; display:block; margin-bottom:2px; }
.lhref { color:#60a5fa; }

/* ── Tag chips ── */
.chip { display:inline-block; background:#1e3a5f; color:#93c5fd;
        border-radius:5px; padding:2px 9px; font-size:.74rem; margin:2px; font-weight:500; }

/* ── KW bars ── */
.kwrow { display:flex; align-items:center; gap:10px; padding:7px 0; border-bottom:1px solid #232b3a; }
.kwrow:last-child{border-bottom:none}
.kww  { color:#e2e8f0; font-size:.82rem; min-width:110px; font-weight:500; word-break:break-word; }
.kwc  { color:#94a3b8; font-size:.78rem; min-width:36px; text-align:right; }
.kwbw { flex:1; background:#2d3748; border-radius:100px; height:5px; min-width:30px; }
.kwbf { height:5px; border-radius:100px; background:linear-gradient(90deg,#3b82f6,#818cf8); }

/* ── Scroll areas ── */
.scrl { max-height:300px; overflow-y:auto; padding-right:4px; }

/* ── Progress bar ── */
.pgwrap { background:#2d3748; border-radius:100px; height:7px; margin-top:5px; overflow:hidden; }
.pgfill { height:7px; border-radius:100px; }

/* ── Analyse button ── */
div[data-testid="stButton"] > button {
  background: linear-gradient(135deg,#2563eb,#7c3aed) !important;
  color: #fff !important; border: none !important;
  border-radius: 10px !important; font-size:.95rem !important;
  font-weight:600 !important; width:100% !important;
  padding: 12px 0 !important; transition: opacity .2s;
}
div[data-testid="stButton"] > button:hover { opacity:.85; }

/* ── Inputs ── */
div[data-testid="stTextInput"] input {
  background:#161b27 !important; border:1px solid #3b4563 !important;
  color:#e2e8f0 !important; border-radius:9px !important;
  font-size:.9rem !important;
}
div[data-testid="stTextInput"] label { color:#94a3b8 !important; font-size:.82rem !important; }

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility:hidden; }

/* ── Mobile tweaks ── */
@media (max-width: 640px) {
  .block-container { padding: 8px 8px 40px !important; }
  .hero { padding: 18px 12px; }
  .score-grid { grid-template-columns: repeat(4,1fr); gap:8px; }
  .score-card { padding: 10px 4px; }
  .mname { min-width: 100px; font-size:.78rem; }
  .mval  { font-size:.78rem; }
  .input-row { padding:12px; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
    "Cache-Control": "no-cache",
}

STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "shall","can","this","that","these","those","it","its","we","our","you",
    "your","he","she","they","their","i","my","me","us","as","so","if","not",
    "no","all","also","about","more","than","then","when","where","which",
    "who","what","how","any","each","both","few","very","just","up","out",
    "into","through","during","before","after","above","below","between",
    "there","here","now","get","got","go","make","made","new","one","two",
    "three","four","five","first","last","page","click","read","view","find",
}

def fetch_page(url):
    try:
        t0 = time.time()
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        elapsed = round((time.time() - t0) * 1000)
        soup = BeautifulSoup(r.text, "lxml")
        return soup, r, elapsed, None
    except Exception as e:
        return None, None, 0, str(e)

def clean_text(soup):
    s = BeautifulSoup(str(soup), "lxml")
    for tag in s(["script","style","noscript","header","footer","nav","aside"]):
        tag.decompose()
    return re.sub(r"\s+", " ", s.get_text(separator=" ")).strip()

def word_freq(text, top=20):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    return Counter(filtered).most_common(top)

def sc(score):
    if score >= 80: return "c-green"
    if score >= 60: return "c-lime"
    if score >= 40: return "c-amber"
    return "c-red"

def slug_analysis(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    slug = path.split("/")[-1] if path else ""
    issues, score = [], 100
    if not slug:
        slug = "(homepage)"
    else:
        if len(slug) > 75:                        issues.append("Slug too long (>75 chars)"); score -= 20
        if re.search(r'[A-Z]', slug):             issues.append("Contains uppercase letters"); score -= 15
        if re.search(r'_', slug):                 issues.append("Use hyphens not underscores"); score -= 10
        if re.search(r'\d{5,}', slug):            issues.append("Contains numeric IDs"); score -= 10
        if re.search(r'[^a-z0-9\-/.]', slug):    issues.append("Contains special characters"); score -= 15
    return slug, max(0, score), issues

def check_robots(base):
    try:
        r = requests.get(f"{base}/robots.txt", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return True, r.text[:600]
    except: pass
    return False, ""

def check_sitemap(base):
    for p in ["/sitemap.xml","/sitemap_index.xml","/sitemap/sitemap.xml"]:
        try:
            r = requests.get(f"{base}{p}", headers=HEADERS, timeout=8)
            if r.status_code == 200:
                return True, f"{base}{p}"
        except: pass
    return False, ""

def analyse_images(soup):
    imgs = soup.find_all("img")
    missing = [i for i in imgs if not i.get("alt","").strip()]
    lazy    = sum(1 for i in imgs if i.get("loading")=="lazy")
    old_fmt = sum(1 for i in imgs if i.get("src","") and
                  not any(x in i.get("src","").lower() for x in [".webp",".avif",".svg"]))
    return {"total":len(imgs),"missing_alt":len(missing),"lazy":lazy,"old_fmt":old_fmt,
            "miss_srcs":[i.get("src","")[:70] for i in missing[:4]]}

def analyse_social(soup):
    og, tw = {}, {}
    for m in soup.find_all("meta"):
        prop = m.get("property","") or m.get("name","")
        c    = m.get("content","")
        if prop.startswith("og:"):      og[prop] = c
        if prop.startswith("twitter:"): tw[prop] = c
    return og, tw

def analyse_schema(soup):
    types = []
    for s in soup.find_all("script", {"type":"application/ld+json"}):
        try:
            d = json.loads(s.string or "")
            t = d.get("@type") or (d.get("@graph",[{}])[0].get("@type") if "@graph" in d else "Unknown")
            if isinstance(t, list): types.extend(t)
            else: types.append(str(t))
        except: pass
    return types

# ─────────────────────────────────────────────
def full_analyse(url, focus_kw):
    with st.spinner("⏳ Fetching & analysing page…"):
        soup, resp, load_ms, err = fetch_page(url)

    if err or soup is None:
        st.error(f"❌ Could not fetch: {err}")
        return

    parsed   = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    focus_kw = focus_kw.strip().lower()

    page_text  = clean_text(soup)
    word_list  = re.findall(r'\b[a-zA-Z]{2,}\b', page_text.lower())
    word_count = len(word_list)

    # ── Meta extraction ──────────────────────────────────────────────────
    title_tag = soup.find("title")
    title_txt = title_tag.get_text(strip=True) if title_tag else ""
    meta_desc = meta_kw = canonical = robots_meta = lang = viewport = charset = ""

    for m in soup.find_all("meta"):
        n = (m.get("name") or "").lower()
        p = (m.get("property") or "").lower()
        c = m.get("content","")
        if n=="description":  meta_desc   = c
        if n=="keywords":     meta_kw     = c
        if n=="robots":       robots_meta = c
        if n=="viewport":     viewport    = c
        if m.get("charset"):  charset     = m["charset"]
    html_tag = soup.find("html")
    if html_tag: lang = html_tag.get("lang","")
    lc = soup.find("link",{"rel":"canonical"})
    if lc: canonical = lc.get("href","")

    # ── Headings ─────────────────────────────────────────────────────────
    headings = {}
    all_h = []
    for lv in range(1,7):
        tags = soup.find_all(f"h{lv}")
        headings[f"h{lv}"] = [t.get_text(strip=True) for t in tags]
        for t in tags: all_h.append((f"h{lv}", t.get_text(strip=True)))

    paras = soup.find_all("p")

    # ── Links ─────────────────────────────────────────────────────────────
    int_links, ext_links, nf = [], [], 0
    for a in soup.find_all("a", href=True):
        href   = a["href"].strip()
        anchor = a.get_text(strip=True)[:70]
        rel    = a.get("rel",[])
        if "nofollow" in rel: nf += 1
        if href.startswith("http") and parsed.netloc not in href:
            ext_links.append((href, anchor))
        elif href and not href.startswith(("javascript","mailto","#","tel")):
            int_links.append((urllib.parse.urljoin(url, href), anchor))

    img_data     = analyse_images(soup)
    scripts      = soup.find_all("script", src=True)
    stylesheets  = soup.find_all("link",{"rel":"stylesheet"})
    og, tw       = analyse_social(soup)
    schemas      = analyse_schema(soup)
    all_meta     = [(m.get("name") or m.get("property") or m.get("http-equiv",""),
                     m.get("content","")[:110])
                    for m in soup.find_all("meta")
                    if m.get("name") or m.get("property") or m.get("http-equiv")]

    slug, slug_sc, slug_iss = slug_analysis(url)
    has_robots, robots_txt  = check_robots(base_url)
    has_sitemap, sitemap_u  = check_sitemap(base_url)
    kw_freq = word_freq(page_text, 20)

    try:
        flesch = round(textstat.flesch_reading_ease(page_text))
        grade  = textstat.text_standard(page_text, float_output=False)
    except:
        flesch, grade = 0, "N/A"

    # ── Scores ────────────────────────────────────────────────────────────
    def title_score():
        s=0
        if title_txt:
            s+=30
            l=len(title_txt)
            s+=(30 if 50<=l<=60 else 15 if 40<=l<=70 else 0)
            if focus_kw and focus_kw in title_txt.lower(): s+=20
            if any(c in title_txt for c in ["|","-","–"]): s+=10
            if title_txt[0].isupper(): s+=10
        return min(100,s)

    def meta_score():
        s=0
        if meta_desc:
            s+=30; l=len(meta_desc)
            s+=(35 if 130<=l<=160 else 20 if 100<=l<=180 else 0)
            if focus_kw and focus_kw in meta_desc.lower(): s+=20
            if any(c in meta_desc for c in ["!","?",".",","]): s+=15
        return min(100,s)

    def content_score():
        s=0
        if word_count>=300:  s+=20
        if word_count>=600:  s+=15
        if word_count>=1000: s+=15
        if headings.get("h1"): s+=15
        if len(headings.get("h2",[]))>=2: s+=10
        if len(headings.get("h3",[]))>=2: s+=5
        if len(paras)>=5: s+=10
        if focus_kw:
            d=page_text.lower().count(focus_kw)/max(word_count,1)*100
            if .5<=d<=2.5: s+=10
        return min(100,s)

    def tech_score():
        s=0
        if url.startswith("https"): s+=20
        if canonical: s+=10
        if lang:      s+=10
        if viewport:  s+=10
        if charset:   s+=5
        if has_robots: s+=10
        if has_sitemap: s+=15
        if "noindex" not in robots_meta.lower(): s+=10
        if img_data["missing_alt"]==0: s+=10
        return min(100,s)

    def speed_score():
        s=(95 if load_ms<500 else 80 if load_ms<1000 else 65 if load_ms<2000
           else 45 if load_ms<3000 else 25 if load_ms<5000 else 10)
        if img_data["lazy"]>0: s=min(100,s+5)
        if len(scripts)<10: s=min(100,s+5)
        return s

    def kw_score():
        if not focus_kw: return 50
        s=0
        if focus_kw in title_txt.lower(): s+=25
        if focus_kw in meta_desc.lower(): s+=20
        if any(focus_kw in h.lower() for h in headings.get("h1",[])): s+=20
        if focus_kw in page_text.lower(): s+=15
        if focus_kw.replace(" ","-") in url.lower(): s+=10
        d=page_text.lower().count(focus_kw)/max(word_count,1)*100
        if .5<=d<=2.5: s+=10
        return min(100,s)

    def social_score():
        s=0
        if og.get("og:title"):       s+=20
        if og.get("og:description"): s+=20
        if og.get("og:image"):       s+=20
        if tw.get("twitter:card"):   s+=20
        if tw.get("twitter:title"):  s+=10
        if tw.get("twitter:image"):  s+=10
        return min(100,s)

    SC = {
        "overall": 0,
        "title": title_score(), "meta": meta_score(),
        "content": content_score(), "tech": tech_score(),
        "speed": speed_score(), "kw": kw_score(), "social": social_score(),
    }
    SC["overall"] = round(
        SC["title"]*.16 + SC["meta"]*.12 + SC["content"]*.22 +
        SC["tech"]*.20 + SC["speed"]*.15 + SC["kw"]*.08 + SC["social"]*.07
    )

    # ── Yoast checks ─────────────────────────────────────────────────────
    def yoast():
        C=[]
        def a(s,t): C.append((s,t))
        if not title_txt:       a("r","Page title is missing")
        elif len(title_txt)<30: a("y",f"Title short ({len(title_txt)} chars) — aim 50–60")
        elif len(title_txt)>70: a("y",f"Title too long ({len(title_txt)} chars) — aim 50–60")
        else:                   a("g",f"Title length good ({len(title_txt)} chars)")
        if focus_kw:
            a("g","Focus keyword in title") if focus_kw in title_txt.lower() else a("r","Focus keyword NOT in title")
        if not meta_desc:           a("r","Meta description missing")
        elif len(meta_desc)<100:    a("y",f"Meta description short ({len(meta_desc)} chars)")
        elif len(meta_desc)>165:    a("y",f"Meta description long ({len(meta_desc)} chars)")
        else:                       a("g",f"Meta description good ({len(meta_desc)} chars)")
        if focus_kw and meta_desc:
            a("g","Keyword in meta description") if focus_kw in meta_desc.lower() else a("y","Keyword not in meta description")
        h1s=headings.get("h1",[])
        if not h1s:        a("r","No H1 heading found")
        elif len(h1s)>1:   a("y",f"Multiple H1 tags ({len(h1s)}) — use only one")
        else:              a("g","Exactly one H1 tag ✓")
        if focus_kw and h1s:
            a("g","Keyword in H1") if any(focus_kw in h.lower() for h in h1s) else a("y","Keyword not in H1")
        if word_count<300:   a("r",f"Thin content ({word_count} words) — aim 600+")
        elif word_count<600: a("y",f"Content could be longer ({word_count} words)")
        else:                a("g",f"Good content length ({word_count} words)")
        if focus_kw:
            cnt=page_text.lower().count(focus_kw); d=cnt/max(word_count,1)*100
            if d<.5:   a("y",f"Keyword density low ({d:.2f}%) — aim 0.5–2.5%")
            elif d>3:  a("r",f"Keyword density high ({d:.2f}%) — possible stuffing")
            else:      a("g",f"Keyword density good ({d:.2f}%)")
        a("g","HTTPS secure") if url.startswith("https") else a("r","Not using HTTPS")
        a("g","Canonical URL set") if canonical else a("y","No canonical URL")
        if img_data["missing_alt"]==0:   a("g","All images have alt text")
        elif img_data["missing_alt"]<3:  a("y",f"{img_data['missing_alt']} image(s) missing alt")
        else:                            a("r",f"{img_data['missing_alt']} images missing alt")
        a("r","noindex found — page won't be indexed!") if "noindex" in robots_meta.lower() else a("g","Page is indexable")
        a("g","Sitemap found") if has_sitemap else a("y","No sitemap.xml detected")
        a("g","robots.txt accessible") if has_robots else a("y","robots.txt not found")
        if len(int_links)>=3:  a("g",f"{len(int_links)} internal links")
        elif len(int_links)>0: a("y",f"Only {len(int_links)} internal links — add more")
        else:                  a("r","No internal links found")
        a("g",f"Structured data: {', '.join(schemas)}") if schemas else a("y","No Schema.org/JSON-LD found")
        a("g","Open Graph tags present") if og.get("og:title") else a("y","Open Graph tags missing")
        a("g",f"HTML lang='{lang}'") if lang else a("y","HTML lang attribute missing")
        a("g","Viewport meta present") if viewport else a("r","Viewport meta missing — not mobile-friendly")
        if load_ms<1000:   a("g",f"Fast load: {load_ms}ms")
        elif load_ms<3000: a("y",f"Moderate load: {load_ms}ms")
        else:              a("r",f"Slow load: {load_ms}ms")
        if len(headings.get("h2",[]))>=2: a("g",f"{len(headings['h2'])} H2 subheadings")
        else:                              a("y",f"Only {len(headings.get('h2',[]))} H2 — add subheadings")
        return C

    checks = yoast()

    # ════════════════════════════════════════════
    #  R E N D E R
    # ════════════════════════════════════════════

    st.markdown(f"""
    <div class="hero">
      <h1>🔍 SEO Analysis Report</h1>
      <p><span class="brand">{url}</span><br>
      <span style="color:#475569;font-size:.78rem">Analysed {datetime.now().strftime('%d %b %Y, %H:%M')}</span></p>
    </div>""", unsafe_allow_html=True)

    # Score cards
    labels = [("Overall",SC["overall"]),("Content",SC["content"]),("Technical",SC["tech"]),
              ("Title",SC["title"]),("Meta",SC["meta"]),("Speed",SC["speed"]),("Social",SC["social"])]
    cols = st.columns(7)
    for col,(lbl,val) in zip(cols,labels):
        col.markdown(f'<div class="score-card"><div class="score-num {sc(val)}">{val}</div><div class="score-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs for mobile-friendly navigation ──────────────────────────────
    tabs = st.tabs(["📋 Overview","✅ Checklist","🎯 Keywords","🔗 Links","🏗️ Structure","📣 Social","⚡ Speed","🏷️ Tags"])

    # ── TAB 0: Overview ──────────────────────────────────────────────────
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stitle">📋 Basic SEO</div>', unsafe_allow_html=True)
            rows = [
                ("Title", (title_txt[:60]+"…" if len(title_txt)>60 else title_txt) or "❌ Missing"),
                ("Title Length", f'{len(title_txt)} chars {"✅" if 50<=len(title_txt)<=60 else "⚠️"}'),
                ("Meta Desc", (meta_desc[:80]+"…" if len(meta_desc)>80 else meta_desc) or "❌ Missing"),
                ("Meta Length", f'{len(meta_desc)} chars {"✅" if 130<=len(meta_desc)<=160 else "⚠️"}'),
                ("Canonical", canonical[:50] or "❌ Not set"),
                ("Robots Meta", robots_meta or "index,follow"),
                ("HTML Lang", lang or "❌ Not set"),
                ("Viewport", "✅ Yes" if viewport else "❌ Missing"),
                ("Charset", charset or "Not detected"),
                ("HTTP Status", f'{resp.status_code} {"✅" if resp.status_code==200 else "⚠️"}' if resp else "N/A"),
                ("HTTPS", "✅ Secure" if url.startswith("https") else "❌ No"),
                ("Load Time", f'{load_ms}ms {"🟢" if load_ms<1000 else "🟡" if load_ms<3000 else "🔴"}'),
            ]
            for n,v in rows:
                st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="scard"><div class="stitle">📝 Content Stats</div>', unsafe_allow_html=True)
            for n,v in [
                ("Word Count",str(word_count)),("Paragraphs",str(len(paras))),
                ("H1",str(len(headings.get("h1",[])))),("H2",str(len(headings.get("h2",[])))),
                ("H3",str(len(headings.get("h3",[])))),("H4",str(len(headings.get("h4",[])))),
                ("H5+H6",str(len(headings.get("h5",[]))+len(headings.get("h6",[])))),
                ("Images",str(img_data["total"])),("Missing Alt",f'{img_data["missing_alt"]} {"✅" if img_data["missing_alt"]==0 else "❌"}'),
                ("Lazy Images",str(img_data["lazy"])),
                ("Int Links",str(len(int_links))),("Ext Links",str(len(ext_links))),
                ("JS Files",str(len(scripts))),("CSS Files",str(len(stylesheets))),
                ("Flesch Score",str(flesch)),("Grade Level",grade),
                ("Schema Types",", ".join(schemas) if schemas else "None"),
            ]:
                st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # URL Slug
        st.markdown('<div class="scard"><div class="stitle">🔗 URL & Slug Efficiency</div>', unsafe_allow_html=True)
        depth = len([p for p in parsed.path.split('/') if p])
        for n,v in [
            ("Full URL", url[:80]),("Slug", slug),
            ("Slug Score", f'{slug_sc}/100'),("Path Depth", f'{depth} levels'),
            ("Query Params", "✅ None" if not parsed.query else f"⚠️ {parsed.query[:50]}"),
        ]:
            st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
        for iss in slug_iss:
            st.markdown(f'<div class="ibox i-warn">⚠️ {iss}</div>', unsafe_allow_html=True)
        if not slug_iss:
            st.markdown('<div class="ibox i-ok">✅ Slug is clean & SEO-friendly</div>', unsafe_allow_html=True)
        pct = slug_sc
        st.markdown(f'<div class="pgwrap"><div class="pgfill" style="width:{pct}%;background:#3b82f6"></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Recommendations
        st.markdown('<div class="scard"><div class="stitle">💡 Priority Recommendations</div>', unsafe_allow_html=True)
        recs=[]
        if not title_txt:             recs.append(("err","Add a page title immediately"))
        elif len(title_txt)>70:       recs.append(("warn",f"Shorten title to <60 chars (currently {len(title_txt)})"))
        if not meta_desc:             recs.append(("err","Add meta description (130–160 chars) to improve CTR"))
        if not canonical:             recs.append(("warn","Set canonical URL to prevent duplicate content"))
        if img_data["missing_alt"]>0: recs.append(("warn",f"Add alt text to {img_data['missing_alt']} image(s)"))
        if not has_sitemap:           recs.append(("warn","Create sitemap.xml & submit to Google Search Console"))
        if not schemas:               recs.append(("inf","Add JSON-LD structured data (JobPosting, Organization…)"))
        if not og.get("og:image"):    recs.append(("warn","Add og:image for social sharing"))
        if word_count<600:            recs.append(("err",f"Increase content ({word_count} words → aim 600+)"))
        if load_ms>3000:              recs.append(("err",f"Improve page speed ({load_ms}ms → aim <1s)"))
        if len(int_links)<3:          recs.append(("warn","Add more internal links"))
        if not recs:                  recs.append(("ok","🎉 No major SEO issues found!"))
        cls_map={"err":"i-err","warn":"i-warn","inf":"i-inf","ok":"i-ok"}
        ico_map={"err":"❌","warn":"⚠️","inf":"ℹ️","ok":"✅"}
        for k,msg in recs:
            st.markdown(f'<div class="ibox {cls_map[k]}">{ico_map[k]} {msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 1: Checklist ────────────────────────────────────────────────
    with tabs[1]:
        gn=sum(1 for s,_ in checks if s=="g")
        yn=sum(1 for s,_ in checks if s=="y")
        rn=sum(1 for s,_ in checks if s=="r")
        st.markdown(f"""
        <div class="scard">
          <div class="stitle">✅ SEO Checklist ({len(checks)} checks)</div>
          <div style="display:flex;gap:18px;margin-bottom:14px;flex-wrap:wrap">
            <span style="color:#22c55e;font-weight:600;font-size:.85rem">✅ {gn} passed</span>
            <span style="color:#f59e0b;font-weight:600;font-size:.85rem">⚠️ {yn} warnings</span>
            <span style="color:#ef4444;font-weight:600;font-size:.85rem">❌ {rn} issues</span>
          </div>""", unsafe_allow_html=True)
        for s,t in checks:
            dc = {"g":"dg","y":"dy","r":"dr"}[s]
            st.markdown(f'<div class="chk"><div class="dot {dc}"></div><div class="chktxt">{t}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 2: Keywords ──────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="scard"><div class="stitle">🎯 Focus Keyword Analysis</div>', unsafe_allow_html=True)
        if focus_kw:
            cnt=page_text.lower().count(focus_kw)
            d=cnt/max(word_count,1)*100
            for n,v in [
                ("Focus Keyword",f'<span style="color:#38bdf8;font-weight:600">{focus_kw}</span>'),
                ("Occurrences",str(cnt)),
                ("Density",f'{d:.2f}% {"✅" if .5<=d<=2.5 else "⚠️"}'),
                ("In Title","✅ Yes" if focus_kw in title_txt.lower() else "❌ No"),
                ("In Meta Desc","✅ Yes" if focus_kw in meta_desc.lower() else "❌ No"),
                ("In H1","✅ Yes" if any(focus_kw in h.lower() for h in headings.get("h1",[])) else "❌ No"),
                ("In URL","✅ Yes" if focus_kw.replace(" ","-") in url.lower() else "❌ No"),
                ("Keyword Score",f'<span class="{sc(SC["kw"])}" style="font-weight:700">{SC["kw"]}/100</span>'),
            ]:
                st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ibox i-inf">ℹ️ Enter a focus keyword above for detailed keyword analysis</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="scard"><div class="stitle">📊 Top Keywords Found</div>', unsafe_allow_html=True)
        mx = kw_freq[0][1] if kw_freq else 1
        for word,cnt in kw_freq:
            pct=round(cnt/mx*100)
            st.markdown(f'<div class="kwrow"><span class="kww">{word}</span><span class="kwc">{cnt}×</span><div class="kwbw"><div class="kwbf" style="width:{pct}%"></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3: Links ─────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown(f'<div class="scard"><div class="stitle">🔁 Internal Links ({len(int_links)})</div><div class="scrl">', unsafe_allow_html=True)
        for href,anc in int_links[:50]:
            st.markdown(f'<div class="lpill"><span class="lanc">⬡ {anc or "(no anchor)"}</span><span class="lhref">{href[:85]}</span></div>', unsafe_allow_html=True)
        if not int_links:
            st.markdown('<div class="ibox i-err">No internal links found</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="scard"><div class="stitle">🌐 External Links ({len(ext_links)})</div><div class="scrl">', unsafe_allow_html=True)
        for href,anc in ext_links[:50]:
            st.markdown(f'<div class="lpill"><span class="lanc">↗ {anc or "(no anchor)"}</span><span class="lhref">{href[:85]}</span></div>', unsafe_allow_html=True)
        if not ext_links:
            st.markdown('<div class="ibox i-inf">No external links found</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ── TAB 4: Structure ─────────────────────────────────────────────────
    with tabs[4]:
        cols6 = st.columns(6)
        css_c = ["h1t","h2t","h3t","h4t","h5t","h6t"]
        for i,lv in enumerate(range(1,7)):
            cols6[i].markdown(f'<div style="text-align:center"><span class="htag {css_c[i]}">H{lv}</span><div style="color:#e2e8f0;font-size:1.5rem;font-weight:700;margin-top:4px">{len(headings.get(f"h{lv}",[]))}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="scard" style="margin-top:14px"><div class="stitle">Heading Tree</div><div class="scrl">', unsafe_allow_html=True)
        for tag,txt in all_h:
            lv=tag[1]
            st.markdown(f'<div class="hrow"><span class="htag {css_c[int(lv)-1]}">{tag.upper()}</span><span class="htxt">{txt[:110]}</span></div>', unsafe_allow_html=True)
        if not all_h:
            st.markdown('<div class="ibox i-err">No headings found on page</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # Robots & Schema
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stitle">🤖 Robots & Sitemap</div>', unsafe_allow_html=True)
            for n,v in [
                ("robots.txt","✅ Found" if has_robots else "❌ Not found"),
                ("Sitemap","✅ "+sitemap_u if has_sitemap else "❌ Not found"),
            ]:
                st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
            if has_robots and robots_txt:
                st.markdown(f'<div style="background:#131924;border-radius:7px;padding:10px;margin-top:8px;font-size:.73rem;color:#94a3b8;font-family:monospace;max-height:120px;overflow-y:auto">{robots_txt.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="scard"><div class="stitle">📐 Structured Data</div>', unsafe_allow_html=True)
            if schemas:
                for s in schemas:
                    st.markdown(f'<div class="ibox i-ok">✅ {s}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox i-warn">⚠️ No JSON-LD found. Add Organization, WebSite, or JobPosting schema.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 5: Social ────────────────────────────────────────────────────
    with tabs[5]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stitle">📘 Open Graph Tags</div>', unsafe_allow_html=True)
            if og:
                for k,v in og.items():
                    st.markdown(f'<div class="mrow"><span class="mname">{k}</span><span class="mval">{v[:70]}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox i-warn">⚠️ No Open Graph tags found</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="scard"><div class="stitle">🐦 Twitter / X Card Tags</div>', unsafe_allow_html=True)
            if tw:
                for k,v in tw.items():
                    st.markdown(f'<div class="mrow"><span class="mname">{k}</span><span class="mval">{v[:70]}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox i-warn">⚠️ No Twitter Card tags found</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="scard"><div class="stitle">📣 Social Score: <span class="{sc(SC["social"])}" style="font-weight:700">{SC["social"]}/100</span></div>', unsafe_allow_html=True)
        checks_soc = [
            ("og:title","og:title set",og.get("og:title")),
            ("og:description","og:description set",og.get("og:description")),
            ("og:image","og:image set",og.get("og:image")),
            ("og:url","og:url set",og.get("og:url")),
            ("twitter:card","twitter:card set",tw.get("twitter:card")),
            ("twitter:image","twitter:image set",tw.get("twitter:image")),
        ]
        for _,lbl,val in checks_soc:
            dc="dg" if val else "dr"
            st.markdown(f'<div class="chk"><div class="dot {dc}"></div><div class="chktxt">{lbl}: {"✅ " + str(val)[:50] if val else "❌ Missing"}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 6: Speed ─────────────────────────────────────────────────────
    with tabs[6]:
        size_kb = round(len(resp.content)/1024,1) if resp else 0
        st.markdown('<div class="scard"><div class="stitle">⚡ Page Speed Insights (Heuristic)</div>', unsafe_allow_html=True)
        for n,v in [
            ("Server Response",f'{load_ms}ms {"🟢" if load_ms<800 else "🟡" if load_ms<2500 else "🔴"}'),
            ("HTML Size",f'{size_kb} KB {"✅" if size_kb<100 else "⚠️ Large"}'),
            ("JS Files",f'{len(scripts)} {"✅" if len(scripts)<=8 else "⚠️"}'),
            ("CSS Files",f'{len(stylesheets)} {"✅" if len(stylesheets)<=4 else "⚠️"}'),
            ("Total Images",str(img_data["total"])),
            ("Lazy-Loaded",f'{img_data["lazy"]} {"✅" if img_data["lazy"]>0 else "⚠️ None"}'),
            ("Non-WebP/AVIF",f'{img_data["old_fmt"]} {"✅" if img_data["old_fmt"]==0 else "⚠️ Optimise"}'),
            ("Speed Score",f'{SC["speed"]}/100'),
        ]:
            st.markdown(f'<div class="mrow"><span class="mname">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)

        # Speed bar
        sp=SC["speed"]
        bar_col = "#22c55e" if sp>=80 else "#f59e0b" if sp>=50 else "#ef4444"
        st.markdown(f'<div style="margin-top:12px"><div style="color:#94a3b8;font-size:.78rem;margin-bottom:4px">Speed Score: {sp}/100</div><div class="pgwrap"><div class="pgfill" style="width:{sp}%;background:{bar_col}"></div></div></div>', unsafe_allow_html=True)

        if load_ms>3000:
            st.markdown('<div class="ibox i-err" style="margin-top:12px">❌ Very slow response. Check hosting, enable caching, use CDN.</div>', unsafe_allow_html=True)
        elif load_ms>1500:
            st.markdown('<div class="ibox i-warn" style="margin-top:12px">⚠️ Moderate speed. Consider optimising images and reducing JS.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ibox i-ok" style="margin-top:12px">✅ Good response time!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 7: Tags ──────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown(f'<div class="scard"><div class="stitle">🏷️ All Meta Tags ({len(all_meta)})</div>', unsafe_allow_html=True)
        chips="".join(f'<span class="chip">{n}</span>' for n,_ in all_meta)
        st.markdown(f'<div style="margin-bottom:14px">{chips}</div>', unsafe_allow_html=True)
        st.markdown('<div class="scrl">', unsafe_allow_html=True)
        for n,v in all_meta:
            st.markdown(f'<div class="mrow"><span class="mname" style="min-width:150px">{n}</span><span class="mval">{v}</span></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  MAIN UI
# ═══════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <h1>🔍 SEO Analyser</h1>
  <p>Full Yoast-style SEO audit · Free · No API keys</p>
</div>
""", unsafe_allow_html=True)

# Input row — always visible at top
st.markdown('<div class="input-row">', unsafe_allow_html=True)
col_url, col_kw, col_btn = st.columns([3, 2, 1])
with col_url:
    url_val = st.text_input("🌐 Page URL", value="https://hiring4jobs.com",
                            placeholder="https://example.com", label_visibility="visible")
with col_kw:
    kw_val  = st.text_input("🎯 Focus Keyword (optional)", value="",
                            placeholder="e.g. jobs in chennai", label_visibility="visible")
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run = st.button("🔍 Analyse Now", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if run:
    raw = url_val.strip()
    if not raw:
        st.warning("⚠️ Please enter a URL.")
    else:
        if not raw.startswith("http"):
            raw = "https://" + raw
        full_analyse(raw, kw_val)
elif not run:
    st.markdown("""
    <div style="text-align:center;padding:40px 16px">
      <div style="font-size:3rem;margin-bottom:12px">🔍</div>
      <div style="color:#94a3b8;font-size:1rem">Enter a URL above and click <b style="color:#38bdf8">Analyse Now</b></div>
      <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:24px">
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">📊 25+ SEO metrics</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">✅ Yoast-style checklist</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">🎯 Keyword analysis</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">⚡ Speed insights</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">🔗 Link audit</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:12px 18px;color:#94a3b8;font-size:.82rem">📣 Social tags</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
