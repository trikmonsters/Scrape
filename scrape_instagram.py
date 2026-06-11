import asyncio
import json
import re
import urllib.parse
import httpx

async def main():
    # Kata kunci pencarian bebas (tidak wajib pakai hashtag)
    keyword = "review moisturizer glad2glow"
    
    # Memanfaatkan Google Dorking untuk mencari di direktori khusus instagram.com/reels/
    query = f"site:instagram.com/reels/ {keyword}"
    encoded_query = urllib.parse.quote_plus(query)
    
    # Menggunakan URL Google Search versi mobile/html dasar agar mudah diekstrak
    url = f"https://www.google.com/search?q={encoded_query}&hl=id"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"Mencari kata kunci '{keyword}' di Instagram Reels via Google Index...")
    
    reels_list = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Regex untuk menangkap pola shortcode/link unik Instagram Reels dari hasil pencarian
                # Contoh: instagram.com/reels/C42bXySyXxx/
                raw_matches = re.findall(r'instagram\.com/reels/([a-zA-Z0-9_\-]+)', html_content)
                
                # Hapus duplikasi shortcode yang terjaring
                unique_shortcodes = list(set(raw_matches))
                
                # Ekstrak juga judul/potongan caption yang muncul di Google jika polanya tertangkap
                # Sebagai fallback, kita buat deskripsi default berdasarkan keyword
                for shortcode in unique_shortcodes:
                    # Bersihkan jika ada parameter sisa dari URL google
                    clean_code = shortcode.split('&')[0].split('%')[0]
                    
                    reels_list.append({
                        "video_url": f"https://www.instagram.com/reels/{clean_code}/",
                        "description": f"Instagram Reels Video Review for {keyword}"
                    })
            else:
                print(f"Gagal bypass Google Search. HTTP Status: {response.status_code}")
                
    except Exception as e:
        print(f"Terjadi kendala teknis: {e}")

    print(f"\n[HASIL] Berhasil mengekstrak {len(reels_list)} video Instagram Reels.")
    
    # Simpan hasil akhir ke file JSON
    with open("instagram_results.json", "w", encoding="utf-8") as f:
        json.dump(reels_list, f, indent=4, ensure_ascii=False)
        
    # Tampilkan list link video di log GitHub Actions
    for idx, reel in enumerate(reels_list[:15], 1):
        print(f"{idx}. {reel['description']}")
        print(f"   Link: {reel['video_url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
