# -*- coding: utf-8 -*-
"""Common utilities and unified schemas for best-sellers-cache."""

import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/128.0.0.0 Safari/537.36'
)

def make_ssl_context():
    """Create a permissive SSL context for scraper reliability."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_html(url, headers=None, timeout=30, retries=3, delay=1.5):
    """Fetch URL and return decoded UTF-8 string with retry logic."""
    hdrs = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    }
    if headers:
        hdrs.update(headers)

    ctx = make_ssl_context()
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                raw = resp.read()
                charset = resp.headers.get_content_charset() or 'utf-8'
                try:
                    return raw.decode(charset, errors='replace')
                except Exception:
                    return raw.decode('utf-8', errors='replace')
        except Exception as e:
            if attempt == retries:
                raise
            time.sleep(delay * attempt)
    return ''

def build_book_entry(
    rank,
    title,
    author='',
    authors='',
    publisher='',
    cover_url='',
    source_url='',
    description='',
    summary='',
    blurb='',
    isbn='',
    isbn13='',
    pages='',
    sales='',
    rank_last_week=0,
    weeks_on_list=0,
    category='',
    buy_links=None
):
    """Build a unified book entry compatible with Calibre plugin and Android app schemas.

    Calibre schema fields:
        rank (str), title, authors, publisher, cover_url, source_url, summary/blurb,
        previous_rank, weeks_on_list, isbn, isbn13, pages, sales.

    Android app schema fields (BookItem):
        rank (int), rankLastWeek (int), weeksOnList (int), title, author, description,
        publisher, isbn13, coverImageUrl, buyLinks.
    """
    try:
        rank_int = int(str(rank).strip() or 0)
    except Exception:
        rank_int = 0

    try:
        rank_last_week_int = int(str(rank_last_week).strip() or 0)
    except Exception:
        rank_last_week_int = 0

    try:
        weeks_on_list_int = int(str(weeks_on_list).strip() or 0)
    except Exception:
        weeks_on_list_int = 0

    author_clean = (author or authors or '—').strip()
    authors_clean = (authors or author or '—').strip()

    desc_clean = (description or summary or blurb or '').strip()

    isbn_clean = (isbn13 or isbn or '').strip()
    isbn13_clean = (isbn13 or isbn or '').strip()

    cover_clean = (cover_url or '').strip()

    return {
        # Ranking & Position (Dual typed for Calibre + Android)
        'rank': rank_int,
        'rank_str': str(rank_int) if rank_int else str(rank),
        'rankLastWeek': rank_last_week_int,
        'previous_rank': str(rank_last_week_int) if rank_last_week_int else '',
        'weeksOnList': weeks_on_list_int,
        'weeks_on_list': str(weeks_on_list_int) if weeks_on_list_int else '',

        # Bibliographic data
        'title': (title or '—').strip(),
        'author': author_clean,
        'authors': authors_clean,
        'publisher': (publisher or '').strip(),
        'category': (category or '').strip(),

        # Descriptions & Synopses
        'description': desc_clean,
        'summary': desc_clean,
        'blurb': desc_clean,

        # Identifiers & Physical Specs
        'isbn': isbn_clean,
        'isbn13': isbn13_clean,
        'pages': str(pages).strip() if pages else '',
        'num_pages': str(pages).strip() if pages else '',

        # Media & Links
        'cover_url': cover_clean,
        'coverImageUrl': cover_clean,
        'source_url': (source_url or '').strip(),
        'buyLinks': buy_links or [],

        # Extra metrics
        'sales': str(sales).strip() if sales else '',
    }

def save_json(file_path, data):
    """Save data as formatted JSON with atomic writing."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    temp_path = file_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if os.path.exists(file_path):
        os.remove(file_path)
    os.rename(temp_path, file_path)

def generate_metadata(source_name, items_by_category, extra_info=None):
    """Generate a standard meta.json payload for a source."""
    now = datetime.now(timezone.utc).isoformat()
    meta = {
        'source': source_name,
        'updated_at': now,
        'categories': {cat: len(items) for cat, items in items_by_category.items()},
        'total_books': sum(len(items) for items in items_by_category.items()),
    }
    if extra_info:
        meta.update(extra_info)
    return meta
