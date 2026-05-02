"""Crawl a website same-domain and save per-page markdown.

Sized from the BFS probe: typical content depth is shallow, but
pagination chains (/page/N/) extend BFS depth, so MAX_DEPTH is set
higher to let pagination resolve. Each crawled page is written as a
markdown file under output/<domain-slug>/ with an index.json
describing the run. Refuses to overwrite an existing output directory.

Usage: python crawl_site.py <url>
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, FilterChain, DomainFilter
from tqdm.asyncio import tqdm

MAX_DEPTH = 8
MAX_PAGES = 300
CONCURRENCY = 5

SCRIPT_DIR = Path(__file__).resolve().parent


def url_to_filename(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "index.md"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", path.replace("/", "__"))
    return f"{safe}.md"


def domain_to_slug(domain: str) -> str:
    return domain.replace(".", "-")


async def main(start_url: str):
    allowed_domain = urlparse(start_url).netloc
    if not allowed_domain:
        raise SystemExit(f"Could not parse domain from URL: {start_url}")

    output_dir = SCRIPT_DIR.parent / "output" / domain_to_slug(allowed_domain)
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    index_file = output_dir / "index.json"

    domain_filter = DomainFilter(allowed_domains=[allowed_domain], blocked_domains=[])
    strategy = BFSDeepCrawlStrategy(
        max_depth=MAX_DEPTH,
        filter_chain=FilterChain([domain_filter]),
        include_external=False,
        max_pages=MAX_PAGES,
    )

    run_config = CrawlerRunConfig(
        deep_crawl_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        stream=True,
        verbose=False,
        semaphore_count=CONCURRENCY,
    )
    browser_config = BrowserConfig(headless=True, verbose=False)

    print(f"Crawling {start_url} (max_depth={MAX_DEPTH}, max_pages={MAX_PAGES})...")
    index = []
    saved = 0
    failed = 0

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result_gen = await crawler.arun(url=start_url, config=run_config)
        progress = tqdm(total=MAX_PAGES, unit="page", dynamic_ncols=True)
        try:
            async for r in result_gen:
                depth = r.metadata.get("depth", 0) if r.metadata else 0
                if not r.success:
                    failed += 1
                    index.append({
                        "url": r.url,
                        "depth": depth,
                        "success": False,
                        "error": r.error_message,
                        "file": None,
                    })
                else:
                    markdown = r.markdown.raw_markdown if r.markdown else ""
                    filename = url_to_filename(r.url)
                    out_path = output_dir / filename
                    out_path.write_text(f"# {r.url}\n\n{markdown}\n", encoding="utf-8")
                    saved += 1
                    index.append({
                        "url": r.url,
                        "depth": depth,
                        "success": True,
                        "file": filename,
                        "title": (r.metadata or {}).get("title"),
                        "length": len(markdown),
                    })

                progress.set_postfix(saved=saved, failed=failed, depth=depth, refresh=False)
                progress.update(1)
        finally:
            progress.close()

    index_file.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Saved {saved} pages, {failed} failed -> {output_dir}")
    print(f"Index: {index_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python crawl_site.py <url>")
    asyncio.run(main(sys.argv[1]))
