import os
import json
import re
import subprocess
import xml.etree.ElementTree as ET

# List of known area/city suffixes in Malaysia to format display names nicely
KNOWN_SUFFIXES = [
    "mont-kiara", "subang-jaya", "petaling-jaya", "batu-caves", "kuala-lumpur", 
    "seri-kembangan", "damansara-heights", "kelana-jaya", "kota-damansara",
    "sri-hartamas", "ara-damansara", "bandar-sunway", "taman-melawati",
    "puncak-alam", "goodview-heights", "mahkota-hills", "setia-ecohill",
    "skysanctuary", "klang", "bangi", "kajang", "puchong", "melaka", "lenggeng",
    "semenyih", "ampang", "sentul", "cheras", "bangsar", "kepong", "setapak",
    "shah-alam", "rawang", "klcc", "cyberjaya", "gombak", "putrajaya", "banting",
    "cyberia", "dengkil", "cyber", "nilai", "port-dickson", "seremban", "johor-bahru"
]

def clean_slug_to_display_name(slug):
    # Remove leading/trailing dashes and lowercase it
    slug = slug.strip('-').lower()
    
    # Try to match a known suffix at the end of the slug
    matched_suffix = None
    for suffix in KNOWN_SUFFIXES:
        if slug.endswith("-" + suffix):
            matched_suffix = suffix
            break
            
    if matched_suffix:
        # Split the slug into name and suffix
        name_part = slug[:-len(matched_suffix)-1]
        
        # Format name and suffix
        name_formatted = " ".join([w.capitalize() for w in name_part.split('-')])
        suffix_formatted = " ".join([w.capitalize() for w in matched_suffix.split('-')])
        
        # Adjust some specific casing (e.g. 1br -> 1BR, lrt -> LRT)
        name_formatted = name_formatted.replace(" Lrt", " LRT").replace(" Mrt", " MRT")
        
        return f"{name_formatted}, {suffix_formatted}"
    else:
        # Fallback to simple capitalization of the whole slug
        name_formatted = " ".join([w.capitalize() for w in slug.split('-')])
        name_formatted = name_formatted.replace(" Lrt", " LRT").replace(" Mrt", " MRT")
        return name_formatted

def build_locations_json():
    print("Building locations index...")
    sitemaps = [
        "https://speedhome.com/sitemap-locations.xml",
        "https://speedhome.com/sitemap-listing-pages.xml"
    ]
    
    headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    collected_locations = {}
    
    # Fallback default locations in case fetching fails
    default_locations = [
        {"name": "Mont Kiara, Kuala Lumpur", "slug": "mont-kiara"},
        {"name": "Bangsar, Kuala Lumpur", "slug": "bangsar"},
        {"name": "Cheras, Kuala Lumpur", "slug": "cheras"},
        {"name": "Sentul, Kuala Lumpur", "slug": "sentul"},
        {"name": "Ampang, Kuala Lumpur", "slug": "ampang"},
        {"name": "Petaling Jaya, Selangor", "slug": "petaling-jaya"},
        {"name": "Subang Jaya, Selangor", "slug": "subang-jaya"},
        {"name": "Puchong, Selangor", "slug": "puchong"},
        {"name": "Cyberjaya, Selangor", "slug": "cyberjaya"},
        {"name": "Putrajaya, Wilayah Persekutuan", "slug": "putrajaya"},
        {"name": "Shah Alam, Selangor", "slug": "shah-alam"},
        {"name": "Klang, Selangor", "slug": "klang"},
        {"name": "Kuala Lumpur, Malaysia", "slug": "kuala-lumpur"}
    ]
    
    for sitemap_url in sitemaps:
        print(f"Fetching sitemap: {sitemap_url}")
        res = subprocess.run(['curl.exe', '-s', '-A', headers, sitemap_url], capture_output=True)
        if res.returncode != 0:
            print(f"Warning: Failed to fetch sitemap {sitemap_url}")
            continue
            
        try:
            root = ET.fromstring(res.stdout)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            for url_node in root.findall('ns:url', ns):
                loc_node = url_node.find('ns:loc', ns)
                if loc_node is not None:
                    url_text = loc_node.text
                    # Extract slug from URL like https://speedhome.com/rent/mont-kiara
                    match = re.search(r'https://speedhome\.com/(?:rent|sewa|zh/rent|my/sewa)/([^/?#]+)', url_text)
                    if match:
                        slug = match.group(1)
                        # Exclude general landing pages or sub-routes
                        if slug in ["kuala-lumpur", "selangor", "johor", "penang"]:
                            # Keep them but handle normally
                            pass
                        
                        display_name = clean_slug_to_display_name(slug)
                        collected_locations[slug] = {
                            "name": display_name,
                            "slug": slug
                        }
        except Exception as e:
            print(f"Warning: Failed to parse sitemap XML: {e}")
            
    # Combine with default fallbacks to ensure we always have the main areas covered
    for fallback in default_locations:
        slug = fallback["slug"]
        if slug not in collected_locations:
            collected_locations[slug] = fallback
            
    # Sort locations by name
    sorted_locations = sorted(list(collected_locations.values()), key=lambda x: x["name"])
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), "locations.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_locations, f, indent=2, ensure_ascii=False)
        
    print(f"Success: Compiled {len(sorted_locations)} locations to {output_path}")

if __name__ == "__main__":
    build_locations_json()
