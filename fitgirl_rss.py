import requests
import re
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
import time

# Constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
]
FITGIRL_FEED_URL = 'https://fitgirl-repacks.site/feed/'
RSS_FILE = 'fitgirl_torrents.xml'
MAX_TORRENTS = 8  # Only process the 8 most recent torrents
MAX_RETRIES = 3    # Maximum number of retry attempts

def get_feed():
    """Get the RSS feed from FitGirl's website with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                'Referer': 'https://www.google.com/',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            print(f"Attempt {attempt+1}/{MAX_RETRIES} to fetch feed...")
            response = requests.get(FITGIRL_FEED_URL, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if we got valid XML
            if not response.text or '<rss' not in response.text:
                print(f"Received invalid response (not RSS/XML)")
                if attempt < MAX_RETRIES - 1:
                    delay = random.uniform(2, 5)
                    print(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    continue
            
            return response.text
        except Exception as e:
            print(f"Error fetching feed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                delay = random.uniform(2, 5)
                print(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed")
    
    return None

def extract_torrents(feed_content):
    """Extract torrent information from the feed content."""
    if not feed_content:
        return []
    
    # Find all items in the feed
    item_pattern = r'<item>(.*?)</item>'
    items = re.findall(item_pattern, feed_content, re.DOTALL)
    
    if not items:
        print("No items found in feed. Feed content may be invalid.")
        print(f"Feed starts with: {feed_content[:100]}...")
        return []
    
    print(f"Found {len(items)} items in feed")
    
    results = []
    for item in items:
        try:
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', item)
            if not title_match:
                continue
            title = title_match.group(1)
            title = title.replace('&#8211;', '-').replace('&#8217;', "'").replace('&amp;', '&')
            
            # Skip non-game posts (like updates, upcoming, etc.)
            skip_keywords = ['upcoming', 'updates', 'moved', 'updated', 'schedule', 'site news']
            if any(keyword in title.lower() for keyword in skip_keywords):
                print(f"Skipping non-game post: {title}")
                continue
            
            # Extract link
            link_match = re.search(r'<link>(.*?)</link>', item)
            if not link_match:
                continue
            link = link_match.group(1)
            
            # Extract publication date
            date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
            pub_date = date_match.group(1) if date_match else datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Extract content
            content_match = re.search(r'<content:encoded>(.*?)</content:encoded>', item, re.DOTALL)
            if not content_match:
                content_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                if not content_match:
                    print(f"No content found for: {title}")
                    continue
            content = content_match.group(1)
            
            # Find magnet link in content
            magnet_match = re.search(r'href="(magnet:\?xt=urn:btih:[^"]+)"', content)
            if not magnet_match:
                print(f"No magnet link found for: {title}")
                continue
            magnet = magnet_match.group(1)
            
            # Unescape HTML entities in the magnet link
            magnet = magnet.replace('&amp;', '&')
            
            results.append({
                'title': title,
                'link': link,
                'pub_date': pub_date,
                'magnet': magnet
            })
            print(f"Successfully extracted: {title}")
        except Exception as e:
            print(f"Error processing item: {e}")
    
    return results[:MAX_TORRENTS]  # Limit to MAX_TORRENTS

def create_rss_feed(torrents):
    """Create an RSS feed from the torrent data."""
    try:
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # Add channel metadata
        ET.SubElement(channel, 'title').text = 'FitGirl Repacks Torrents'
        ET.SubElement(channel, 'link').text = 'https://fitgirl-repacks.site/'
        ET.SubElement(channel, 'description').text = 'Latest torrents from FitGirl Repacks'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Add items for each torrent
        for torrent in torrents:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = torrent['title']
            ET.SubElement(item, 'link').text = torrent['link']
            ET.SubElement(item, 'enclosure', {
                'url': torrent['magnet'],
                'type': 'application/x-bittorrent'
            })
            ET.SubElement(item, 'pubDate').text = torrent['pub_date']
            ET.SubElement(item, 'description').text = f"FitGirl Repack: {torrent['title']}"
        
        # Save to file
        with open(RSS_FILE, 'w', encoding='utf-8') as f:
            f.write(minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  "))
        
        print(f"RSS feed created with {len(torrents)} torrents")
        return True
    except Exception as e:
        print(f"Error creating RSS feed: {e}")
        return False

def main():
    print("Starting FitGirl RSS feed generator...")
    
    # Get feed content
    feed_content = get_feed()
    if not feed_content:
        print("Could not fetch the feed")
        return
    
    # Extract torrent information
    torrents = extract_torrents(feed_content)
    if not torrents:
        print("No torrents found in the feed")
        return
    
    print(f"Found {len(torrents)} torrents in the feed")
    
    # Create RSS feed
    create_rss_feed(torrents)
    
    print("Finished.")

if __name__ == "__main__":
    main() 
