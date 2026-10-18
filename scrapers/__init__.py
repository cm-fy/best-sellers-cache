# -*- coding: utf-8 -*-
"""Scrapers package for best-sellers-cache."""

from .publishnews import run_publishnews_scraper

SCRAPER_REGISTRY = {
    'publishnews': run_publishnews_scraper,
}
