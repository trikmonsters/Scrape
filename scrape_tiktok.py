import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 1. Gunakan User-Agent asli (menyamar sebagai pencari reguler di Chrome Windows)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    # 2. Set up Browser Config dengan proteksi anti-bot yang lebih ketat
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        text_mode=False,
        headers={"User-Agent": user_agent},
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--window-size=1920,1080",
            "--start-maximized"
        ]
    )

    # 3. Skema ekstraksi (diperluas agar fleksibel)
    schema = {
        "name": "TikTok Search Videos",
        "baseSelector": 'div[data-e2e="search_video-item"], div[class*="DivVideoItem"]', # Menambahkan fallback selector
        "fields": [
            {
                "name": "video_url",
                "selector": 'a[href*="/video/"]',
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "description",
                "selector": 'div[data-e2e="search-card-video-caption"], h1, div[class*="DivCaption"]',
                "type": "text"
            }
        ]
    }
    
    extraction_strategy = JsonCssExtractionStrategy(schema)

    # 4. Trik: Menggunakan JavaScript Scroll yang lebih halus agar menyerupai manusia
    js_scroll_code = """
    for (let i = 0; i < 3; i++) {
        window.scrollBy(0, window.innerHeight);
        await new Promise(r => setTimeout(r, 1500));
    }
    """

    # 5. Ubah 'wait_for' ke elemen 'body' agar jika kena Captcha, script tidak langsung timeout/crash,
    # melainkan tetap mengambil isi halaman untuk kita analisa.
    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        js_code=js_scroll_code,
        wait_for='body', 
        delay_before_return_html=8, # Beri waktu ekstra untuk loading konten JavaScript
        cache_mode=CacheMode.BYPASS 
    )

    search_url = "https://www.tiktok.com/search/video?q=moisturizer%20g2g"
    print(f"Memulai scraping pada: {search_url}")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        if result.success:
            # Simpan screenshot/HTML mentah untuk debugging jika hasil kosong
            if not result.extracted_content or result.extracted_content == "[]":
                print("\n[⚠️ WARNING] Konten kosong. Kemungkinan besar terkena Captcha/Blokir IP GitHub.")
                print("Mencoba menyimpan HTML mentah untuk analisa...")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(result.html)
            
            try:
                videos = json.loads(result.extracted_content)
            except Exception:
                videos = []

            print(f"\nBerhasil mengekstrak {len(videos)} data video.")
            
            # Tetap buat file JSON agar GitHub Actions tidak error saat upload artifact
            with open("tiktok_results.json", "w", encoding="utf-8") as f:
                json.dump(videos, f, indent=4, ensure_ascii=False)
                
            for idx, video in enumerate(videos, 1):
                url = video.get('video_url', '')
                desc = video.get('description', '').strip()
                if url: # Hanya print yang memiliki link
                    print(f"{idx}. {desc if desc else 'No Title'}")
                    print(f"   Link: {url}\n")
        else:
            print(f"Gagal melakukan crawl. Error: {result.error_message}")
            # Buat file kosong agar step upload artifact di GitHub Actions tidak skip/error
            with open("tiktok_results.json", "w") as f: f.write("[]")

if __name__ == "__main__":
    asyncio.run(main())
