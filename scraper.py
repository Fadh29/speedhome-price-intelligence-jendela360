import requests
import json
import re
import time
from bs4 import BeautifulSoup

def slugify(text):
    """
    Convert a string text into a URL slug.
    """
    text = text.lower().strip()
    # Replace non-word chars with dashes
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with dashes
    text = re.sub(r'[\s_]+', '-', text)
    # Replace multiple dashes with single dash
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def extract_slug_from_url(url):
    """
    Extract search slug and current page from a Speedhome URL.
    Returns (slug, page_number)
    """
    # Remove trailing slash or spaces
    url = url.strip().rstrip('/')
    
    # Try to match /rent/slug or /sewa/slug etc.
    match = re.search(r'https://speedhome\.com/(?:rent|sewa|zh/rent|my/sewa)/([^/?#]+)', url)
    if not match:
        # Check if they just pasted the slug or a relative path
        match = re.search(r'(?:rent|sewa)/([^/?#]+)', url)
        
    slug = match.group(1) if match else slugify(url.split('/')[-1])
    
    # Check if page query param exists
    page_match = re.search(r'[?&]page=(\d+)', url)
    page = int(page_match.group(1)) if page_match else 1
    
    return slug, page

def normalize_furniture(furnish_type):
    if not furnish_type:
        return "Unfurnished"
    ft = furnish_type.upper()
    if "FULL" in ft:
        return "Fully Furnished"
    elif "PART" in ft:
        return "Partially Furnished"
    else:
        return "Unfurnished"

def normalize_room_type(bedroom_count, type_str):
    if type_str and type_str.upper() in ["STUDIO", "ROOM"]:
        return type_str.capitalize()
    if bedroom_count is None:
        return "N/A"
    if bedroom_count == 0:
        return "Studio"
    return f"{bedroom_count} BR"

def fetch_speedhome_page_source(url):
    """
    Fetch raw HTML source of a URL, bypassing Cloudflare bot protection.
    Strategy:
      1. curl_cffi (impersonates Chrome TLS fingerprint) — most reliable
      2. subprocess curl — works when curl is installed  
      3. requests — basic fallback
    """
    # Method 1: curl_cffi (best Cloudflare bypass)
    try:
        from curl_cffi import requests as cffi_requests
        res = cffi_requests.get(url, impersonate="chrome", timeout=20)
        if res.status_code == 200 and len(res.content) > 1000:
            return res.content
    except Exception:
        pass

    # Method 2: subprocess curl (cross-platform)
    try:
        import subprocess
        import platform
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        curl_cmd = 'curl.exe' if platform.system() == 'Windows' else 'curl'
        cmd = [
            curl_cmd, '-s', '-L',
            '-A', user_agent,
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '-H', 'Accept-Language: en-US,en;q=0.9',
            '-H', 'Accept-Encoding: gzip, deflate',
            '--compressed',
            url
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=20)
        if res.returncode == 0 and len(res.stdout) > 1000:
            return res.stdout
    except Exception:
        pass

    # Method 3: plain requests (last resort)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200 and len(res.content) > 1000:
            return res.content
    except Exception:
        pass

    return None

def scrape_speedhome_listings(search_input, delay=1.0):
    """
    Scrape all speedhome listings for a given search_input (can be a URL or area name).
    Returns (listings, area_name, search_url, error_message)
    """
    # 1. Determine the starting slug and page
    if search_input.startswith("http://") or search_input.startswith("https://"):
        slug, start_page = extract_slug_from_url(search_input)
    else:
        slug = slugify(search_input)
        start_page = 1
        
    if not slug:
        return [], "", "", "Invalid search input or URL."
        
    listings = []
    page = start_page
    area_name = slug.replace('-', ' ').title() # Fallback display name
    base_search_url = f"https://speedhome.com/rent/{slug}"
    
    while True:
        # Construct search URL for the page
        url = f"{base_search_url}?page={page}" if page > 1 else base_search_url
        print(f"Scraping page {page}: {url}")
        
        # Add friendly delay between page fetches
        if page > start_page:
            time.sleep(delay)
            
        html = fetch_speedhome_page_source(url)
        if not html:
            if page == start_page:
                return [], "", "", f"Failed to fetch content from SPEEDHOME (check your connection or URL)."
            else:
                print(f"Failed to fetch page {page}. Stopping pagination.")
                break
                
        # Parse html
        soup = BeautifulSoup(html, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            if page == start_page:
                return [], "", "", "No structural data found on the page (website structure might have changed)."
            else:
                break
                
        try:
            data = json.loads(script.string)
            page_props = data.get('props', {}).get('pageProps', {})
            
            # Update area name from SEO data if available
            seo_data = page_props.get('initialSeoData', {})
            if seo_data and seo_data.get('area'):
                area_name = seo_data.get('area')
                
            property_list = page_props.get('propertyList', {})
            content = property_list.get('content', [])
            
            if not content:
                print(f"No listings found on page {page}. Stopping.")
                break
                
            for item in content:
                # Raw and calculated fields
                monthly_price = item.get('price')
                yearly_price = monthly_price * 12 if monthly_price else None
                furnish = normalize_furniture(item.get('furnishType'))
                beds = item.get('bedroom')
                baths = item.get('bathroom')
                room_type = normalize_room_type(beds, item.get('roomType') or item.get('type'))
                
                slug_attr = item.get('slug') or f"{slugify(item.get('name', 'property'))}-{item.get('ref', '')}"
                direct_link = f"https://speedhome.com/details/{slug_attr}"
                
                listings.append({
                    "id": item.get('id'),
                    "title": item.get('name'),
                    "property_name": item.get('name'),
                    "room_type": room_type,
                    "bedroom": beds if beds is not None else 0,
                    "bathroom": baths,
                    "price_monthly": monthly_price,
                    "price_yearly": yearly_price,
                    "sqft": item.get('sqft'),
                    "furniture": furnish,
                    "link": direct_link,
                    "latitude": item.get('latitude'),
                    "longitude": item.get('longitude'),
                    "ref": item.get('ref')
                })
                
            # Check pagination
            next_url = page_props.get('nextUrl')
            if not next_url:
                print("No next page. Scraping complete.")
                break
                
            # Extract page number from nextUrl
            page_match = re.search(r'[?&]page=(\d+)', next_url)
            if page_match:
                next_page = int(page_match.group(1))
                if next_page > page:
                    page = next_page
                else:
                    # Prevent infinite loops if page doesn't increment
                    break
            else:
                break
                
        except Exception as e:
            print(f"Error parsing page {page} JSON: {e}")
            if page == start_page:
                return [], "", "", f"Failed to parse SPEEDHOME data: {e}"
            break
            
    return listings, area_name, base_search_url, None

if __name__ == "__main__":
    print("Testing scraper for Mont Kiara...")
    res, name, url, err = scrape_speedhome_listings("mont-kiara")
    if err:
        print("Scraping error:", err)
    else:
        print(f"Scraped {len(res)} listings for {name}. URL: {url}")
        if res:
            print("First listing sample:", res[0])
