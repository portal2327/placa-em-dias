#!/usr/bin/env python3
"""Gera um portal estático com manchetes e links para as fontes originais."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import os
import re

# Fontes via Google News RSS: o portal mostra manchetes, fonte e links,
# sem copiar o texto integral dos artigos.
QUERIES = [
    ("Futebol brasileiro", "futebol Brasileirão"),
    ("Libertadores e futebol internacional", "Libertadores Champions League futebol"),
    ("Seleção brasileira", "Seleção Brasileira futebol"),
    ("Outros esportes", "Formula 1 basquete vôlei esporte Brasil"),
    ("Mercado da bola", "mercado da bola transferências futebol"),
]
MAX_POR_CATEGORIA = 8
OUT = "index.html"

def get_text(parent, path):
    el = parent.find(path)
    return (el.text or "").strip() if el is not None else ""

def parse_date(value):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def fetch_feed(label, query):
    url = "https://news.google.com/rss/search?q=" + quote(query) + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    req = Request(url, headers={"User-Agent": "PortalEsportivo/1.0 (RSS reader)"})
    with urlopen(req, timeout=20) as response:
        data = response.read()
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item")[:MAX_POR_CATEGORIA]:
        title = get_text(item, "title")
        link = get_text(item, "link")
        source = get_text(item, "source") or "Fonte original"
        pub = parse_date(get_text(item, "pubDate"))
        if not title or not link or not link.startswith("http"):
            continue
        items.append({
            "category": label,
            "title": title,
            "link": link,
            "source": source,
            "date": pub,
        })
    return items

def fmt_date(dt):
    if not dt:
        return "Data não informada"
    return dt.astimezone().strftime("%d/%m/%Y às %H:%M")

def build_page(items, errors):
    now = datetime.now().astimezone().strftime("%d/%m/%Y às %H:%M")
    grouped = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    sections = []
    for label, _ in QUERIES:
        cards = []
        for it in grouped.get(label, []):
            cards.append(f"""
            <article class="card">
              <p class="meta">{escape(it['category'])} · {escape(fmt_date(it['date']))}</p>
              <h3><a href="{escape(it['link'], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(it['title'])}</a></h3>
              <p class="source">Fonte: {escape(it['source'])}</p>
              <a class="read" href="{escape(it['link'], quote=True)}" target="_blank" rel="noopener noreferrer">Ler na fonte original ↗</a>
            </article>""")
        if cards:
            sections.append(f'<section><h2>{escape(label)}</h2><div class="cards">{"".join(cards)}</div></section>')

    if not sections:
        sections.append('<section><h2>Notícias</h2><p>Não foi possível carregar as manchetes nesta atualização. Tente novamente mais tarde.</p></section>')

    warning = ""
    if errors:
        warning = '<p class="notice">Algumas fontes não responderam nesta atualização. As notícias disponíveis foram mantidas.</p>'

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Portal independente com manchetes e links para notícias de futebol e outros esportes.">
<title>Placar em Dia | Futebol e Esportes</title>
<style>
:root{{--bg:#f3f5f7;--card:#fff;--ink:#15202b;--muted:#637083;--green:#087f5b;--line:#e2e8ee}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}
header{{background:#082f26;color:white;padding:34px 18px}} .wrap{{max-width:1080px;margin:auto;padding:0 18px}}
.brand{{font-weight:900;letter-spacing:-1px;font-size:clamp(30px,5vw,46px);margin:0}}
header p{{color:#d4f5e8;margin:8px 0 0}} .updated{{font-size:13px;color:#c4e8dc;margin-top:16px}}
main{{padding:24px 0 48px}} section{{margin:0 0 34px}} h2{{font-size:23px;margin:0 0 14px;border-left:5px solid var(--green);padding-left:11px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 3px 12px #14202b08}}
.meta,.source{{color:var(--muted);font-size:13px}} .meta{{margin:0 0 8px}} h3{{font-size:18px;line-height:1.35;margin:0 0 12px}}
a{{color:#075e49}} h3 a{{text-decoration:none}} h3 a:hover{{text-decoration:underline}}
.read{{font-weight:700;font-size:14px;text-decoration:none}} .notice{{background:#fff7db;padding:12px;border-radius:8px}}
footer{{border-top:1px solid var(--line);padding:22px 0;color:var(--muted);font-size:13px}}
footer a{{color:inherit}} .disclaimer{{font-size:13px;color:var(--muted);margin-top:20px}}
</style>
</head>
<body>
<header><div class="wrap">
<p class="brand">⚽ PLACAR EM DIA</p>
<p>Futebol, resultados e notícias do mundo esportivo.</p>
<p class="updated">Atualizado automaticamente: {escape(now)}</p>
</div></header>
<main class="wrap">
{warning}
{''.join(sections)}
<p class="disclaimer">Este portal reúne manchetes e links públicos para facilitar a descoberta de notícias. O conteúdo completo pertence às fontes originais. Confira a publicação de origem para contexto, correções e informações completas. Este é um projeto independente e não é afiliado a clubes, ligas ou veículos de imprensa.</p>
</main>
<footer><div class="wrap">Placar em Dia · <a href="sobre.html">Sobre e contato</a> · <a href="privacidade.html">Privacidade</a></div></footer>
</body></html>"""

def main():
    all_items, errors = [], []
    seen = set()
    for label, query in QUERIES:
        try:
            for item in fetch_feed(label, query):
                key = re.sub(r"\W+", "", item["title"].lower())
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
        except Exception as exc:
            errors.append(f"{label}: {exc}")
            print(f"[AVISO] {label}: {exc}")
    all_items.sort(key=lambda x: x["date"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build_page(all_items, errors))
    print(f"Página gerada com {len(all_items)} manchetes. Erros em {len(errors)} categoria(s).")

if __name__ == "__main__":
    main()
