# Best Sellers Cache

Unified static cache and scheduled mirror for high-demand bestseller lists, served over GitHub Pages.

Designed for high performance, low latency, and cross-platform consumption across:
- **Calibre Plugin**: [Best-Sellers](https://github.com/cm-fy/Best-Sellers)
- **Android App**: `best-sellers-android`
- External clients and web frontends

---

## 1. Endpoints

Once deployed on GitHub Pages (`https://cm-fy.github.io/best-sellers-cache/`), the static endpoints are:

### PublishNews — Weekly (Nielsen BookScan)
- **General / Geral**: [`/publishnews/semanal_0.json`](publishnews/semanal_0.json)
- **Fiction / Ficção**: [`/publishnews/semanal_7.json`](publishnews/semanal_7.json)
- **Trade Nonfiction / Não-ficção**: [`/publishnews/semanal_9.json`](publishnews/semanal_9.json)
- **Specialist Nonfiction / Não-ficção Especialista**: [`/publishnews/semanal_8.json`](publishnews/semanal_8.json)
- **Children & YA / Infantojuvenil**: [`/publishnews/semanal_10.json`](publishnews/semanal_10.json)
- **Metadata**: [`/publishnews/meta.json`](publishnews/meta.json)

---

## 2. Universal Schema

Every list item follows a dual-compatible schema satisfying Calibre and Android models:

```json
{
  "rank": 1,
  "rank_str": "1",
  "rankLastWeek": 0,
  "previous_rank": "",
  "weeksOnList": 0,
  "weeks_on_list": "",
  "title": "Verity",
  "author": "Colleen Hoover",
  "authors": "Colleen Hoover",
  "publisher": "Galera Record",
  "category": "Ficção",
  "description": "Full synopsis...",
  "summary": "Full synopsis...",
  "blurb": "Full synopsis...",
  "isbn": "9788501117847",
  "isbn13": "9788501117847",
  "pages": "320",
  "num_pages": "320",
  "cover_url": "https://www.publishnews.com.br/...",
  "coverImageUrl": "https://www.publishnews.com.br/...",
  "source_url": "https://www.publishnews.com.br/ranking-nielsen.php/semanal/0",
  "buyLinks": [],
  "sales": "8.502"
}
```

---

## 3. Adding New Sources

To add a new source:
1. Create a scraper module in `scrapers/<source_name>.py`.
2. Implement your fetch and parse logic, utilizing `build_book_entry` and `save_json` from `scrapers.common`.
3. Register the runner in `scrapers/__init__.py`.
4. Output JSON files into `<source_name>/`.
5. Update `.github/workflows/update-caches.yml` to track the new folder.

---

## 4. Local Execution

```bash
pip install -r requirements.txt
python run_scrapers.py --source publishnews
```
