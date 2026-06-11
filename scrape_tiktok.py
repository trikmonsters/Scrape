import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        text_mode=False,
        headers={"User-Agent": user_agent},
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--window-size=1920,1080"
        ]
    )

    # Kita tidak pakai JsonCssExtractionStrategy karena rawan diblokir CSS-nya.
    # Kita ambil HTML mentahnya saja, lalu kita bedah pakai Regex di Python.
    run_config = CrawlerRunConfig(
        wait_for='body', 
        delay_before_return_html=10, # Beri waktu lebih lama agar data hydrasi TikTok selesai loading
        cache_mode=CacheMode.BYPASS 
    )

    search_url = "https://www.tiktok.com/search/video?q=moisturizer%20g2g"
    print(f"Memulai scraping data internal pada: {search_url}")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        videos_list = []

        if result.success:
            html_content = result.html
            
            # --- TRIK REGEX: Mencari JSON internal TikTok ---
            # TikTok menyimpan data video di dalam window.__UNIVERSAL_DATA_FOR_REHYDRATION__ atau script SIGI_STATE
            match = re.search(r'__UNIVERSAL_DATA_FOR_REHYDRATION__\s*=\s*({.+?});', html_content)
            
            if not match:
                # Coba fallback ke pattern script kedua jika pattern pertama tidak ketemu
                match = re.search(r'<script id="SIGI_STATE" type="application/json">({.+?})</script>', html_content)

            if match:
                try:
                    raw_json = match.group(1)
                    data = json.loads(raw_json)
                    
                    # Mencari objek video di dalam nested JSON secara rekursif (Simplifikasi pencarian)
                    # Karena struktur JSON TikTok sangat dalam, kita cari pattern keyword url video
                    urls = re.findall(r'"https://www\.tiktok\.com/@.*?/video/\d+"', raw_json)
                    descriptions = re.findall(r'"desc"\s*:\s*"([^"]+)"', raw_json)
                    
                    # Bersihkan hasil duplikat
                    urls = list(set([url.strip('"') for url in urls]))
                    
                    for idx, url in enumerate(urls):
                        desc = descriptions[idx] if idx < len(descriptions) else "No Description"
                        videos_list.append({
                            "video_url": url,
                            "description": desc.encode().decode('unicode-escape', errors='ignore')
                        })
                except Exception as e:
                    print(f"Gagal memparsing struktur JSON internal: {e}")
            
            # Jika regex gagal, coba cara kasar (Regex langsung ke seluruh HTML) sebagai pertahanan terakhir
            if not videos_list:
                print("Mencoba ekstraksi langsung via Regex global...")
                raw_urls = re.findall(r'https://www\.tiktok\.com/@[a-zA-Z0-9_.]+/video/\d+', html_content)
                raw_urls = list(set(raw_urls)) # Hapus duplikat
                
                for url in raw_urls:
                    videos_list.append({
                        "video_url": url,
                        "description": "TikTok Video Review (Glad2Glow)"
                    })

            print(f"\n[HASIL] Berhasil mengekstrak {len(videos_list)} data video.")
            
            # Simpan hasil ke JSON
            with open("tiktok_results.json", "w", encoding="utf-8") as f:
                json.dump(videos_list, f, indent=4, ensure_ascii=False)
                
            for idx, video in enumerate(videos_list[:15], 1): # Batasi print 15 teratas di log
                print(f"{idx}. {video['description']}")
                print(f"   Link: {video['video_url']}\n")
                
            if not videos_list:
                print("[⚠️] TikTok benar-benar menyembunyikan konten dari IP ini. Menyimpan file debug...")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
        else:
            print(f"Crawl gagal: {result.error_message}")
            with open("tiktok_results.json", "w") as f: f.write("[]")

if __name__ == "__main__":
    asyncio.run(main())
