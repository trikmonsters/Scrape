import asyncio
import json
import re
import urllib.parse
import httpx

async def main():
    # Kata kunci pencarian bebas (non-hashtag)
    keyword = "review moisturizer glad2glow"
    
    # Menggunakan dorking khusus untuk mengunci hasil di instagram.com/reels/
    query = f"site:instagram.com/reels/ {keyword}"
    encoded_query = urllib.parse.quote_plus(query)
    
    # Menggunakan endpoint DuckDuckGo HTML (Lite version) yang ramah terhadap automation/bot
    url = f"https://lite.duckduckgo.com/lite/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # Data POST untuk dikirim ke DuckDuckGo Lite
    data = {
        "q": query,
        "kl": "id-id" # Mengutamakan indeks wilayah Indonesia
    }

    print(f"Mencari kata kunci '{keyword}' via DuckDuckGo Index...")
    
    reels_list = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            # DuckDuckGo Lite menggunakan metode POST untuk pencarian
            response = await client.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Regex untuk mendeteksi shortcode video Reels Instagram
                # Pola: instagram.com/reels/XXXXX/ atau instagram.com/reels/XXXXX?
                raw_matches = re.findall(r'instagram\.com/reels/([a-zA-Z0-9_\-]+)', html_content)
                
                # Menghapus duplikasi link yang sama
                unique_shortcodes = list(set(raw_matches))
                
                for shortcode in unique_shortcodes:
                    # Filter pembersihan karakter sisa hasil encoding HTML
                    clean_code = shortcode.split('&')[0].split('%')[0].split('?')[0]
                    if len(clean_code) >= 5: # Validasi panjang shortcode IG standar
                        reels_list.append({
                            "video_url": f"https://www.instagram.com/reels/{clean_code}/",
                            "description": f"Instagram Reels Video Review for {keyword}"
                        })
            else:
                print(f"Gagal bypass Search Engine. HTTP Status: {response.status_code}")
                
    except Exception as e:
        print(f"Terjadi kendala teknis saat membaca data: {e}")

    print(f"\n[HASIL] Berhasil mengekstrak {len(reels_list)} video Instagram Reels.")
    
    # Simpan hasil akhir ke file JSON agar GitHub Actions Artifact sukses dibuat
    with open("instagram_results.json", "w", encoding="utf-8") as f:
        json.dump(reels_list, f, indent=4, ensure_ascii=False)
        
    # Cetak hasil ke log GitHub Actions
    for idx, reel in enumerate(reels_list[:15], 1):
        print(f"{idx}. {reel['description']}")
        print(f"   Link: {reel['video_url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
