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
  header {
      background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
      color: white;
      padding: 3.5rem 1.5rem;
      text-align: center;
      position: relative;
      overflow: hidden;
      border-bottom: 4px solid #10b981;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
    }

    header::before {
      content: "";
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 60%);
      pointer-events: none;
    }

    .header-container {
      max-width: 1200px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }

    .brand-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.1);
      padding: 6px 16px;
      border-radius: 50px;
      font-size: 0.85rem;
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 12px;
      backdrop-filter: blur(5px);
      border: 1px solid rgba(255, 255, 255, 0.15);
    }

    header h1 {
      font-size: 2.8rem;
      font-weight: 800;
      letter-spacing: -1px;
      text-transform: uppercase;
      margin-bottom: 8px;
      background: linear-gradient(to right, #ffffff, #a7f3d0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    header p.subtitle {
      font-size: 1.1rem;
      opacity: 0.85;
      max-width: 600px;
      margin: 0 auto 12px auto;
      font-weight: 400;
    }

    header p.updated {
      font-size: 0.8rem;
      opacity: 0.6;
      background: rgba(0, 0, 0, 0.2);
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
    }
</style>
</head>
<body>
<header>
    <div class="header-container">
      <div class="brand-badge">
        <span>⚽</span> Portal Oficial de Notícias
      </div>
      <h1>Placar em Dia</h1>
      <p class="subtitle">Futebol, resultados em tempo real e as principais manchetes do mundo desportivo.</p>
      <p class="updated">Atualizado automaticamente em {now}</p>
    </div>
  </header>
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
