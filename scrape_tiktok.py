import asyncio
import json
# Tambahkan CacheMode di bagian import
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 1. Konfigurasi Browser (Anti-Bot/Stealth)
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        text_mode=False,
        extra_args=["--disable-blink-features=AutomationControlled"]
    )

    # 2. Skema ekstraksi TikTok
    schema = {
        "name": "TikTok Search Videos",
        "baseSelector": 'div[data-e2e="search_video-item"]',
        "fields": [
            {
                "name": "video_url",
                "selector": 'a[href*="/video/"]',
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "description",
                "selector": 'div[data-e2e="search-card-video-caption"]',
                "type": "text"
            }
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema)

    # 3. Konfigurasi crawling dan interaksi halaman
    js_scroll_code = """
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 3000));
    window.scrollTo(0, document.body.scrollHeight);
    """

    # --- PERBAIKAN DI SINI ---
    # Ganti bypass_cache=True menjadi cache_mode=CacheMode.BYPASS
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        js_code=js_scroll_code,
        wait_for='div[data-e2e="search_video-item"]', 
        delay_before_return_html=5,
        cache_mode=CacheMode.BYPASS 
    )
    # -------------------------

    # URL Pencarian TikTok untuk "moisturizer g2g"
    search_url = "https://www.tiktok.com/search/video?q=moisturizer%20g2g"

    print(f"Memulai scraping pada: {search_url}")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        if result.success:
            videos = json.loads(result.extracted_content)
            print(f"\nBerhasil menemukan {len(videos)} video:")
            
            with open("tiktok_results.json", "w", encoding="utf-8") as f:
                json.dump(videos, f, indent=4, ensure_ascii=False)
                
            for idx, video in enumerate(videos, 1):
                print(f"{idx}. {video.get('description', 'No Title')}")
                print(f"   Link: {video.get('video_url', 'No Link')}\n")
        else:
            print(f"Gagal melakukan crawl. Error: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
