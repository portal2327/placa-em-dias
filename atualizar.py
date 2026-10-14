#!/usr/bin/env python3
'''Portal de notícias esportivas: uma publicação por execução, até cinco por dia.'''
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import hashlib, html, json, os, re, xml.etree.ElementTree as ET

TZ = ZoneInfo("America/Sao_Paulo")
FEEDS = [
    ("Futebol brasileiro", "futebol Brasileirão Série A Série B"),
    ("Libertadores e futebol internacional", "Libertadores Champions League futebol"),
    ("Seleção brasileira", "Seleção Brasileira futebol"),
    ("Outros esportes", "esportes Brasil basquete vôlei Fórmula 1"),
    ("Mercado da bola", "mercado da bola transferências futebol"),
]
def now_local(): return datetime.now(TZ)
def esc(x): return html.escape(str(x or ""), quote=True)
def norm(title):
    title = re.sub(r"\\s+[|–—-]\\s+[^|–—-]{2,80}$", "", title.strip()).casefold()
    return re.sub(r"\\s+", " ", re.sub(r"[^\\w\\s]", " ", title, flags=re.UNICODE)).strip()
def parse_date(raw):
    try:
        dt = parsedate_to_datetime(raw)
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except Exception: return None
def make_id(title, link):
    return hashlib.sha256((norm(title) + "|" + link.split("#")[0].rstrip("/")).encode()).hexdigest()[:16]
def slug(title, ident):
    text = re.sub(r"[^\\w\\s-]", "", title.lower(), flags=re.UNICODE)
    text = re.sub(r"[\\s_-]+", "-", text).strip("-")[:60].strip("-")
    return (text or "noticia") + "-" + ident[:8]
def load_state():
    try:
        with open("state.json", encoding="utf-8") as f: data = json.load(f)
        data.setdefault("published", []); data.setdefault("pending", [])
        return data
    except Exception: return {"published": [], "pending": []}
def save_state(state):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
def fetch(category, query):
    url = "https://news.google.com/rss/search?q=" + quote(query) + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    req = Request(url, headers={"User-Agent": "PlacarEmDia/2.0 RSS reader"})
    with urlopen(req, timeout=20) as res: root = ET.fromstring(res.read())
    out, cutoff = [], datetime.now(timezone.utc) - timedelta(hours=72)
    for node in root.findall(".//item")[:15]:
        t, l, d, s = (node.find(k) for k in ("title", "link", "pubDate", "source"))
        title = (t.text or "").strip() if t is not None else ""
        link = (l.text or "").strip() if l is not None else ""
        published = parse_date((d.text or "").strip()) if d is not None else None
        source = (s.text or "").strip() if s is not None else ""
        if not title or not link.startswith("https://") or (published and published < cutoff): continue
        source = source or urlparse(link).netloc.removeprefix("www.")
        ident = make_id(title, link)
        out.append({"id":ident, "key":norm(title), "slug":slug(title, ident), "title":title,
                    "link":link, "source":source or "Fonte original", "category":category,
                    "source_date":published.isoformat() if published else None})
    return out
def collect(state):
    ids = {x.get("id") for x in state["published"] + state["pending"]}
    keys = {x.get("key") for x in state["published"] + state["pending"]}
    errors = []
    for category, query in FEEDS:
        try: items = fetch(category, query)
        except Exception as e:
            print("[AVISO]", category, type(e).__name__); errors.append(category); continue
        for item in items:
            if item["id"] not in ids and item["key"] and item["key"] not in keys:
                state["pending"].append(item); ids.add(item["id"]); keys.add(item["key"])
    state["pending"].sort(key=lambda x: x.get("source_date") or "", reverse=True)
    state["pending"] = state["pending"][:100]
    return errors
def publish_one(state):
    today = now_local().date().isoformat()
    if sum(x.get("published_day") == today for x in state["published"]) >= 5:
        print("Limite de cinco notícias por dia atingido."); return False
    if not state["pending"]:
        print("Nenhuma novidade disponível nesta execução."); return False
    item = state["pending"].pop(0)
    item["published_at"] = now_local().isoformat(); item["published_day"] = today
    state["published"].append(item); print("Publicada:", item["title"]); return True
def date_text(item):
    try: return datetime.fromisoformat(item["published_at"]).astimezone(TZ).strftime("%d/%m/%Y às %H:%M")
    except Exception: return "Data não informada"
