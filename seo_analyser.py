import streamlit as st
import requests
import time
import re
import urllib.parse
import json
from collections import Counter
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

try:
    import textstat
    TEXTSTAT_OK = True
except ImportError:
    TEXTSTAT_OK = False

try:
    from curl_cffi import requests as cffi_requests
    CURL_OK = True
except ImportError:
    CURL_OK = False

try:
    import cloudscraper
    CLOUD_OK = True
except ImportError:
    CLOUD_OK = False

st.set_page_config(
    page_title="SEO Analyser – hiring4jobs.com",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.block-container { padding: 10px 10px 60px !important; max-width: 100% !important; }

.hero {
  background: linear-gradient(135deg,#1a1f2e,#0f3460);
  border: 1px solid #2d3748; border-radius: 14px;
  padding: 20px 16px; margin-bottom: 14px; text-align: center;
}
.hero h1 { color: #e2e8f0; font-size: clamp(1.1rem,4vw,1.8rem); font-weight:700; margin:0 0 4px; }
.hero p  { color: #94a3b8; font-size: clamp(.75rem,2.5vw,.9rem); margin:0; }
.brand   { color: #38bdf8; font-weight:700; }

.ibar {
  background: #1e2533; border:1px solid #2d3748; border-radius:12px;
  padding:14px; margin-bottom:14px;
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(7,1fr);
  gap: 8px; margin-bottom: 14px;
}
@media(max-width:700px){
  .score-grid { grid-template-columns: repeat(4,1fr); }
}
@media(max-width:400px){
  .score-grid { grid-template-columns: repeat(2,1fr); }
}
.sc {
  background:#1e2533; border:1px solid #2d3748; border-radius:10px;
  padding:12px 6px; text-align:center;
}
.scn { font-size:clamp(1.4rem,4vw,2rem); font-weight:700; line-height:1; }
.scl { color:#94a3b8; font-size:.68rem; margin-top:4px; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
.cg{color:#22c55e} .cl{color:#84cc16} .ca{color:#f59e0b} .cr{color:#ef4444}

.scard { background:#1e2533; border:1px solid #2d3748; border-radius:11px; padding:14px; margin-bottom:13px; }
.stit  { color:#e2e8f0; font-size:.9rem; font-weight:600; margin-bottom:10px; }

.mrow  { display:flex; justify-content:space-between; align-items:flex-start;
         padding:7px 0; border-bottom:1px solid #232b3a; gap:8px; flex-wrap:wrap; }
.mrow:last-child { border-bottom:none; }
.mn { color:#94a3b8; font-size:.79rem; min-width:110px; flex-shrink:0; }
.mv { color:#e2e8f0; font-size:.79rem; font-weight:500; text-align:right; word-break:break-word; flex:1; }

.chk { display:flex; gap:8px; padding:7px 0; border-bottom:1px solid #232b3a; align-items:flex-start; }
.chk:last-child { border-bottom:none; }
.dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; margin-top:3px; }
.dg{background:#22c55e} .dy{background:#f59e0b} .dr{background:#ef4444}
.ct { color:#cbd5e1; font-size:.79rem; line-height:1.5; }

.ibox { border-left:3px solid; padding:8px 11px; border-radius:0 7px 7px 0; margin-bottom:7px; font-size:.79rem; }
.iok {border-color:#22c55e;background:#0f2d1f;color:#86efac}
.iwn {border-color:#f59e0b;background:#2d1f0f;color:#fcd34d}
.ier {border-color:#ef4444;background:#2d0f0f;color:#fca5a5}
.inf {border-color:#3b82f6;background:#0f1f2d;color:#93c5fd}

.htag{display:inline-block;padding:2px 6px;border-radius:4px;font-size:.68rem;font-weight:700;margin-right:5px;min-width:26px;text-align:center}
.h1t{background:#450a0a;color:#fca5a5}.h2t{background:#1e3a5f;color:#93c5fd}
.h3t{background:#14532d;color:#86efac}.h4t{background:#2d1f0f;color:#fcd34d}
.h5t{background:#1e1e40;color:#c4b5fd}.h6t{background:#2d2d2d;color:#9ca3af}
.hrow{display:flex;align-items:flex-start;padding:6px 0;border-bottom:1px solid #232b3a;gap:5px}
.hrow:last-child{border-bottom:none}
.htxt{color:#cbd5e1;font-size:.79rem;flex:1;word-break:break-word}

.lpill{background:#1a2235;border:1px solid #2d3748;border-radius:6px;
       padding:6px 9px;margin-bottom:6px;font-size:.73rem;word-break:break-all}
.lanc{color:#a78bfa;display:block;margin-bottom:1px}
.lhref{color:#60a5fa}

.chip{display:inline-block;background:#1e3a5f;color:#93c5fd;
      border-radius:4px;padding:2px 8px;font-size:.71rem;margin:2px;font-weight:500}

.kwrow{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #232b3a}
.kwrow:last-child{border-bottom:none}
.kww{color:#e2e8f0;font-size:.79rem;min-width:100px;font-weight:500;word-break:break-word}
.kwc{color:#94a3b8;font-size:.75rem;min-width:30px;text-align:right}
.kwbw{flex:1;background:#2d3748;border-radius:100px;height:5px;min-width:20px}
.kwbf{height:5px;border-radius:100px;background:linear-gradient(90deg,#3b82f6,#818cf8)}

.scrl{max-height:280px;overflow-y:auto;padding-right:3px}
.pgwrap{background:#2d3748;border-radius:100px;height:6px;margin-top:4px;overflow:hidden}
.pgfill{height:6px;border-radius:100px}

.fetch-info{background:#131924;border:1px solid #2d3748;border-radius:8px;
            padding:10px 14px;margin-bottom:14px;font-size:.78rem;color:#64748b}
.fetch-info b{color:#94a3b8}

div[data-testid="stButton"]>button{
  background:linear-gradient(135deg,#2563eb,#7c3aed)!important;
  color:#fff!important;border:none!important;border-radius:9px!important;
  font-size:.9rem!important;font-weight:600!important;width:100%!important;
  padding:11px 0!important;
}
div[data-testid="stButton"]>button:hover{opacity:.85}
div[data-testid="stTextInput"] input{
  background:#161b27!important;border:1px solid #3b4563!important;
  color:#e2e8f0!important;border-radius:8px!important;font-size:.88rem!important;
}
div[data-testid="stTextInput"] label{color:#94a3b8!important;font-size:.79rem!important}
#MainMenu,footer,header{visibility:hidden}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with","by",
    "from","is","are","was","were","be","been","have","has","had","do","does",
    "did","will","would","could","should","this","that","these","those","it",
    "its","we","our","you","your","he","she","they","their","i","my","me","us",
    "as","so","if","not","no","all","also","about","more","than","then","when",
    "where","which","who","what","how","any","just","up","out","get","new","one",
    "page","click","read","view","find","job","jobs","apply","here","now","amp",
}

# ─────────────────────────────────────────────────────────────
def fetch_with_best_method(url):
    """
    Try multiple fetch strategies in order:
    1. curl_cffi  – spoofs Chrome TLS fingerprint, bypasses Cloudflare
    2. cloudscraper – dedicated Cloudflare bypass
    3. requests    – plain fallback
    Returns (html_text, status_code, load_ms, method_used, error)
    """
    errors = []

    # Strategy 1: curl_cffi (best Cloudflare bypass)
    if CURL_OK:
        try:
            t0 = time.time()
            r = cffi_requests.get(
                url,
                impersonate="chrome124",
                timeout=20,
                allow_redirects=True,
                headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Upgrade-Insecure-Requests": "1",
                }
            )
            ms = round((time.time()-t0)*1000)
            if r.status_code < 400:
                return r.text, r.status_code, ms, "curl_cffi (Chrome TLS)", None
            errors.append(f"curl_cffi: HTTP {r.status_code}")
        except Exception as e:
            errors.append(f"curl_cffi: {e}")

    # Strategy 2: cloudscraper
    if CLOUD_OK:
        try:
            t0 = time.time()
            sc = cloudscraper.create_scraper(
                browser={"browser":"chrome","platform":"windows","mobile":False},
                delay=3
            )
            r = sc.get(url, timeout=25, allow_redirects=True)
            ms = round((time.time()-t0)*1000)
            if r.status_code < 400:
                return r.text, r.status_code, ms, "cloudscraper", None
            errors.append(f"cloudscraper: HTTP {r.status_code}")
        except Exception as e:
            errors.append(f"cloudscraper: {e}")

    # Strategy 3: requests with full browser headers
    try:
        t0 = time.time()
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "sec-ch-ua": '"Chromium";v="124","Google Chrome";v="124"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Referer": "https://www.google.com/",
        })
        r = sess.get(url, timeout=20, allow_redirects=True)
        ms = round((time.time()-t0)*1000)
        if r.status_code < 400:
            return r.text, r.status_code, ms, "requests (browser headers)", None
        errors.append(f"requests: HTTP {r.status_code}")
    except Exception as e:
        errors.append(f"requests: {e}")

    return None, 0, 0, "all methods failed", " | ".join(errors)


def parse_html(html):
    if not BS4_OK or not html:
        return None
    return BeautifulSoup(html, "lxml")

def clean_text(soup):
    s = BeautifulSoup(str(soup), "lxml")
    for t in s(["script","style","noscript","header","footer","nav","aside","iframe"]):
        t.decompose()
    return re.sub(r"\s+", " ", s.get_text(separator=" ")).strip()

def word_freq(text, top=20):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return Counter(w for w in words if w not in STOP_WORDS).most_common(top)

def sc_cls(v):
    return "cg" if v>=80 else "cl" if v>=60 else "ca" if v>=40 else "cr"

def slug_analysis(url):
    p = urllib.parse.urlparse(url)
    path = p.path.rstrip("/")
    slug = path.split("/")[-1] if path else ""
    issues, score = [], 100
    if not slug:
        slug = "(homepage)"
    else:
        if len(slug)>75:                    issues.append("Slug too long (>75 chars)"); score-=20
        if re.search(r'[A-Z]',slug):       issues.append("Has uppercase — use lowercase"); score-=15
        if re.search(r'_',slug):           issues.append("Has underscores — use hyphens"); score-=10
        if re.search(r'\d{6,}',slug):      issues.append("Contains long numeric ID"); score-=10
        if re.search(r'[^a-z0-9\-/.]',slug): issues.append("Has special characters"); score-=15
    return slug, max(0,score), issues

def check_robots(base):
    for lib in (["curl_cffi"] if CURL_OK else []) + (["cloudscraper"] if CLOUD_OK else []) + ["requests"]:
        try:
            url = f"{base}/robots.txt"
            if lib=="curl_cffi":
                r = cffi_requests.get(url, impersonate="chrome124", timeout=8)
            elif lib=="cloudscraper":
                r = cloudscraper.create_scraper().get(url, timeout=8)
            else:
                r = requests.get(url, timeout=8,
                    headers={"User-Agent":"Mozilla/5.0 Chrome/124"})
            if r.status_code==200: return True, r.text[:600]
        except: pass
    return False, ""

def check_sitemap(base):
    for path in ["/sitemap.xml","/sitemap_index.xml","/sitemap/sitemap.xml"]:
        for lib in (["curl_cffi"] if CURL_OK else []) + ["requests"]:
            try:
                u = f"{base}{path}"
                r = (cffi_requests.get(u, impersonate="chrome124", timeout=8) if lib=="curl_cffi"
                     else requests.get(u, timeout=8, headers={"User-Agent":"Mozilla/5.0 Chrome/124"}))
                if r.status_code==200: return True, u
            except: pass
    return False, ""

def analyse_images(soup):
    imgs = soup.find_all("img")
    miss = [i for i in imgs if not i.get("alt","").strip()]
    lazy = sum(1 for i in imgs if i.get("loading")=="lazy")
    oldf = sum(1 for i in imgs if i.get("src","") and
               not any(x in i.get("src","").lower() for x in [".webp",".avif",".svg"]))
    return {"total":len(imgs),"missing_alt":len(miss),"lazy":lazy,"old_fmt":oldf,
            "miss_srcs":[i.get("src","")[:70] for i in miss[:4]]}

def analyse_social(soup):
    og,tw={},{}
    for m in soup.find_all("meta"):
        prop=(m.get("property","") or m.get("name",""))
        c=m.get("content","")
        if prop.startswith("og:"): og[prop]=c
        if prop.startswith("twitter:"): tw[prop]=c
    return og,tw

def analyse_schema(soup):
    types=[]
    for s in soup.find_all("script",{"type":"application/ld+json"}):
        try:
            d=json.loads(s.string or "")
            t=d.get("@type") or (d.get("@graph",[{}])[0].get("@type") if "@graph" in d else "Unknown")
            if isinstance(t,list): types.extend(t)
            else: types.append(str(t))
        except: pass
    return types

# ─────────────────────────────────────────────────────────────
def full_analyse(url, focus_kw):
    # Status area
    status_ph = st.empty()

    with status_ph.container():
        st.info("⏳ **Step 1/3** — Connecting to page (trying best fetch method)…")

    html, status_code, load_ms, method_used, fetch_err = fetch_with_best_method(url)

    if fetch_err and not html:
        status_ph.empty()
        st.error(f"""
**❌ Could not fetch the page.**

**Reason:** {fetch_err}

**What this means for hiring4jobs.com:**
The site is protected by **Cloudflare** which blocks automated Python requests. 
This is a server-side protection — your site is working fine for real users.

**Solutions:**
- Run this tool **locally** on your computer (`streamlit run seo_analyser.py`)
- Use a **Selenium/Playwright** based tool with a real browser
- Check the SEO manually via **Google Search Console** → your actual indexed data
- Use **Screaming Frog SEO Spider** (free up to 500 URLs) for full audits
        """)
        # Still show URL-level analysis
        _show_url_analysis(url, focus_kw)
        return

    with status_ph.container():
        st.info(f"⏳ **Step 2/3** — Parsing HTML ({len(html):,} bytes received)…")

    soup = parse_html(html)
    if not soup:
        status_ph.empty()
        st.error("❌ Failed to parse HTML. The page may be JavaScript-rendered (SPA/React).")
        return

    status_ph.empty()

    parsed   = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    focus_kw = focus_kw.strip().lower()

    page_text  = clean_text(soup)
    word_list  = re.findall(r'\b[a-zA-Z]{2,}\b', page_text.lower())
    word_count = len(word_list)

    # ── Meta extraction ──────────────────────────────────────────────────
    title_tag = soup.find("title")
    title_txt = title_tag.get_text(strip=True) if title_tag else ""
    meta_desc=meta_kw=canonical=robots_meta=lang=viewport=charset=""

    for m in soup.find_all("meta"):
        n=(m.get("name") or "").lower()
        c=m.get("content","")
        if n=="description": meta_desc=c
        if n=="keywords":    meta_kw=c
        if n=="robots":      robots_meta=c
        if n=="viewport":    viewport=c
        if m.get("charset"): charset=m["charset"]
    ht=soup.find("html")
    if ht: lang=ht.get("lang","")
    lc=soup.find("link",{"rel":"canonical"})
    if lc: canonical=lc.get("href","")

    # ── Headings ─────────────────────────────────────────────────────────
    headings={}; all_h=[]
    for lv in range(1,7):
        tags=soup.find_all(f"h{lv}")
        headings[f"h{lv}"]=[t.get_text(strip=True) for t in tags]
        for t in tags: all_h.append((f"h{lv}",t.get_text(strip=True)))

    paras=soup.find_all("p")

    # ── Links ─────────────────────────────────────────────────────────────
    int_links=[]; ext_links=[]; nf=0
    for a in soup.find_all("a",href=True):
        href=a["href"].strip()
        anchor=a.get_text(strip=True)[:70]
        rel=a.get("rel",[])
        if "nofollow" in rel: nf+=1
        if href.startswith("http") and parsed.netloc not in href:
            ext_links.append((href,anchor))
        elif href and not href.startswith(("javascript","mailto","#","tel")):
            int_links.append((urllib.parse.urljoin(url,href),anchor))

    img_data    = analyse_images(soup)
    scripts     = soup.find_all("script",src=True)
    stylesheets = soup.find_all("link",{"rel":"stylesheet"})
    og,tw       = analyse_social(soup)
    schemas     = analyse_schema(soup)
    all_meta    = [(m.get("name") or m.get("property") or m.get("http-equiv",""),
                    m.get("content","")[:110])
                   for m in soup.find_all("meta")
                   if m.get("name") or m.get("property") or m.get("http-equiv")]

    slug,slug_sc,slug_iss = slug_analysis(url)
    has_robots,robots_txt = check_robots(base_url)
    has_sitemap,sitemap_u = check_sitemap(base_url)
    kw_freq = word_freq(page_text, 20)

    if TEXTSTAT_OK:
        try:
            flesch=round(textstat.flesch_reading_ease(page_text))
            grade =textstat.text_standard(page_text,float_output=False)
        except: flesch,grade=0,"N/A"
    else: flesch,grade=0,"N/A"

    # ── Scores ────────────────────────────────────────────────────────────
    def ts():
        s=0
        if title_txt:
            s+=30; l=len(title_txt)
            s+=(30 if 50<=l<=60 else 15 if 40<=l<=70 else 0)
            if focus_kw and focus_kw in title_txt.lower(): s+=20
            if any(c in title_txt for c in ["|","-","–"]): s+=10
            if title_txt[0].isupper(): s+=10
        return min(100,s)
    def ms_():
        s=0
        if meta_desc:
            s+=30; l=len(meta_desc)
            s+=(35 if 130<=l<=160 else 20 if 100<=l<=180 else 0)
            if focus_kw and focus_kw in meta_desc.lower(): s+=20
            if any(c in meta_desc for c in ["!","?",".",","]): s+=15
        return min(100,s)
    def cs():
        s=0
        if word_count>=300:s+=20
        if word_count>=600:s+=15
        if word_count>=1000:s+=15
        if headings.get("h1"):s+=15
        if len(headings.get("h2",[]))>=2:s+=10
        if len(headings.get("h3",[]))>=2:s+=5
        if len(paras)>=5:s+=10
        if focus_kw:
            d=page_text.lower().count(focus_kw)/max(word_count,1)*100
            if .5<=d<=2.5:s+=10
        return min(100,s)
    def tech_s():
        s=0
        if url.startswith("https"):s+=20
        if canonical:s+=10
        if lang:s+=10
        if viewport:s+=10
        if charset:s+=5
        if has_robots:s+=10
        if has_sitemap:s+=15
        if "noindex" not in robots_meta.lower():s+=10
        if img_data["missing_alt"]==0:s+=10
        return min(100,s)
    def sp_s():
        s=(95 if load_ms<500 else 80 if load_ms<1000 else 65 if load_ms<2000
           else 45 if load_ms<3000 else 25 if load_ms<5000 else 10)
        if img_data["lazy"]>0:s=min(100,s+5)
        if len(scripts)<10:s=min(100,s+5)
        return s
    def kw_s():
        if not focus_kw:return 50
        s=0
        if focus_kw in title_txt.lower():s+=25
        if focus_kw in meta_desc.lower():s+=20
        if any(focus_kw in h.lower() for h in headings.get("h1",[])):s+=20
        if focus_kw in page_text.lower():s+=15
        if focus_kw.replace(" ","-") in url.lower():s+=10
        d=page_text.lower().count(focus_kw)/max(word_count,1)*100
        if .5<=d<=2.5:s+=10
        return min(100,s)
    def soc_s():
        s=0
        if og.get("og:title"):s+=20
        if og.get("og:description"):s+=20
        if og.get("og:image"):s+=20
        if tw.get("twitter:card"):s+=20
        if tw.get("twitter:title"):s+=10
        if tw.get("twitter:image"):s+=10
        return min(100,s)

    SC={
        "title":ts(),"meta":ms_(),"content":cs(),
        "tech":tech_s(),"speed":sp_s(),"kw":kw_s(),"social":soc_s(),
    }
    SC["overall"]=round(SC["title"]*.16+SC["meta"]*.12+SC["content"]*.22+
                        SC["tech"]*.20+SC["speed"]*.15+SC["kw"]*.08+SC["social"]*.07)

    # ── Yoast checks ─────────────────────────────────────────────────────
    def yoast():
        C=[]
        def a(s,t):C.append((s,t))
        if not title_txt:       a("r","Page title is missing")
        elif len(title_txt)<30: a("y",f"Title short ({len(title_txt)} chars) — aim 50–60")
        elif len(title_txt)>70: a("y",f"Title too long ({len(title_txt)} chars)")
        else:                   a("g",f"Title length good ({len(title_txt)} chars)")
        if focus_kw:
            a("g","Focus keyword in title") if focus_kw in title_txt.lower() else a("r","Focus keyword NOT in title")
        if not meta_desc:         a("r","Meta description missing")
        elif len(meta_desc)<100: a("y",f"Meta desc short ({len(meta_desc)} chars)")
        elif len(meta_desc)>165: a("y",f"Meta desc long ({len(meta_desc)} chars)")
        else:                    a("g",f"Meta desc good ({len(meta_desc)} chars)")
        if focus_kw and meta_desc:
            a("g","Keyword in meta desc") if focus_kw in meta_desc.lower() else a("y","Keyword not in meta desc")
        h1s=headings.get("h1",[])
        if not h1s:       a("r","No H1 heading found")
        elif len(h1s)>1:  a("y",f"Multiple H1s ({len(h1s)}) — use only one")
        else:             a("g","One H1 tag ✓")
        if focus_kw and h1s:
            a("g","Keyword in H1") if any(focus_kw in h.lower() for h in h1s) else a("y","Keyword not in H1")
        if word_count<300:   a("r",f"Thin content ({word_count} words) — aim 600+")
        elif word_count<600: a("y",f"Content could be longer ({word_count} words)")
        else:                a("g",f"Good content length ({word_count} words)")
        if focus_kw:
            cnt=page_text.lower().count(focus_kw); d=cnt/max(word_count,1)*100
            if d<.5:  a("y",f"Keyword density low ({d:.2f}%) — aim 0.5–2.5%")
            elif d>3: a("r",f"Keyword density too high ({d:.2f}%) — stuffing risk")
            else:     a("g",f"Keyword density good ({d:.2f}%)")
        a("g","HTTPS ✓") if url.startswith("https") else a("r","Not using HTTPS")
        a("g","Canonical URL set") if canonical else a("y","No canonical URL")
        if img_data["missing_alt"]==0:  a("g","All images have alt text ✓")
        elif img_data["missing_alt"]<3: a("y",f"{img_data['missing_alt']} image(s) missing alt")
        else:                           a("r",f"{img_data['missing_alt']} images missing alt text")
        a("r","noindex found — page won't index!") if "noindex" in robots_meta.lower() else a("g","Page is indexable ✓")
        a("g","Sitemap found ✓") if has_sitemap else a("y","No sitemap.xml detected")
        a("g","robots.txt accessible ✓") if has_robots else a("y","robots.txt not found")
        if len(int_links)>=3:   a("g",f"{len(int_links)} internal links ✓")
        elif len(int_links)>0:  a("y",f"Only {len(int_links)} internal links — add more")
        else:                   a("r","No internal links found")
        a("g",f"Structured data: {', '.join(schemas)}") if schemas else a("y","No Schema.org/JSON-LD found")
        a("g","Open Graph tags present ✓") if og.get("og:title") else a("y","Open Graph tags missing")
        a("g",f"lang='{lang}' ✓") if lang else a("y","HTML lang attribute missing")
        a("g","Viewport meta present ✓") if viewport else a("r","Viewport meta missing — not mobile-friendly")
        if load_ms<1000:   a("g",f"Fast load: {load_ms}ms ✓")
        elif load_ms<3000: a("y",f"Moderate load: {load_ms}ms")
        else:              a("r",f"Slow load: {load_ms}ms — needs optimisation")
        if len(headings.get("h2",[]))>=2: a("g",f"{len(headings['h2'])} H2 subheadings ✓")
        else:                             a("y","Add more H2 subheadings for structure")
        return C
    checks=yoast()

    # ════════════════════════════════════════════
    #  RENDER
    # ════════════════════════════════════════════

    # Fetch info banner
    st.markdown(f"""
    <div class="fetch-info">
      <b>✅ Page fetched via:</b> {method_used} &nbsp;·&nbsp;
      <b>Status:</b> {status_code} &nbsp;·&nbsp;
      <b>Load time:</b> {load_ms}ms &nbsp;·&nbsp;
      <b>HTML size:</b> {len(html):,} bytes &nbsp;·&nbsp;
      <b>Words:</b> {word_count:,}
    </div>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown(f"""
    <div class="hero">
      <h1>🔍 SEO Report</h1>
      <p><span class="brand">{url[:70]}</span><br>
      <span style="color:#475569;font-size:.73rem">{datetime.now().strftime('%d %b %Y, %H:%M')}</span></p>
    </div>""", unsafe_allow_html=True)

    # Score cards
    score_items=[("Overall",SC["overall"]),("Content",SC["content"]),("Technical",SC["tech"]),
                 ("Title",SC["title"]),("Meta",SC["meta"]),("Speed",SC["speed"]),("Social",SC["social"])]
    html_sc="".join(f'<div class="sc"><div class="scn {sc_cls(v)}">{v}</div><div class="scl">{l}</div></div>'
                    for l,v in score_items)
    st.markdown(f'<div class="score-grid">{html_sc}</div>', unsafe_allow_html=True)

    # Tabs
    tabs=st.tabs(["📋 Overview","✅ Checklist","🎯 Keywords","🔗 Links","🏗️ Structure","📣 Social","⚡ Speed","🏷️ Tags"])

    css_c=["h1t","h2t","h3t","h4t","h5t","h6t"]

    # ── TAB 0: Overview ──────────────────────────────────────────────────
    with tabs[0]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stit">📋 Basic SEO</div>', unsafe_allow_html=True)
            for n,v in [
                ("Title",(title_txt[:55]+"…" if len(title_txt)>55 else title_txt) or "❌ Missing"),
                ("Title Length",f'{len(title_txt)} chars {"✅" if 50<=len(title_txt)<=60 else "⚠️"}'),
                ("Meta Desc",(meta_desc[:75]+"…" if len(meta_desc)>75 else meta_desc) or "❌ Missing"),
                ("Meta Length",f'{len(meta_desc)} chars {"✅" if 130<=len(meta_desc)<=160 else "⚠️"}'),
                ("Canonical",canonical[:50] or "❌ Not set"),
                ("Robots Meta",robots_meta or "index,follow"),
                ("HTML Lang",lang or "❌ Not set"),
                ("Viewport","✅ Yes" if viewport else "❌ Missing"),
                ("Charset",charset or "Not detected"),
                ("HTTP Status",f'{status_code} {"✅" if status_code==200 else "⚠️"}'),
                ("HTTPS","✅ Secure" if url.startswith("https") else "❌ No"),
                ("Load Time",f'{load_ms}ms {"🟢" if load_ms<1000 else "🟡" if load_ms<3000 else "🔴"}'),
            ]:
                st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="scard"><div class="stit">📝 Content Stats</div>',unsafe_allow_html=True)
            for n,v in [
                ("Word Count",str(word_count)),("Paragraphs",str(len(paras))),
                ("H1",str(len(headings.get("h1",[])))),("H2",str(len(headings.get("h2",[])))),
                ("H3",str(len(headings.get("h3",[])))),("H4",str(len(headings.get("h4",[])))),
                ("H5+H6",str(len(headings.get("h5",[]))+len(headings.get("h6",[])))),
                ("Images",str(img_data["total"])),
                ("Missing Alt",f'{img_data["missing_alt"]} {"✅" if img_data["missing_alt"]==0 else "❌"}'),
                ("Lazy Images",str(img_data["lazy"])),
                ("Int Links",str(len(int_links))),("Ext Links",str(len(ext_links))),
                ("Nofollow",str(nf)),
                ("JS Files",str(len(scripts))),("CSS Files",str(len(stylesheets))),
                ("Flesch Score",str(flesch)),("Grade Level",grade),
                ("Schema",", ".join(schemas) if schemas else "None"),
            ]:
                st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

        # URL Slug
        st.markdown('<div class="scard"><div class="stit">🔗 URL & Slug</div>',unsafe_allow_html=True)
        depth=len([p for p in parsed.path.split('/') if p])
        for n,v in [
            ("Full URL",url[:80]),("Slug",slug),
            ("Slug Score",f'{slug_sc}/100'),("Path Depth",f'{depth} levels'),
            ("Query Params","✅ None" if not parsed.query else f"⚠️ {parsed.query[:50]}"),
        ]:
            st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
        for iss in slug_iss:
            st.markdown(f'<div class="ibox iwn">⚠️ {iss}</div>',unsafe_allow_html=True)
        if not slug_iss:
            st.markdown('<div class="ibox iok">✅ Slug is clean & SEO-friendly</div>',unsafe_allow_html=True)
        pct=slug_sc
        st.markdown(f'<div class="pgwrap"><div class="pgfill" style="width:{pct}%;background:#3b82f6"></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

        # Recommendations
        st.markdown('<div class="scard"><div class="stit">💡 Priority Recommendations</div>',unsafe_allow_html=True)
        recs=[]
        if not title_txt:             recs.append(("er","Add a page title immediately"))
        elif len(title_txt)>70:       recs.append(("wn",f"Shorten title to <60 chars (currently {len(title_txt)})"))
        if not meta_desc:             recs.append(("er","Add meta description (130–160 chars)"))
        if not canonical:             recs.append(("wn","Set canonical URL"))
        if img_data["missing_alt"]>0: recs.append(("wn",f"Add alt text to {img_data['missing_alt']} image(s)"))
        if not has_sitemap:           recs.append(("wn","Create sitemap.xml"))
        if not schemas:               recs.append(("in","Add JSON-LD schema (JobPosting, Organization…)"))
        if not og.get("og:image"):    recs.append(("wn","Add og:image for social sharing"))
        if word_count<600:            recs.append(("er",f"Increase content ({word_count} words → aim 600+)"))
        if load_ms>3000:              recs.append(("er",f"Improve page speed ({load_ms}ms → aim <1s)"))
        if len(int_links)<3:          recs.append(("wn","Add more internal links"))
        if not lang:                  recs.append(("wn","Set HTML lang attribute"))
        if not recs:                  recs.append(("ok","🎉 No major issues found!"))
        cm={"er":"ier","wn":"iwn","in":"inf","ok":"iok"}
        im={"er":"❌","wn":"⚠️","in":"ℹ️","ok":"✅"}
        for k,msg in recs:
            st.markdown(f'<div class="ibox {cm[k]}">{im[k]} {msg}</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 1: Checklist ────────────────────────────────────────────────
    with tabs[1]:
        gn=sum(1 for s,_ in checks if s=="g")
        yn=sum(1 for s,_ in checks if s=="y")
        rn=sum(1 for s,_ in checks if s=="r")
        st.markdown(f'<div class="scard"><div class="stit">✅ SEO Checklist ({len(checks)} checks)</div>'
                    f'<div style="display:flex;gap:16px;margin-bottom:12px;flex-wrap:wrap">'
                    f'<span style="color:#22c55e;font-weight:600;font-size:.8rem">✅ {gn} passed</span>'
                    f'<span style="color:#f59e0b;font-weight:600;font-size:.8rem">⚠️ {yn} warnings</span>'
                    f'<span style="color:#ef4444;font-weight:600;font-size:.8rem">❌ {rn} issues</span>'
                    f'</div>',unsafe_allow_html=True)
        for s,t in checks:
            dc={"g":"dg","y":"dy","r":"dr"}[s]
            st.markdown(f'<div class="chk"><div class="dot {dc}"></div><div class="ct">{t}</div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 2: Keywords ──────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="scard"><div class="stit">🎯 Focus Keyword</div>',unsafe_allow_html=True)
        if focus_kw:
            cnt=page_text.lower().count(focus_kw); d=cnt/max(word_count,1)*100
            for n,v in [
                ("Keyword",f'<span style="color:#38bdf8;font-weight:600">{focus_kw}</span>'),
                ("Occurrences",str(cnt)),
                ("Density",f'{d:.2f}% {"✅" if .5<=d<=2.5 else "⚠️"}'),
                ("In Title","✅" if focus_kw in title_txt.lower() else "❌"),
                ("In Meta","✅" if focus_kw in meta_desc.lower() else "❌"),
                ("In H1","✅" if any(focus_kw in h.lower() for h in headings.get("h1",[])) else "❌"),
                ("In URL","✅" if focus_kw.replace(" ","-") in url.lower() else "❌"),
                ("Score",f'<span class="{sc_cls(SC["kw"])}" style="font-weight:700">{SC["kw"]}/100</span>'),
            ]:
                st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="ibox inf">ℹ️ Enter a focus keyword in the input bar above for analysis</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

        st.markdown('<div class="scard"><div class="stit">📊 Top Keywords on Page</div>',unsafe_allow_html=True)
        mx=kw_freq[0][1] if kw_freq else 1
        for word,cnt in kw_freq:
            pct=round(cnt/mx*100)
            st.markdown(f'<div class="kwrow"><span class="kww">{word}</span><span class="kwc">{cnt}×</span>'
                        f'<div class="kwbw"><div class="kwbf" style="width:{pct}%"></div></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 3: Links ─────────────────────────────────────────────────────
    with tabs[3]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown(f'<div class="scard"><div class="stit">🔁 Internal Links ({len(int_links)})</div><div class="scrl">',unsafe_allow_html=True)
            for href,anc in int_links[:60]:
                st.markdown(f'<div class="lpill"><span class="lanc">⬡ {anc or "(no anchor)"}</span><span class="lhref">{href[:80]}</span></div>',unsafe_allow_html=True)
            if not int_links:
                st.markdown('<div class="ibox ier">No internal links found</div>',unsafe_allow_html=True)
            st.markdown('</div></div>',unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="scard"><div class="stit">🌐 External Links ({len(ext_links)})</div><div class="scrl">',unsafe_allow_html=True)
            for href,anc in ext_links[:60]:
                st.markdown(f'<div class="lpill"><span class="lanc">↗ {anc or "(no anchor)"}</span><span class="lhref">{href[:80]}</span></div>',unsafe_allow_html=True)
            if not ext_links:
                st.markdown('<div class="ibox inf">No external links found</div>',unsafe_allow_html=True)
            st.markdown('</div></div>',unsafe_allow_html=True)

    # ── TAB 4: Structure ─────────────────────────────────────────────────
    with tabs[4]:
        cols6=st.columns(6)
        for i,lv in enumerate(range(1,7)):
            cols6[i].markdown(f'<div style="text-align:center"><span class="htag {css_c[i]}">H{lv}</span>'
                              f'<div style="color:#e2e8f0;font-size:1.4rem;font-weight:700;margin-top:3px">{len(headings.get(f"h{lv}",[]))}</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="scard" style="margin-top:12px"><div class="stit">Heading Tree</div><div class="scrl">',unsafe_allow_html=True)
        for tag,txt in all_h:
            lv=tag[1]
            st.markdown(f'<div class="hrow"><span class="htag {css_c[int(lv)-1]}">{tag.upper()}</span><span class="htxt">{txt[:100]}</span></div>',unsafe_allow_html=True)
        if not all_h:
            st.markdown('<div class="ibox ier">No headings found</div>',unsafe_allow_html=True)
        st.markdown('</div></div>',unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stit">🤖 Robots & Sitemap</div>',unsafe_allow_html=True)
            for n,v in [("robots.txt","✅ Found" if has_robots else "❌ Not found"),
                        ("Sitemap","✅ "+sitemap_u if has_sitemap else "❌ Not found")]:
                st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
            if has_robots and robots_txt:
                st.markdown(f'<div style="background:#131924;border-radius:7px;padding:9px;margin-top:7px;font-size:.71rem;color:#94a3b8;font-family:monospace;max-height:110px;overflow-y:auto">{robots_txt.replace(chr(10),"<br>")}</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="scard"><div class="stit">📐 Structured Data</div>',unsafe_allow_html=True)
            if schemas:
                for s in schemas:
                    st.markdown(f'<div class="ibox iok">✅ {s}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox iwn">⚠️ No JSON-LD found. Add JobPosting, Organization, or WebSite schema.</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 5: Social ────────────────────────────────────────────────────
    with tabs[5]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown('<div class="scard"><div class="stit">📘 Open Graph</div>',unsafe_allow_html=True)
            if og:
                for k,v in og.items():
                    st.markdown(f'<div class="mrow"><span class="mn">{k}</span><span class="mv">{v[:65]}</span></div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox iwn">⚠️ No OG tags found</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="scard"><div class="stit">🐦 Twitter / X Card</div>',unsafe_allow_html=True)
            if tw:
                for k,v in tw.items():
                    st.markdown(f'<div class="mrow"><span class="mn">{k}</span><span class="mv">{v[:65]}</span></div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="ibox iwn">⚠️ No Twitter Card tags found</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 6: Speed ─────────────────────────────────────────────────────
    with tabs[6]:
        size_kb=round(len(html)/1024,1)
        st.markdown('<div class="scard"><div class="stit">⚡ Page Speed (Heuristic)</div>',unsafe_allow_html=True)
        for n,v in [
            ("Response Time",f'{load_ms}ms {"🟢" if load_ms<800 else "🟡" if load_ms<2500 else "🔴"}'),
            ("HTML Size",f'{size_kb} KB {"✅" if size_kb<100 else "⚠️ Large"}'),
            ("JS Files",f'{len(scripts)} {"✅" if len(scripts)<=8 else "⚠️"}'),
            ("CSS Files",f'{len(stylesheets)} {"✅" if len(stylesheets)<=4 else "⚠️"}'),
            ("Images",str(img_data["total"])),
            ("Lazy Loaded",f'{img_data["lazy"]} {"✅" if img_data["lazy"]>0 else "⚠️ None"}'),
            ("Non-WebP/AVIF",f'{img_data["old_fmt"]} {"✅" if img_data["old_fmt"]==0 else "⚠️ Optimise"}'),
            ("Speed Score",f'{SC["speed"]}/100'),
        ]:
            st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
        sp=SC["speed"]
        bc="#22c55e" if sp>=80 else "#f59e0b" if sp>=50 else "#ef4444"
        st.markdown(f'<div class="pgwrap" style="margin-top:10px"><div class="pgfill" style="width:{sp}%;background:{bc}"></div></div>',unsafe_allow_html=True)
        if load_ms>3000:
            st.markdown('<div class="ibox ier" style="margin-top:10px">❌ Very slow. Check hosting, enable caching, use CDN.</div>',unsafe_allow_html=True)
        elif load_ms>1500:
            st.markdown('<div class="ibox iwn" style="margin-top:10px">⚠️ Moderate speed. Optimise images, reduce JS.</div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="ibox iok" style="margin-top:10px">✅ Good response time!</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    # ── TAB 7: Tags ──────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown(f'<div class="scard"><div class="stit">🏷️ All Meta Tags ({len(all_meta)})</div>',unsafe_allow_html=True)
        chips="".join(f'<span class="chip">{n}</span>' for n,_ in all_meta)
        st.markdown(f'<div style="margin-bottom:12px">{chips}</div>',unsafe_allow_html=True)
        st.markdown('<div class="scrl">',unsafe_allow_html=True)
        for n,v in all_meta:
            st.markdown(f'<div class="mrow"><span class="mn" style="min-width:140px">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
        st.markdown('</div></div>',unsafe_allow_html=True)


def _show_url_analysis(url, focus_kw):
    """Show what we can analyse from just the URL even without fetching."""
    slug, slug_sc, slug_iss = slug_analysis(url)
    parsed = urllib.parse.urlparse(url)
    focus_kw = focus_kw.strip().lower()

    st.markdown("---")
    st.markdown("### 🔗 URL Analysis (available without page access)")
    st.markdown(f'<div class="scard">',unsafe_allow_html=True)
    depth=len([p for p in parsed.path.split('/') if p])
    kw_in_url = focus_kw and (focus_kw.replace(" ","-") in url.lower() or focus_kw.replace(" ","") in url.lower())
    for n,v in [
        ("Full URL", url),
        ("Domain", parsed.netloc),
        ("Path", parsed.path),
        ("Slug", slug),
        ("Slug Score", f'{slug_sc}/100'),
        ("Path Depth", f'{depth} levels'),
        ("HTTPS", "✅ Secure" if url.startswith("https") else "❌ Not secure"),
        ("Query Params", "✅ None" if not parsed.query else f"⚠️ {parsed.query}"),
        ("Keyword in URL", f'✅ Yes — "{focus_kw}"' if kw_in_url else ("❌ No" if focus_kw else "N/A (no keyword set)")),
    ]:
        st.markdown(f'<div class="mrow"><span class="mn">{n}</span><span class="mv">{v}</span></div>',unsafe_allow_html=True)
    for iss in slug_iss:
        st.markdown(f'<div class="ibox iwn">⚠️ {iss}</div>',unsafe_allow_html=True)
    if not slug_iss:
        st.markdown(f'<div class="ibox iok">✅ Slug looks clean and keyword-rich</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>🔍 SEO Analyser</h1>
  <p>Full Yoast-style audit · Free · No API keys · Mobile-friendly</p>
</div>
""",unsafe_allow_html=True)

# Input bar
col_url,col_kw,col_btn=st.columns([3,2,1])
with col_url:
    url_val=st.text_input("🌐 Page URL",value="https://www.hiring4jobs.com/jobs/graduate-engineer-trainee-volvo-group-job-872",
                          placeholder="https://example.com",label_visibility="visible")
with col_kw:
    kw_val=st.text_input("🎯 Focus Keyword",value="graduate engineer trainee",
                         placeholder="e.g. jobs in chennai",label_visibility="visible")
with col_btn:
    st.markdown("<div style='height:28px'></div>",unsafe_allow_html=True)
    run=st.button("🔍 Analyse Now",use_container_width=True)

if run:
    raw=url_val.strip()
    if not raw:
        st.warning("⚠️ Please enter a URL.")
    else:
        if not raw.startswith("http"):
            raw="https://"+raw
        full_analyse(raw,kw_val)
else:
    st.markdown("""
    <div style="text-align:center;padding:30px 12px">
      <div style="font-size:2.5rem;margin-bottom:10px">🔍</div>
      <div style="color:#94a3b8;font-size:.95rem">Enter a URL above and click <b style="color:#38bdf8">Analyse Now</b></div>
      <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:18px">
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">📊 25+ metrics</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">✅ Yoast checklist</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">🎯 Keyword score</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">⚡ Speed insights</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">🔗 Link audit</div>
        <div style="background:#1e2533;border:1px solid #2d3748;border-radius:9px;padding:10px 14px;color:#94a3b8;font-size:.79rem">📣 Social tags</div>
      </div>
    </div>
    """,unsafe_allow_html=True)
