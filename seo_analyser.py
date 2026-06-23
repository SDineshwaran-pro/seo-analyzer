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

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Analyser – hiring4jobs.com",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styles ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0f1117; }

.hero-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2d3748;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    text-align: center;
}
.hero-header h1 { color: #e2e8f0; font-size: 2.2rem; font-weight: 700; margin: 0 0 8px; }
.hero-header p  { color: #94a3b8; font-size: 1rem; margin: 0; }
.hero-header .brand { color: #38bdf8; font-weight: 700; }

/* Score cards */
.score-card {
    background: #1e2533;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 16px;
}
.score-num { font-size: 3rem; font-weight: 700; line-height: 1; }
.score-label { color: #94a3b8; font-size: 0.85rem; margin-top: 6px; font-weight: 500; letter-spacing: .5px; text-transform: uppercase; }
.score-excellent { color: #22c55e; }
.score-good      { color: #84cc16; }
.score-ok        { color: #f59e0b; }
.score-poor      { color: #ef4444; }

/* Status badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-pass  { background: #14532d; color: #4ade80; }
.badge-warn  { background: #713f12; color: #fbbf24; }
.badge-fail  { background: #450a0a; color: #f87171; }
.badge-info  { background: #1e3a5f; color: #60a5fa; }

/* Section cards */
.section-card {
    background: #1e2533;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.section-title { color: #e2e8f0; font-size: 1.1rem; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

/* Metric rows */
.metric-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #2d3748; }
.metric-row:last-child { border-bottom: none; }
.metric-name  { color: #94a3b8; font-size: 0.88rem; }
.metric-value { color: #e2e8f0; font-size: 0.88rem; font-weight: 500; text-align: right; max-width: 60%; word-break: break-word; }

/* Link pills */
.link-pill {
    background: #1a2235;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 0.8rem;
    color: #94a3b8;
    word-break: break-all;
}
.link-pill .link-text { color: #60a5fa; }
.link-pill .link-anchor { color: #a78bfa; margin-right: 8px; }

/* Progress bar */
.prog-wrap { background: #2d3748; border-radius: 100px; height: 8px; margin-top: 6px; overflow: hidden; }
.prog-fill  { height: 8px; border-radius: 100px; }

/* Tag chip */
.tag-chip { display: inline-block; background: #1e3a5f; color: #93c5fd; border-radius: 6px; padding: 3px 10px; font-size: 0.78rem; margin: 3px; font-weight: 500; }

/* Keyword row */
.kw-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #232b3a; }
.kw-row:last-child { border-bottom: none; }
.kw-word { color: #e2e8f0; font-size: 0.88rem; min-width: 120px; font-weight: 500; }
.kw-count { color: #94a3b8; font-size: 0.82rem; min-width: 40px; }
.kw-bar-wrap { flex: 1; background: #2d3748; border-radius: 100px; height: 6px; }
.kw-bar-fill { height: 6px; border-radius: 100px; background: linear-gradient(90deg, #3b82f6, #818cf8); }

/* Yoast-style checklist */
.check-item { display: flex; align-items: flex-start; gap: 10px; padding: 9px 0; border-bottom: 1px solid #232b3a; }
.check-item:last-child { border-bottom: none; }
.check-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; }
.dot-green  { background: #22c55e; }
.dot-yellow { background: #f59e0b; }
.dot-red    { background: #ef4444; }
.dot-grey   { background: #475569; }
.check-text { color: #cbd5e1; font-size: 0.86rem; line-height: 1.5; }

/* Insight boxes */
.insight-box { border-left: 3px solid; padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 8px; }
.insight-success { border-color: #22c55e; background: #0f2d1f; color: #86efac; }
.insight-warning { border-color: #f59e0b; background: #2d1f0f; color: #fcd34d; }
.insight-error   { border-color: #ef4444; background: #2d0f0f; color: #fca5a5; }
.insight-info    { border-color: #3b82f6; background: #0f1f2d; color: #93c5fd; }

/* Heading tags */
.h-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-right: 8px; min-width: 30px; text-align: center; }
.h1-tag { background: #450a0a; color: #fca5a5; }
.h2-tag { background: #1e3a5f; color: #93c5fd; }
.h3-tag { background: #14532d; color: #86efac; }
.h4-tag { background: #2d1f0f; color: #fcd34d; }
.h5-tag { background: #1e1e40; color: #c4b5fd; }
.h6-tag { background: #2d2d2d; color: #9ca3af; }

.heading-row { display: flex; align-items: flex-start; padding: 8px 0; border-bottom: 1px solid #232b3a; gap: 8px; }
.heading-row:last-child { border-bottom: none; }
.heading-text { color: #cbd5e1; font-size: 0.87rem; flex: 1; }

/* Scrollable area */
.scroll-area { max-height: 320px; overflow-y: auto; padding-right: 4px; }

/* Analyse button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    width: 100%;
    transition: opacity .2s;
}
div[data-testid="stButton"] > button:hover { opacity: .88; }

/* Input */
div[data-testid="stTextInput"] input {
    background: #1e2533 !important;
    border: 1px solid #3b4563 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
}

/* Spinner */
.stSpinner > div { color: #60a5fa !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] { background: #161b27 !important; border-right: 1px solid #2d3748; }
[data-testid="stSidebar"] .stMarkdown { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
    "three","four","five","first","last","&amp;","–","—","|","-",
}


def fetch_page(url: str):
    """Return (soup, response, load_time_ms, error)."""
    try:
        t0 = time.time()
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        elapsed = round((time.time() - t0) * 1000)
        soup = BeautifulSoup(r.text, "lxml")
        return soup, r, elapsed, None
    except Exception as e:
        return None, None, 0, str(e)


def clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    return re.sub(r"\s+", " ", soup.get_text(separator=" ")).strip()


def word_freq(text: str, top: int = 20):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered = [w for w in words if w not in STOP_WORDS]
    return Counter(filtered).most_common(top)


def score_color(score: int) -> str:
    if score >= 80: return "score-excellent"
    if score >= 60: return "score-good"
    if score >= 40: return "score-ok"
    return "score-poor"


def badge(text, kind="info"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def progress_bar(value, max_val, color="#3b82f6"):
    pct = min(100, round(value / max_val * 100)) if max_val else 0
    return (
        f'<div class="prog-wrap">'
        f'<div class="prog-fill" style="width:{pct}%;background:{color};"></div>'
        f'</div>'
    )


def slug_analysis(url: str):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    slug = path.split("/")[-1] if path else ""
    issues = []
    score = 100
    if not slug:
        slug = "(homepage)"
    else:
        if len(slug) > 75:
            issues.append("Slug is too long (>75 chars)")
            score -= 20
        if re.search(r'[A-Z]', slug):
            issues.append("Slug contains uppercase letters")
            score -= 15
        if re.search(r'[_]', slug):
            issues.append("Use hyphens instead of underscores")
            score -= 10
        if re.search(r'\d{4,}', slug):
            issues.append("Slug contains numeric IDs (not keyword-rich)")
            score -= 10
        if slug.count("-") > 6:
            issues.append("Slug has too many hyphens")
            score -= 5
        if re.search(r'[^a-z0-9\-/.]', slug):
            issues.append("Slug contains special characters")
            score -= 15
    return slug, max(0, score), issues


def check_robots(base: str):
    try:
        r = requests.get(f"{base}/robots.txt", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            return True, r.text[:800]
        return False, "robots.txt not found"
    except:
        return False, "Could not fetch robots.txt"


def check_sitemap(base: str):
    for path in ["/sitemap.xml", "/sitemap_index.xml", "/sitemap/sitemap.xml"]:
        try:
            r = requests.get(f"{base}{path}", headers=HEADERS, timeout=8)
            if r.status_code == 200 and "xml" in r.headers.get("content-type", "").lower():
                return True, f"{base}{path}"
        except:
            pass
    return False, "No sitemap found"


def analyse_images(soup: BeautifulSoup, base: str):
    imgs = soup.find_all("img")
    total = len(imgs)
    missing_alt = [i for i in imgs if not i.get("alt", "").strip()]
    has_lazy = sum(1 for i in imgs if i.get("loading") == "lazy")
    oversized = []  # heuristic: flag very long src paths (likely unoptimised)
    for i in imgs:
        src = i.get("src", "")
        if src and not any(ext in src.lower() for ext in [".webp", ".avif", ".svg"]):
            oversized.append(src)
    return {
        "total": total,
        "missing_alt": len(missing_alt),
        "lazy_loaded": has_lazy,
        "non_next_gen": len(oversized),
        "samples_missing_alt": [i.get("src", "")[:80] for i in missing_alt[:5]],
    }


def analyse_social(soup: BeautifulSoup):
    og = {}
    tw = {}
    for meta in soup.find_all("meta"):
        prop = meta.get("property", "") or meta.get("name", "")
        content = meta.get("content", "")
        if prop.startswith("og:"):
            og[prop] = content
        if prop.startswith("twitter:"):
            tw[prop] = content
    return og, tw


def analyse_schema(soup: BeautifulSoup):
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    schemas = []
    for s in scripts:
        try:
            data = json.loads(s.string or "")
            t = data.get("@type") or (data.get("@graph", [{}])[0].get("@type") if "@graph" in data else "Unknown")
            schemas.append(t)
        except:
            schemas.append("(parse error)")
    return schemas


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ANALYSER
# ═══════════════════════════════════════════════════════════════════════════════

def full_analyse(url: str, focus_kw: str = ""):
    with st.spinner("🔍 Fetching page…"):
        soup, resp, load_ms, err = fetch_page(url)

    if err or soup is None:
        st.error(f"❌ Could not fetch page: {err}")
        return

    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    focus_kw = focus_kw.strip().lower()

    # ── Raw data ──────────────────────────────────────────────────────────────
    page_text  = clean_text(soup)
    word_list  = re.findall(r'\b[a-zA-Z]{2,}\b', page_text.lower())
    word_count = len(word_list)

    # Title & Meta
    title_tag   = soup.find("title")
    title_text  = title_tag.get_text(strip=True) if title_tag else ""
    meta_desc   = ""
    meta_kw     = ""
    canonical   = ""
    robots_meta = ""
    lang        = soup.find("html").get("lang", "") if soup.find("html") else ""
    viewport    = ""
    charset     = ""

    for meta in soup.find_all("meta"):
        name    = (meta.get("name") or "").lower()
        prop    = (meta.get("property") or "").lower()
        content = meta.get("content", "")
        if name == "description":              meta_desc   = content
        if name == "keywords":                 meta_kw     = content
        if name == "robots":                   robots_meta = content
        if name == "viewport":                 viewport    = content
        if meta.get("charset"):                charset     = meta.get("charset")
    link_can = soup.find("link", {"rel": "canonical"})
    if link_can: canonical = link_can.get("href", "")

    # Headings
    headings = {}
    all_headings_list = []
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        headings[f"h{level}"] = [t.get_text(strip=True) for t in tags]
        for t in tags:
            all_headings_list.append((f"h{level}", t.get_text(strip=True)))

    # Paragraphs
    paras = soup.find_all("p")
    para_count = len(paras)

    # Links
    all_links   = soup.find_all("a", href=True)
    int_links   = []
    ext_links   = []
    nofollow_c  = 0
    for a in all_links:
        href = a["href"].strip()
        anchor = a.get_text(strip=True)[:80]
        rel = a.get("rel", [])
        if "nofollow" in rel: nofollow_c += 1
        if href.startswith("http") and parsed.netloc not in href:
            ext_links.append((href, anchor))
        elif href and not href.startswith("javascript") and not href.startswith("mailto"):
            full = urllib.parse.urljoin(url, href)
            int_links.append((full, anchor))

    # Images
    img_data = analyse_images(soup, base_url)

    # Scripts & CSS
    scripts   = soup.find_all("script", src=True)
    stylesheets = soup.find_all("link", {"rel": "stylesheet"})

    # Social / Schema
    og_tags, tw_tags = analyse_social(soup)
    schema_types = analyse_schema(soup)

    # All meta tags list
    all_meta_list = []
    for m in soup.find_all("meta"):
        name = m.get("name") or m.get("property") or m.get("http-equiv") or ""
        content = m.get("content", "")[:120]
        if name:
            all_meta_list.append((name, content))

    # Slug
    slug, slug_score, slug_issues = slug_analysis(url)

    # robots.txt & sitemap
    has_robots, robots_content = check_robots(base_url)
    has_sitemap, sitemap_url   = check_sitemap(base_url)

    # Keyword frequency
    kw_freq = word_freq(page_text, 25)

    # ── SCORES ────────────────────────────────────────────────────────────────
    scores = {}

    # Title score
    ts = 0
    if title_text:
        ts += 30
        if 50 <= len(title_text) <= 60: ts += 30
        elif 40 <= len(title_text) <= 70: ts += 15
        if focus_kw and focus_kw in title_text.lower(): ts += 20
        if "|" in title_text or "-" in title_text: ts += 10
        if title_text[0].isupper(): ts += 10
    scores["title"] = min(100, ts)

    # Meta desc score
    ms = 0
    if meta_desc:
        ms += 30
        if 130 <= len(meta_desc) <= 160: ms += 35
        elif 100 <= len(meta_desc) <= 180: ms += 20
        if focus_kw and focus_kw in meta_desc.lower(): ms += 20
        if any(c in meta_desc for c in ["!", "?", ".", ","]): ms += 15
    scores["meta_desc"] = min(100, ms)

    # Content score
    cs = 0
    if word_count >= 300:  cs += 20
    if word_count >= 600:  cs += 15
    if word_count >= 1000: cs += 15
    if headings.get("h1"): cs += 15
    if len(headings.get("h2", [])) >= 2: cs += 10
    if len(headings.get("h3", [])) >= 2: cs += 5
    if para_count >= 5:    cs += 10
    if focus_kw:
        density = page_text.lower().count(focus_kw) / max(word_count, 1) * 100
        if 0.5 <= density <= 2.5: cs += 10
    scores["content"] = min(100, cs)

    # Technical score
    tech = 0
    if url.startswith("https"): tech += 20
    if canonical:                tech += 10
    if lang:                     tech += 10
    if viewport:                 tech += 10
    if charset:                  tech += 5
    if has_robots:               tech += 10
    if has_sitemap:              tech += 15
    if robots_meta.lower() != "noindex" and "noindex" not in robots_meta.lower(): tech += 10
    if img_data["missing_alt"] == 0: tech += 10
    scores["technical"] = min(100, tech)

    # Speed score (heuristic)
    sp = 0
    if load_ms < 500:   sp = 95
    elif load_ms < 1000: sp = 80
    elif load_ms < 2000: sp = 65
    elif load_ms < 3000: sp = 45
    elif load_ms < 5000: sp = 25
    else:               sp = 10
    if img_data["lazy_loaded"] > 0: sp = min(100, sp + 5)
    if len(scripts) < 10:           sp = min(100, sp + 5)
    scores["speed"] = sp

    # Keyword score
    ks = 0
    if focus_kw:
        kw_in_title   = focus_kw in title_text.lower()
        kw_in_desc    = focus_kw in meta_desc.lower()
        kw_in_h1      = any(focus_kw in h.lower() for h in headings.get("h1", []))
        kw_in_content = focus_kw in page_text.lower()
        kw_in_url     = focus_kw.replace(" ", "-") in url.lower() or focus_kw.replace(" ", "") in url.lower()
        count_in_page = page_text.lower().count(focus_kw)
        density       = count_in_page / max(word_count, 1) * 100
        if kw_in_title:   ks += 25
        if kw_in_desc:    ks += 20
        if kw_in_h1:      ks += 20
        if kw_in_content: ks += 15
        if kw_in_url:     ks += 10
        if 0.5 <= density <= 2.5: ks += 10
    else:
        ks = 50  # neutral when no focus keyword
    scores["keyword"] = min(100, ks)

    # Social score
    soc = 0
    if og_tags.get("og:title"):       soc += 20
    if og_tags.get("og:description"): soc += 20
    if og_tags.get("og:image"):       soc += 20
    if tw_tags.get("twitter:card"):   soc += 20
    if tw_tags.get("twitter:title"):  soc += 10
    if tw_tags.get("twitter:image"):  soc += 10
    scores["social"] = min(100, soc)

    # Overall page score
    weights = {"title": .18, "meta_desc": .12, "content": .22, "technical": .20,
               "speed": .15, "keyword": .08, "social": .05}
    page_score = round(sum(scores[k] * w for k, w in weights.items()))
    scores["overall"] = page_score

    # Readability
    try:
        flesch = round(textstat.flesch_reading_ease(page_text))
        grade  = textstat.text_standard(page_text, float_output=False)
    except:
        flesch, grade = 0, "N/A"

    # ── YOAST-STYLE CHECKS ───────────────────────────────────────────────────
    def yoast_checks():
        checks = []
        def add(status, text):
            checks.append((status, text))

        # Title
        if not title_text:         add("red",    "Page title is missing")
        elif len(title_text) < 30: add("yellow", f"Title is short ({len(title_text)} chars) – aim for 50–60")
        elif len(title_text) > 70: add("yellow", f"Title is too long ({len(title_text)} chars) – aim for 50–60")
        else:                      add("green",  f"Title length is good ({len(title_text)} chars)")

        if focus_kw:
            if focus_kw in title_text.lower(): add("green",  "Focus keyword appears in title")
            else:                              add("red",    "Focus keyword NOT found in title")

        # Meta desc
        if not meta_desc:            add("red",    "Meta description is missing")
        elif len(meta_desc) < 100:   add("yellow", f"Meta description is short ({len(meta_desc)} chars)")
        elif len(meta_desc) > 165:   add("yellow", f"Meta description is too long ({len(meta_desc)} chars)")
        else:                        add("green",  f"Meta description length is good ({len(meta_desc)} chars)")

        if focus_kw and meta_desc:
            if focus_kw in meta_desc.lower(): add("green", "Focus keyword in meta description")
            else:                             add("yellow","Focus keyword not in meta description")

        # H1
        h1s = headings.get("h1", [])
        if not h1s:            add("red",    "No H1 heading found")
        elif len(h1s) > 1:     add("yellow", f"Multiple H1 tags found ({len(h1s)}) – use only one")
        else:                  add("green",  "Exactly one H1 tag – perfect")

        if focus_kw and h1s:
            if any(focus_kw in h.lower() for h in h1s): add("green",  "Focus keyword appears in H1")
            else:                                        add("yellow", "Focus keyword not in H1")

        # Content
        if word_count < 300:   add("red",    f"Content is thin ({word_count} words) – aim for 600+")
        elif word_count < 600: add("yellow", f"Content could be longer ({word_count} words)")
        else:                  add("green",  f"Good content length ({word_count} words)")

        # Keyword density
        if focus_kw:
            count_kw = page_text.lower().count(focus_kw)
            density  = count_kw / max(word_count, 1) * 100
            if density < 0.5:    add("yellow", f"Keyword density is low ({density:.2f}%) – aim for 0.5–2.5%")
            elif density > 3.0:  add("red",    f"Keyword density is high ({density:.2f}%) – possible stuffing")
            else:                add("green",  f"Keyword density is good ({density:.2f}%)")

        # HTTPS
        if url.startswith("https"): add("green", "Page uses HTTPS (secure)")
        else:                       add("red",   "Page does NOT use HTTPS")

        # Canonical
        if canonical: add("green",  f"Canonical URL is set")
        else:         add("yellow", "No canonical URL found")

        # Images alt
        if img_data["missing_alt"] == 0: add("green",  "All images have alt attributes")
        elif img_data["missing_alt"] < 3: add("yellow", f"{img_data['missing_alt']} image(s) missing alt text")
        else:                            add("red",    f"{img_data['missing_alt']} images missing alt text")

        # Robots / indexing
        if "noindex" in robots_meta.lower(): add("red",   "Page has noindex directive – won't be indexed!")
        else:                                add("green", "Page is indexable (no noindex found)")

        # Sitemap
        if has_sitemap: add("green",  f"Sitemap found")
        else:           add("yellow", "No sitemap.xml detected")

        # Robots.txt
        if has_robots: add("green",  "robots.txt is accessible")
        else:          add("yellow", "robots.txt not found or inaccessible")

        # Internal links
        if len(int_links) >= 3: add("green",  f"{len(int_links)} internal links found")
        elif len(int_links) > 0: add("yellow", f"Only {len(int_links)} internal links – add more")
        else:                   add("red",    "No internal links detected")

        # Structured data
        if schema_types: add("green",  f"Structured data (Schema.org) found: {', '.join(schema_types)}")
        else:            add("yellow", "No structured data (Schema.org/JSON-LD) found")

        # OG tags
        if og_tags.get("og:title"): add("green",  "Open Graph tags present")
        else:                       add("yellow", "Open Graph (og:) tags missing")

        # Lang
        if lang: add("green",  f"HTML lang attribute set: '{lang}'")
        else:    add("yellow", "HTML lang attribute is missing")

        # Viewport
        if viewport: add("green",  "Viewport meta tag present (mobile-friendly)")
        else:        add("red",    "Viewport meta tag missing – not mobile-friendly")

        # Load time
        if load_ms < 1000: add("green",  f"Page loaded in {load_ms}ms – excellent")
        elif load_ms < 3000: add("yellow", f"Page loaded in {load_ms}ms – could be faster")
        else:              add("red",    f"Page loaded in {load_ms}ms – too slow")

        # H2 subheadings
        if len(headings.get("h2", [])) >= 2: add("green",  f"{len(headings['h2'])} H2 subheadings found – good structure")
        else:                                add("yellow", f"Only {len(headings.get('h2',[]))} H2 – add more subheadings")

        return checks

    checks = yoast_checks()

    # ═══════════════════════════════════════════════════════════════════════
    #  RENDER UI
    # ═══════════════════════════════════════════════════════════════════════

    # Hero
    st.markdown(f"""
    <div class="hero-header">
        <h1>🔍 SEO Analysis Report</h1>
        <p><span class="brand">{url}</span> &nbsp;·&nbsp; Analysed at {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Top Score Row ──────────────────────────────────────────────────────
    sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns(7)
    def render_score(col, label, val):
        col.markdown(f"""
        <div class="score-card">
            <div class="score-num {score_color(val)}">{val}</div>
            <div class="score-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    render_score(sc1, "Overall",   scores["overall"])
    render_score(sc2, "Content",   scores["content"])
    render_score(sc3, "Technical", scores["technical"])
    render_score(sc4, "Title",     scores["title"])
    render_score(sc5, "Meta Desc", scores["meta_desc"])
    render_score(sc6, "Speed",     scores["speed"])
    render_score(sc7, "Social",    scores["social"])

    # ── Two columns layout ────────────────────────────────────────────────
    left, right = st.columns([1.1, 1], gap="large")

    # ────────────────────── LEFT COLUMN ──────────────────────────────────
    with left:

        # ── Basic SEO ────────────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Basic SEO Elements</div>', unsafe_allow_html=True)

        rows = [
            ("Page Title", f'{title_text[:80] or "<em>Missing</em>"} {badge(f"{len(title_text)} chars", "info" if 50<=len(title_text)<=60 else "warn")}'),
            ("Title Length", f'{len(title_text)} chars {"✅" if 50<=len(title_text)<=60 else "⚠️"}'),
            ("Meta Description", (meta_desc[:120] + "…" if len(meta_desc) > 120 else meta_desc) or "<em>Missing</em>"),
            ("Meta Desc Length", f'{len(meta_desc)} chars {"✅" if 130<=len(meta_desc)<=160 else "⚠️"}'),
            ("Focus Keyword", focus_kw or "<em>Not set</em>"),
            ("Canonical URL", canonical or "<em>Not set</em>"),
            ("Meta Keywords", meta_kw[:100] or "<em>None</em>"),
            ("Robots Meta",  robots_meta or "index, follow (default)"),
            ("HTML Lang",    lang or "<em>Not set</em>"),
            ("Viewport",     "✅ Present" if viewport else "❌ Missing"),
            ("Charset",      charset or "<em>Not detected</em>"),
            ("HTTP Status",  f'{resp.status_code} {"✅" if resp.status_code == 200 else "⚠️"}' if resp else "N/A"),
            ("HTTPS",        "✅ Secure" if url.startswith("https") else "❌ Not secure"),
            ("Load Time",    f'{load_ms} ms {"🟢" if load_ms<1000 else "🟡" if load_ms<3000 else "🔴"}'),
        ]
        for name, val in rows:
            st.markdown(f'<div class="metric-row"><span class="metric-name">{name}</span><span class="metric-value">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Content Analysis ─────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📝 Content Analysis</div>', unsafe_allow_html=True)

        content_rows = [
            ("Total Word Count",     str(word_count)),
            ("Paragraph Count",      str(para_count)),
            ("H1 Tags",              str(len(headings.get("h1",[])))),
            ("H2 Tags",              str(len(headings.get("h2",[])))),
            ("H3 Tags",              str(len(headings.get("h3",[])))),
            ("H4 Tags",              str(len(headings.get("h4",[])))),
            ("H5 Tags",              str(len(headings.get("h5",[])))),
            ("H6 Tags",              str(len(headings.get("h6",[])))),
            ("Total Headings",       str(len(all_headings_list))),
            ("Total Images",         str(img_data["total"])),
            ("Images Missing Alt",   f'{img_data["missing_alt"]} {"✅" if img_data["missing_alt"]==0 else "❌"}'),
            ("Lazy-Loaded Images",   str(img_data["lazy_loaded"])),
            ("Non-NextGen Images",   str(img_data["non_next_gen"])),
            ("Internal Links",       str(len(int_links))),
            ("External Links",       str(len(ext_links))),
            ("Nofollow Links",       str(nofollow_c)),
            ("JS Files",             str(len(scripts))),
            ("CSS Stylesheets",      str(len(stylesheets))),
            ("Flesch Reading Ease",  str(flesch)),
            ("Reading Grade Level",  grade),
            ("Structured Data",      ", ".join(schema_types) if schema_types else "None"),
        ]
        for name, val in content_rows:
            st.markdown(f'<div class="metric-row"><span class="metric-name">{name}</span><span class="metric-value">{val}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── URL Slug Efficiency ───────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔗 URL & Slug Efficiency</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row"><span class="metric-name">Full URL</span><span class="metric-value" style="color:#60a5fa">{url[:80]}</span></div>
        <div class="metric-row"><span class="metric-name">Slug</span><span class="metric-value">{slug}</span></div>
        <div class="metric-row"><span class="metric-name">Slug Score</span><span class="metric-value {score_color(slug_score)}">{slug_score}/100</span></div>
        <div class="metric-row"><span class="metric-name">URL Path Depth</span><span class="metric-value">{len([p for p in parsed.path.split('/') if p])} levels</span></div>
        <div class="metric-row"><span class="metric-name">Query Params</span><span class="metric-value">{"✅ None" if not parsed.query else f"⚠️ {parsed.query[:60]}"}</span></div>
        """, unsafe_allow_html=True)
        if slug_issues:
            for iss in slug_issues:
                st.markdown(f'<div class="insight-box insight-warning">⚠️ {iss}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box insight-success">✅ Slug looks clean and SEO-friendly</div>', unsafe_allow_html=True)
        st.markdown(progress_bar(slug_score, 100, "#3b82f6"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ────────────────────── RIGHT COLUMN ─────────────────────────────────
    with right:

        # ── Yoast-Style Checklist ─────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✅ SEO Checklist (Yoast-style)</div>', unsafe_allow_html=True)
        green_c = sum(1 for s, _ in checks if s == "green")
        yellow_c = sum(1 for s, _ in checks if s == "yellow")
        red_c    = sum(1 for s, _ in checks if s == "red")
        st.markdown(f"""
        <div style="display:flex;gap:16px;margin-bottom:12px">
          <span style="color:#22c55e;font-size:.85rem;font-weight:600">✅ {green_c} passed</span>
          <span style="color:#f59e0b;font-size:.85rem;font-weight:600">⚠️ {yellow_c} warnings</span>
          <span style="color:#ef4444;font-size:.85rem;font-weight:600">❌ {red_c} issues</span>
        </div>
        """, unsafe_allow_html=True)
        for status, text in checks:
            dot_cls = {"green": "dot-green", "yellow": "dot-yellow", "red": "dot-red"}.get(status, "dot-grey")
            st.markdown(f'<div class="check-item"><div class="check-dot {dot_cls}"></div><div class="check-text">{text}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Keyword Analysis ──────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Keyword Analysis</div>', unsafe_allow_html=True)
        if focus_kw:
            count_kw  = page_text.lower().count(focus_kw)
            density   = count_kw / max(word_count, 1) * 100
            kw_in_title   = focus_kw in title_text.lower()
            kw_in_desc    = focus_kw in meta_desc.lower()
            kw_in_h1      = any(focus_kw in h.lower() for h in headings.get("h1", []))
            kw_in_url     = focus_kw.replace(" ", "-") in url.lower()
            st.markdown(f"""
            <div class="metric-row"><span class="metric-name">Focus Keyword</span><span class="metric-value" style="color:#38bdf8">{focus_kw}</span></div>
            <div class="metric-row"><span class="metric-name">Occurrences in Page</span><span class="metric-value">{count_kw}</span></div>
            <div class="metric-row"><span class="metric-name">Keyword Density</span><span class="metric-value">{density:.2f}% {"✅" if .5<=density<=2.5 else "⚠️"}</span></div>
            <div class="metric-row"><span class="metric-name">In Title</span><span class="metric-value">{"✅ Yes" if kw_in_title else "❌ No"}</span></div>
            <div class="metric-row"><span class="metric-name">In Meta Description</span><span class="metric-value">{"✅ Yes" if kw_in_desc else "❌ No"}</span></div>
            <div class="metric-row"><span class="metric-name">In H1</span><span class="metric-value">{"✅ Yes" if kw_in_h1 else "❌ No"}</span></div>
            <div class="metric-row"><span class="metric-name">In URL</span><span class="metric-value">{"✅ Yes" if kw_in_url else "❌ No"}</span></div>
            <div class="metric-row"><span class="metric-name">Keyword Score</span><span class="metric-value {score_color(scores['keyword'])}">{scores['keyword']}/100</span></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box insight-info">ℹ️ Enter a focus keyword in the sidebar for keyword-specific analysis</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top:12px;font-size:.85rem;color:#94a3b8;font-weight:600;margin-bottom:8px">TOP KEYWORDS ON PAGE</div>', unsafe_allow_html=True)
        max_freq = kw_freq[0][1] if kw_freq else 1
        for word, cnt in kw_freq[:15]:
            pct = round(cnt / max_freq * 100)
            st.markdown(f"""
            <div class="kw-row">
              <span class="kw-word">{word}</span>
              <span class="kw-count">{cnt}×</span>
              <div class="kw-bar-wrap"><div class="kw-bar-fill" style="width:{pct}%"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Social / OG Tags ─────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">📣 Social & Open Graph &nbsp; {badge(str(scores["social"])+"/100", "info")}</div>', unsafe_allow_html=True)
        all_social = {**{k: v for k, v in og_tags.items()}, **{k: v for k, v in tw_tags.items()}}
        if all_social:
            for k, v in list(all_social.items())[:12]:
                st.markdown(f'<div class="metric-row"><span class="metric-name">{k}</span><span class="metric-value">{v[:80]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box insight-warning">⚠️ No Open Graph or Twitter Card tags found</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Full-width sections ────────────────────────────────────────────────

    # ── Headings Structure ────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏗️ Heading Structure</div>', unsafe_allow_html=True)

    tag_cols = st.columns(6)
    for i, level in enumerate(range(1, 7)):
        tag_cols[i].markdown(f'<div style="text-align:center"><span class="h{level}-tag">H{level}</span><div style="color:#e2e8f0;font-size:1.4rem;font-weight:700;margin-top:4px">{len(headings.get(f"h{level}",[]))}</div><div style="color:#64748b;font-size:.75rem">tags</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="scroll-area" style="margin-top:16px">', unsafe_allow_html=True)
    for tag, text in all_headings_list:
        st.markdown(f'<div class="heading-row"><span class="h{tag[1]}-tag">{tag.upper()}</span><span class="heading-text">{text[:120]}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Links ─────────────────────────────────────────────────────────────
    lcol, rcol = st.columns(2, gap="large")

    with lcol:
        st.markdown(f'<div class="section-card"><div class="section-title">🔁 Internal Links ({len(int_links)})</div>', unsafe_allow_html=True)
        st.markdown('<div class="scroll-area">', unsafe_allow_html=True)
        for href, anchor in int_links[:60]:
            st.markdown(f'<div class="link-pill"><span class="link-anchor">⬡ {anchor or "(no anchor)"}</span><br><span class="link-text">{href[:90]}</span></div>', unsafe_allow_html=True)
        if not int_links:
            st.markdown('<div class="insight-box insight-error">No internal links found</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with rcol:
        st.markdown(f'<div class="section-card"><div class="section-title">🌐 External Links ({len(ext_links)})</div>', unsafe_allow_html=True)
        st.markdown('<div class="scroll-area">', unsafe_allow_html=True)
        for href, anchor in ext_links[:60]:
            st.markdown(f'<div class="link-pill"><span class="link-anchor">↗ {anchor or "(no anchor)"}</span><br><span class="link-text">{href[:90]}</span></div>', unsafe_allow_html=True)
        if not ext_links:
            st.markdown('<div class="insight-box insight-info">No external links found</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Meta Tags Full List ────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🏷️ All Meta Tags ({len(all_meta_list)})</div>', unsafe_allow_html=True)
    tag_html = "".join(f'<span class="tag-chip">{n}</span>' for n, _ in all_meta_list)
    st.markdown(f'<div style="margin-bottom:16px">{tag_html}</div>', unsafe_allow_html=True)
    st.markdown('<div class="scroll-area">', unsafe_allow_html=True)
    for name, content in all_meta_list:
        st.markdown(f'<div class="metric-row"><span class="metric-name" style="min-width:180px">{name}</span><span class="metric-value">{content}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Schema / Robots / Sitemap ─────────────────────────────────────────
    t1, t2 = st.columns(2, gap="large")
    with t1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 Robots.txt & Sitemap</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row"><span class="metric-name">robots.txt</span><span class="metric-value">{"✅ Found" if has_robots else "❌ Not found"}</span></div>
        <div class="metric-row"><span class="metric-name">Sitemap</span><span class="metric-value">{"✅ " + sitemap_url if has_sitemap else "❌ Not found"}</span></div>
        """, unsafe_allow_html=True)
        if has_robots and robots_content:
            st.markdown('<div style="background:#131924;border-radius:8px;padding:12px;margin-top:10px;font-size:.78rem;color:#94a3b8;font-family:monospace;max-height:140px;overflow-y:auto">' + robots_content.replace("\n","<br>") + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📐 Structured Data (Schema.org)</div>', unsafe_allow_html=True)
        if schema_types:
            for s in schema_types:
                st.markdown(f'<div class="insight-box insight-success">✅ {s}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box insight-warning">⚠️ No JSON-LD structured data found. Consider adding Organization, WebSite, or JobPosting schema.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Page Speed Heuristics ─────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚡ Page Speed Insights (Heuristic)</div>', unsafe_allow_html=True)
    size_bytes = len(resp.content) if resp else 0
    size_kb    = round(size_bytes / 1024, 1)

    sp_rows = [
        ("Server Response Time",  f'{load_ms} ms {"🟢 Fast" if load_ms<800 else "🟡 Moderate" if load_ms<2500 else "🔴 Slow"}'),
        ("HTML Page Size",        f'{size_kb} KB {"✅" if size_kb < 100 else "⚠️ Large"}'),
        ("JavaScript Files",      f'{len(scripts)} {"✅" if len(scripts)<=8 else "⚠️ Many JS files"}'),
        ("CSS Stylesheets",       f'{len(stylesheets)} {"✅" if len(stylesheets)<=4 else "⚠️ Many CSS files"}'),
        ("Total Images",          str(img_data["total"])),
        ("Lazy Loaded Images",    f'{img_data["lazy_loaded"]} {"✅" if img_data["lazy_loaded"]>0 else "⚠️ None lazy-loaded"}'),
        ("Next-Gen Images",       f'{"⚠️ " + str(img_data["non_next_gen"]) + " non-webp/avif" if img_data["non_next_gen"] > 0 else "✅ All modern format"}'),
        ("Speed Score (est.)",    f'{scores["speed"]}/100'),
    ]
    sp1, sp2 = st.columns(2)
    half = len(sp_rows) // 2
    with sp1:
        for name, val in sp_rows[:half]:
            st.markdown(f'<div class="metric-row"><span class="metric-name">{name}</span><span class="metric-value">{val}</span></div>', unsafe_allow_html=True)
    with sp2:
        for name, val in sp_rows[half:]:
            st.markdown(f'<div class="metric-row"><span class="metric-name">{name}</span><span class="metric-value">{val}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Final Summary Insights ─────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💡 Priority Recommendations</div>', unsafe_allow_html=True)
    recs = []
    if not title_text:           recs.append(("error",   "Add a page title immediately"))
    elif len(title_text) > 70:   recs.append(("warning", f"Shorten your title to under 60 chars (currently {len(title_text)})"))
    if not meta_desc:            recs.append(("error",   "Add a meta description (130–160 chars) to improve CTR"))
    if not canonical:            recs.append(("warning", "Set a canonical URL to avoid duplicate content issues"))
    if img_data["missing_alt"] > 0: recs.append(("warning", f"Add alt text to {img_data['missing_alt']} image(s) for accessibility & SEO"))
    if not has_sitemap:          recs.append(("warning", "Create and submit a sitemap.xml to Google Search Console"))
    if not schema_types:         recs.append(("info",    "Add JSON-LD structured data (e.g. JobPosting, Organization, WebSite)"))
    if not og_tags.get("og:image"): recs.append(("warning", "Add og:image for better social media sharing"))
    if word_count < 600:         recs.append(("error",   f"Increase content length (currently {word_count} words, aim for 600+)"))
    if load_ms > 3000:           recs.append(("error",   f"Improve page speed (loaded in {load_ms}ms, aim for <1s)"))
    if len(int_links) < 3:       recs.append(("warning", "Add more internal links to improve crawlability"))
    if not lang:                 recs.append(("warning", "Set the HTML lang attribute (e.g. lang='en')"))
    if not recs:
        recs.append(("success", "🎉 Great job! No major SEO issues found."))
    for kind, msg in recs:
        css_kind = {"error": "insight-error", "warning": "insight-warning", "info": "insight-info", "success": "insight-success"}[kind]
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "success": "✅"}[kind]
        st.markdown(f'<div class="insight-box {css_kind}">{icon} {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR + MAIN
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
        <div style='font-size:2rem'>🔍</div>
        <div style='color:#e2e8f0;font-size:1.1rem;font-weight:700;margin-top:6px'>SEO Analyser</div>
        <div style='color:#64748b;font-size:.78rem;margin-top:2px'>Powered by BeautifulSoup</div>
    </div>
    <hr style='border-color:#2d3748;margin:12px 0'>
    """, unsafe_allow_html=True)

    url_input = st.text_input(
        "🌐 Page URL",
        value="https://hiring4jobs.com",
        placeholder="https://example.com",
    )
    focus_kw = st.text_input(
        "🎯 Focus Keyword (optional)",
        placeholder="e.g. jobs in chennai",
    )
    analyse_btn = st.button("🔍 Analyse Now")

    st.markdown("""
    <hr style='border-color:#2d3748;margin:16px 0'>
    <div style='color:#475569;font-size:.78rem;line-height:1.7'>
    <b style='color:#64748b'>What this checks:</b><br>
    ✅ Title & Meta description<br>
    ✅ Heading structure (H1–H6)<br>
    ✅ Keyword density & score<br>
    ✅ Internal & external links<br>
    ✅ Images & alt text<br>
    ✅ Schema / structured data<br>
    ✅ Open Graph & Twitter cards<br>
    ✅ robots.txt & sitemap<br>
    ✅ URL slug efficiency<br>
    ✅ Page speed heuristics<br>
    ✅ Readability score<br>
    ✅ Yoast-style checklist<br>
    ✅ All meta tags<br>
    ✅ Priority recommendations
    </div>
    <hr style='border-color:#2d3748;margin:16px 0'>
    <div style='color:#334155;font-size:.72rem;text-align:center'>No API keys · Free · No tracking</div>
    """, unsafe_allow_html=True)

# ── Welcome Screen ─────────────────────────────────────────────────────────────
if not analyse_btn:
    st.markdown("""
    <div class="hero-header" style="padding:60px 40px">
        <div style="font-size:3rem;margin-bottom:16px">🔍</div>
        <h1>SEO Analyser</h1>
        <p>Enter a URL in the sidebar and click <b style="color:#38bdf8">Analyse Now</b><br>
        to get a full Yoast-style SEO audit — free, no API key required.</p>
        <div style="margin-top:24px;display:flex;justify-content:center;gap:24px;flex-wrap:wrap">
            <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:14px 20px;min-width:140px;text-align:center">
                <div style="font-size:1.6rem">📊</div>
                <div style="color:#94a3b8;font-size:.82rem;margin-top:4px">25+ metrics</div>
            </div>
            <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:14px 20px;min-width:140px;text-align:center">
                <div style="font-size:1.6rem">✅</div>
                <div style="color:#94a3b8;font-size:.82rem;margin-top:4px">Yoast checklist</div>
            </div>
            <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:14px 20px;min-width:140px;text-align:center">
                <div style="font-size:1.6rem">🎯</div>
                <div style="color:#94a3b8;font-size:.82rem;margin-top:4px">Keyword analysis</div>
            </div>
            <div style="background:#1e2533;border:1px solid #2d3748;border-radius:10px;padding:14px 20px;min-width:140px;text-align:center">
                <div style="font-size:1.6rem">⚡</div>
                <div style="color:#94a3b8;font-size:.82rem;margin-top:4px">Speed insights</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    if url_input:
        raw = url_input.strip()
        if not raw.startswith("http"):
            raw = "https://" + raw
        full_analyse(raw, focus_kw)
    else:
        st.warning("Please enter a URL.")
