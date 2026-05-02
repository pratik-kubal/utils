"""Mock BFS probe of a website to discover site depth.

Same-domain only, bounded by max_depth and max_pages. Prints a depth
histogram and the deepest URLs found. BFS reports shortest-path depth
from the start URL.

Usage: python probe_depth.py <url>
"""

import asyncio
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, FilterChain, DomainFilter

MAX_DEPTH = 6
MAX_PAGES = 80


async def main(start_url: str):
    allowed_domain = urlparse(start_url).netloc
    if not allowed_domain:
        raise SystemExit(f"Could not parse domain from URL: {start_url}")

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
        stream=False,
        verbose=False,
    )
    browser_config = BrowserConfig(headless=True, verbose=False)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(url=start_url, config=run_config)

    depth_counts = Counter()
    by_depth = defaultdict(list)
    failures = 0
    for r in results:
        if not r.success:
            failures += 1
            continue
        depth = r.metadata.get("depth", 0) if r.metadata else 0
        depth_counts[depth] += 1
        by_depth[depth].append(r.url)

    total = sum(depth_counts.values())
    max_observed = max(depth_counts) if depth_counts else -1

    print(f"Start:           {start_url}")
    print(f"Configured cap:  max_depth={MAX_DEPTH}, max_pages={MAX_PAGES}")
    print(f"Pages crawled:   {total} (failures: {failures})")
    print(f"Max depth seen:  {max_observed}")
    print()
    print("Depth histogram:")
    for d in sorted(depth_counts):
        print(f"  depth {d}: {depth_counts[d]} pages")

    if max_observed >= 0:
        print()
        print(f"Sample URLs at deepest level ({max_observed}):")
        for url in by_depth[max_observed][:10]:
            print(f"  {url}")

    print()
    if max_observed == MAX_DEPTH and total >= MAX_PAGES:
        print("NOTE: hit both caps — true depth may be larger.")
    elif max_observed == MAX_DEPTH:
        print("NOTE: hit max_depth cap — true depth may be larger.")
    elif total >= MAX_PAGES:
        print("NOTE: hit max_pages cap — depth count may be incomplete.")
    else:
        print("Crawl exhausted naturally; depth is conclusive.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python probe_depth.py <url>")
    asyncio.run(main(sys.argv[1]))
