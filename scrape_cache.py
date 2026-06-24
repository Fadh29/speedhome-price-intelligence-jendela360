import os
import json
import time
from scraper import scrape_speedhome_listings

def build_offline_cache():
    slugs = [
        "mont-kiara", "bangsar", "cheras", "sentul", "ampang",
        "petaling-jaya", "subang-jaya", "puchong", "cyberjaya", "putrajaya"
    ]
    
    cache_dir = os.path.join(os.path.dirname(__file__), "cached_data")
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Starting to build offline cache in: {cache_dir}")
    
    for slug in slugs:
        print(f"Scraping {slug}...")
        try:
            listings, area_name, search_url, error = scrape_speedhome_listings(slug, delay=1.5)
            if error:
                print(f"Error scraping {slug}: {error}")
                continue
                
            if not listings:
                print(f"No listings returned for {slug}")
                continue
                
            output_file = os.path.join(cache_dir, f"{slug}.json")
            cache_payload = {
                "slug": slug,
                "area_name": area_name,
                "search_url": search_url,
                "listings": listings
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, indent=2, ensure_ascii=False)
                
            print(f"Successfully cached {len(listings)} listings for {slug} to {output_file}")
            time.sleep(2.0)  # Politeness delay
            
        except Exception as e:
            print(f"Exception while caching {slug}: {e}")

if __name__ == "__main__":
    build_offline_cache()
