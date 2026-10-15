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
    :root {
      --header-bg: #0b3c26;
      --bg-color: #f4f6f8;
      --card-bg: #ffffff;
      --text-main: #1e293b;
      --text-muted: #64748b;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-main);
      line-height: 1.5;
    }

    header {
      background: linear-gradient(135deg, #0f4c2e, #0b3c26);
      color: white;
      padding: 2.5rem 1.5rem;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .header-container {
      max-width: 1200px;
      margin: 0 auto;
    }

    header h1 {
      font-size: 2.2rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    main {
      max-width: 1200px;
      margin: 2rem auto;
      padding: 0 1.5rem;
    }

    .category-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--header-bg);
      margin-bottom: 1.5rem;
      border-left: 4px solid #2e7d32;
      padding-left: 12px;
    }

    .news-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .news-card {
      background: var(--card-bg);
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border: 1px solid #e2e8f0;
      box-shadow: 0 2px 4px rgba(0,0,0,0.02);
      transition: all 0.25s ease-in-out;
    }

    .news-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    }

    .news-link {
      display: inline-block;
      text-decoration: none;
      color: #1b5e20;
      font-size: 0.875rem;
      font-weight: 600;
      padding: 8px 14px;
      background-color: #e8f5e9;
      border-radius: 6px;
      margin-top: 12px;
    }

    .news-link:hover {
      background-color: #c8e6c9;
    }
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
