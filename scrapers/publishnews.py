# -*- coding: utf-8 -*-
"""Scraper for PublishNews — Weekly Nielsen bestseller rankings."""

import os
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .common import fetch_html, build_book_entry, save_json, generate_metadata

BASE_URL = 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/{cat_id}'

PUBLISHNEWS_WEEKLY_CATEGORIES = [
    {
        'id': '0',
        'key': 'semanal_0',
        'slug': 'geral',
        'label': 'General / Geral',
        'url': 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/0',
    },
    {
        'id': '7',
        'key': 'semanal_7',
        'slug': 'ficcao',
        'label': 'Fiction / Ficção',
        'url': 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/7',
    },
    {
        'id': '9',
        'key': 'semanal_9',
        'slug': 'nao_ficcao',
        'label': 'Trade Nonfiction / Não-ficção',
        'url': 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/9',
    },
    {
        'id': '8',
        'key': 'semanal_8',
        'slug': 'especialista',
        'label': 'Specialist Nonfiction / Não-ficção Especialista',
        'url': 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/8',
    },
    {
        'id': '10',
        'key': 'semanal_10',
        'slug': 'infantojuvenil',
        'label': 'Children and Young Adult / Infantojuvenil',
        'url': 'https://www.publishnews.com.br/ranking-nielsen.php/semanal/10',
    },
]

def parse_publishnews_row(row_elem, source_url, index):
    """Parse a single pn-ranking-livros-posicao row."""
    # Rank
    rank_elem = row_elem.select_one('.pn-ranking-livros-posicao-numero')
    rank_text = rank_elem.get_text(strip=True) if rank_elem else str(index)
    try:
        rank = int(re.sub(r'[^\d]', '', rank_text) or index)
    except Exception:
        rank = index

    # Title
    title_elem = row_elem.select_one('.pn-ranking-livro-nome')
    title = title_elem.get_text(strip=True) if title_elem else ''
    if not title:
        return None

    # Author
    author_elem = row_elem.select_one('.pn-ranking-livro-autor')
    author = author_elem.get_text(strip=True) if author_elem else '—'

    # Publisher
    pub_elem = row_elem.select_one('.pn-ranking-livro-editora')
    publisher = pub_elem.get_text(strip=True) if pub_elem else ''

    # Sales volume
    volume_elem = row_elem.select_one('.pn-ranking-livros-posicao-volume')
    sales = volume_elem.get_text(strip=True) if volume_elem else ''

    # Cover URL
    img_elem = row_elem.select_one('img')
    cover_url = ''
    if img_elem and img_elem.get('src'):
        cover_url = urljoin('https://www.publishnews.com.br/', img_elem['src'].strip())

    # Extras: Blurb, ISBN, Pages, Category
    blurb = ''
    isbn = ''
    pages = ''
    category = ''

    resumo_elem = row_elem.select_one('.pn-ranking-livro-resumo')
    if resumo_elem:
        blurb = resumo_elem.get_text(strip=True)

    isbn_elem = row_elem.select_one('.pn-ranking-livro-isbn')
    if isbn_elem:
        isbn_raw = isbn_elem.get_text(strip=True)
        # Clean 'ISBN  978-85-01117-84-7'
        isbn_match = re.search(r'[\d\-]{10,20}', isbn_raw)
        isbn = isbn_match.group(0).replace('-', '') if isbn_match else isbn_raw.replace('ISBN', '').strip()

    paginas_elem = row_elem.select_one('.pn-ranking-livro-paginas')
    if paginas_elem:
        pages_raw = paginas_elem.get_text(strip=True)
        pages_match = re.search(r'\d+', pages_raw)
        pages = pages_match.group(0) if pages_match else ''

    cat_elem = row_elem.select_one('.pn-ranking-livro-categoria')
    if cat_elem:
        category = cat_elem.get_text(strip=True).replace('Categoria', '').strip()

    return build_book_entry(
        rank=rank,
        title=title,
        author=author,
        authors=author,
        publisher=publisher,
        cover_url=cover_url,
        source_url=source_url,
        description=blurb,
        summary=blurb,
        blurb=blurb,
        isbn=isbn,
        isbn13=isbn,
        pages=pages,
        sales=sales,
        category=category,
    )

def scrape_category(cat_info):
    """Scrape a single PublishNews category."""
    url = cat_info['url']
    headers = {
        'Referer': 'https://www.publishnews.com.br/ranking',
    }
    html = fetch_html(url, headers=headers)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('.pn-ranking-livros-posicao')
    books = []
    for idx, row in enumerate(rows, start=1):
        item = parse_publishnews_row(row, url, idx)
        if item:
            books.append(item)
    return books

def run_publishnews_scraper(output_dir):
    """Run full PublishNews weekly scraper and save JSON files."""
    pn_dir = os.path.join(output_dir, 'publishnews')
    os.makedirs(pn_dir, exist_ok=True)

    results_by_cat = {}
    print('Starting PublishNews Weekly scraper...')

    for cat in PUBLISHNEWS_WEEKLY_CATEGORIES:
        key = cat['key']
        print(f"  Fetching: {cat['label']} ({cat['url']})...")
        try:
            books = scrape_category(cat)
            results_by_cat[key] = books
            out_file = os.path.join(pn_dir, f"{key}.json")
            save_json(out_file, books)
            print(f"    Saved {len(books)} books -> {out_file}")
        except Exception as e:
            print(f"    Failed {key}: {e}")
            results_by_cat[key] = []

    # Write metadata
    meta = generate_metadata(
        source_name='PublishNews — Weekly',
        items_by_category=results_by_cat,
        extra_info={
            'cadence': 'weekly',
            'categories_info': PUBLISHNEWS_WEEKLY_CATEGORIES,
        }
    )
    meta_file = os.path.join(pn_dir, 'meta.json')
    save_json(meta_file, meta)
    print(f"  Saved metadata -> {meta_file}")

    return results_by_cat