def article_page(item, all_items):
    title, source, category, link = map(esc, (item["title"], item["source"], item["category"], item["link"]))
    related = "".join(f'<li><a href="../noticias/{esc(x["slug"])}.html">{esc(x["title"])}</a></li>'
                      for x in all_items[:8] if x["id"] != item["id"])
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{title} — manchete esportiva com link para a fonte original."><title>{title} | Placar em Dia</title>
<style>body{{margin:0;background:#f3f5f7;color:#17212b;font:16px/1.65 system-ui,sans-serif}}header{{background:#082f26;padding:22px}}header a{{color:white;text-decoration:none;font-weight:900;font-size:22px}}main{{max-width:780px;margin:30px auto;padding:0 18px}}article,.related{{background:white;border:1px solid #e1e7eb;border-radius:14px;padding:24px}}.meta{{color:#64748b;font-size:14px}}h1{{font-size:clamp(27px,5vw,40px);line-height:1.2}}.button{{display:inline-block;background:#087f5b;color:white;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:700}}footer{{max-width:780px;margin:auto;padding:20px 18px 40px;color:#64748b;font-size:13px}}a{{color:#08634c}}</style></head>
<body><header><a href="../index.html">⚽ PLACAR EM DIA</a></header><main><article><p class="meta">{category} · {esc(date_text(item))}</p><h1>{title}</h1>
<p>Esta página organiza a manchete e direciona você à publicação original. Para ler a reportagem completa e verificar o contexto, acesse a fonte indicada.</p>
<p><strong>Fonte:</strong> {source}</p><p><a class="button" href="{link}" target="_blank" rel="noopener noreferrer">Ler na fonte original ↗</a></p>
<p class="meta">Portal independente, sem afiliação a clubes, ligas ou veículos de imprensa.</p></article>
<section class="related"><h2>Mais notícias</h2><ul>{related or "<li>Confira as manchetes na página inicial.</li>"}</ul><p><a href="../index.html">← Voltar ao início</a></p></section></main>
<footer>Placar em Dia · <a href="../sobre.html">Sobre e contato</a> · <a href="../privacidade.html">Privacidade</a></footer></body></html>'''
def index_page(published, errors):
    current = sorted(published, key=lambda x: x.get("published_at", ""), reverse=True)
    today = now_local().date().isoformat()
    count = sum(x.get("published_day") == today for x in current)
    cards = []
    for x in current[:50]:
        cards.append(f'''<article class="card"><p class="meta">{esc(x["category"])} · {esc(date_text(x))}</p>
<h2><a href="noticias/{esc(x["slug"])}.html">{esc(x["title"])}</a></h2><p class="source">Fonte: {esc(x["source"])}</p>
<a class="read" href="noticias/{esc(x["slug"])}.html">Abrir notícia →</a></article>''')
    if not cards: cards = ['<p>A primeira execução automática vai buscar as manchetes e preencher esta página.</p>']
    warning = '<p class="notice">Algumas fontes não responderam; as notícias disponíveis foram mantidas.</p>' if errors else ""
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Manchetes de futebol e esportes com links para fontes originais."><title>Placar em Dia | Futebol e Esportes</title>
<style>:root{{--bg:#f3f5f7;--card:#fff;--ink:#15202b;--muted:#637083;--green:#087f5b;--line:#e2e8ee}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{background:#082f26;color:white;padding:34px 18px}}.wrap{{max-width:1080px;margin:auto;padding:0 18px}}.brand{{font-weight:900;letter-spacing:-1px;font-size:clamp(30px,5vw,46px);margin:0}}header p{{color:#d4f5e8;margin:8px 0 0}}.updated{{font-size:13px;color:#c4e8dc;margin-top:16px}}main{{padding:24px 0 48px}}.summary{{background:white;border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin-bottom:22px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:14px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 3px 12px #14202b08}}.meta,.source{{color:var(--muted);font-size:13px}}h2{{font-size:19px;line-height:1.35;margin:0 0 12px}}h2 a{{color:#075e49;text-decoration:none}}.read{{font-weight:700;font-size:14px;color:#075e49;text-decoration:none}}.notice{{background:#fff7db;padding:12px;border-radius:8px}}footer{{border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:13px}}footer a{{color:inherit}}.disclaimer{{font-size:13px;color:var(--muted);margin-top:24px}}</style></head>
<body><header><div class="wrap"><p class="brand">⚽ PLACAR EM DIA</p><p>Futebol, resultados e notícias do mundo esportivo.</p><p class="updated">Atualizado: {esc(now_local().strftime("%d/%m/%Y às %H:%M"))}</p></div></header>
<main class="wrap">{warning}<div class="summary"><strong>Hoje:</strong> {count} de 5 notícias programadas publicadas.</div><div class="cards">{''.join(cards)}</div>
<p class="disclaimer">Portal independente que organiza manchetes e links para fontes originais. Não reproduz o texto completo das reportagens. O conteúdo automático pode conter erros ou atrasos; consulte a fonte original.</p></main>
<footer><div class="wrap">Placar em Dia · <a href="sobre.html">Sobre e contato</a> · <a href="privacidade.html">Privacidade</a></div></footer></body></html>'''
def main():
    os.makedirs("noticias", exist_ok=True)
    state = load_state()
    errors = collect(state)
    publish_one(state)
    published = sorted(state["published"], key=lambda x: x.get("published_at", ""), reverse=True)
    for item in published:
        with open(os.path.join("noticias", item["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(article_page(item, published))
    with open("index.html", "w", encoding="utf-8") as f: f.write(index_page(published, errors))
    save_state(state)
    print("Publicadas:", len(published), "| Na fila:", len(state["pending"]))
if __name__ == "__main__": main()
