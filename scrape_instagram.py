import asyncio
import json
import re
import urllib.parse
import httpx

async def main():
    # Kata kunci pencarian bebas (bukan hashtag, bisa pakai spasi)
    keyword = "review moisturizer glad2glow"
    
    # Menggunakan metode Dorking pada mesin pencari AOL (Bing Engine)
    query = f"site:instagram.com/reels/ {keyword}"
    encoded_query = urllib.parse.quote_plus(query)
    
    # URL Pencarian AOL Search (Sangat toleran terhadap IP Github Actions)
    url = f"https://search.aol.com/aol/search?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    print(f"Mencari kata kunci '{keyword}' di Instagram Reels via AOL Index (Murni Gratis)...")
    
    reels_list = []
    
    try:
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Regex untuk mencari shortcode unik dari link Reels Instagram di dalam HTML AOL
                # Pola: instagram.com/reels/XXXXX/
                raw_matches = re.findall(r'instagram\.com/reels/([a-zA-Z0-9_\-]+)', html_content)
                
                # Hapus duplikasi shortcode yang sama
                unique_shortcodes = list(set(raw_matches))
                
                for shortcode in unique_shortcodes:
                    # Bersihkan karakter sampah sisa link jika ada
                    clean_code = shortcode.split('&')[0].split('%')[0].split('?')[0].split('"')[0]
                    
                    # Pastikan shortcode valid (IG shortcode biasanya minimal 5 karakter)
                    if len(clean_code) >= 5:
                        reels_list.append({
                            "video_url": f"https://www.instagram.com/reels/{clean_code}/",
                            "description": f"Instagram Reels Video - {keyword}"
                        })
            else:
                print(f"Gagal menembus Search Engine. HTTP Status: {response.status_code}")
                
    except Exception as e:
        print(f"Terjadi kendala teknis: {e}")

    print(f"\n[HASIL] Berhasil mengekstrak {len(reels_list)} video Instagram Reels.")
    
    # Simpan hasil akhir ke file JSON
    with open("instagram_results.json", "w", encoding="utf-8") as f:
        json.dump(reels_list, f, indent=4, ensure_ascii=False)
        
    # Cetak hasil ke log GitHub Actions agar Anda bisa langsung klik link-nya
    for idx, reel in enumerate(reels_list[:15], 1):
        print(f"{idx}. {reel['description']}")
        print(f"   Link: {reel['video_url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
