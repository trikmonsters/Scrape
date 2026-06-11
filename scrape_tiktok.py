import asyncio
import json
import httpx

async def main():
    # Keyword pencarian: moisturizer g2g
    keyword = "moisturizer g2g"
    
    # Menggunakan API publik TikWM untuk mencari video berdasarkan keyword
    # API ini gratis, cepat, dan sudah membypass bot detection TikTok secara internal
    api_url = "https://www.tikwm.com/api/feed/search"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    params = {
        "keywords": keyword,
        "count": 10,     # Jumlah video yang ingin diambil
        "cursor": 0
    }

    print(f"Memulai request pencarian TikTok via API untuk: '{keyword}'...")
    
    videos_list = []
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(api_url, data=params, headers=headers)
            
            if response.status_code == 200:
                res_json = response.json()
                
                # Cek apakah API mengembalikan data sukses
                if res_json.get("code") == 0 and "data" in res_json:
                    raw_videos = res_json["data"].get("videos", [])
                    
                    for vid in raw_videos:
                        video_id = vid.get("video_id")
                        author = vid.get("author", {}).get("unique_id")
                        
                        # Susun URL Video TikTok resmi
                        if video_id and author:
                            video_url = f"https://www.tiktok.com/@{author}/video/{video_id}"
                            description = vid.get("title", "No Title")
                            
                            videos_list.append({
                                "video_url": video_url,
                                "description": description
                            })
                else:
                    print(f"API merespon tetapi gagal memberikan data: {res_json.get('msg', 'Unknown Error')}")
            else:
                print(f"Gagal menghubungi API. HTTP Status: {response.status_code}")
                
    except Exception as e:
        print(f"Terjadi error saat request API: {e}")

    # Output Hasil
    print(f"\n[HASIL] Berhasil mengekstrak {len(videos_list)} data video.")
    
    # Simpan hasil ke JSON agar Github Actions Artifact tidak error
    with open("tiktok_results.json", "w", encoding="utf-8") as f:
        json.dump(videos_list, f, indent=4, ensure_ascii=False)
        
    for idx, video in enumerate(videos_list, 1):
        print(f"{idx}. {video['description']}")
        print(f"   Link: {video['video_url']}\n")

if __name__ == "__main__":
    asyncio.run(main())
