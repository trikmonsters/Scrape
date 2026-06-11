import asyncio
import json
import re
import urllib.parse
import httpx

async def main():
    # Kata kunci pencarian bebas (bisa pakai spasi)
    keyword = "moisturizer glad2glow"
    encoded_keyword = urllib.parse.quote_plus(keyword)
    
    # Menembak langsung ke search engine web viewer Instagram gratis (GreatFon)
    # Jalur ini mengembalikan HTML berisi post/video yang relevan dengan kata kunci
    url = f"https://greatfon.io/search?q={encoded_keyword}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "id,en-US;q=0.7,en;q=0.3",
        "Alt-Used": "greatfon.io"
    }

    print(f"Memulai scraping via Web Viewer Gratis untuk kata kunci: '{keyword}'...")
    
    reels_list = []
    
    try:
        # Gunakan limit timeout agak panjang karena web viewer gratisan kadang agak lambat
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Pola 1: Mencari link shortcode instagram asli jika diteruskan langsung oleh web tersebut
                # Pola 2: Mencari link internal video web tersebut (misal: /p/Cxxx/ atau /c/xxx) lalu kita ubah jadi link IG resmi
                shortcodes = re.findall(r'/(?:p|reels|reel)/([a-zA-Z0-9_\-]+)', html_content)
                
                # Bersihkan duplikat
                unique_shortcodes = list(set(shortcodes))
                
                for code in unique_shortcodes:
                    if len(code) >= 5: # Validasi panjang ID Reels standar
                        reels_list.append({
                            "video_url": f"https://www.instagram.com/reels/{code}/",
                            "description": f"Instagram Video Review - {keyword}"
                        })
            else:
                print(f"Gagal memuat halaman Web Viewer. Status HTTP: {response.status_code}")
                # Backup trik ke-2: Gunakan alternatif viewer lain (Picuki) jika GreatFon down
                print("Mencoba jalur cadangan via Picuki...")
                picuki_url = f"https://www.picuki.com/search?q={encoded_keyword}"
                res_picuki = await client.get(picuki_url, headers=headers)
                if res_picuki.status_code == 200:
                    shortcodes = re.findall(r'/(?:p|media)/([a-zA-Z0-9_\-]+)', res_picuki.text)
                    for code in list(set(shortcodes)):
                        if len(code) >= 5:
                            reels_list.append({
                                "video_url": f"https://www.instagram.com/reels/{code}/",
                                "description": f"Instagram Video Review (Picuki Alternative) - {keyword}"
                            })

    except Exception as e:
        print(f"Terjadi kendala saat ekstraksi data: {e}")

    print(f"\n[HASIL] Berhasil mengekstrak {len(reels_list)} video Instagram Reels.")
    
    # Simpan hasil akhir ke file JSON
    with open("instagram_results.json", "w", encoding="utf-8") as f:
        json.dump(reels_list, f, indent=4, ensure_ascii=False)
        
    # Cetak hasil ke log GitHub Actions
    for idx, reel in enumerate(reels_list[:15], 1):
        print(f"{idx}. {reel['description']}")
        print(f"   Link: {reel['video_url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
