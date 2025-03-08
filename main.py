import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]
BASE_URL = 'https://1337x.to'
FITGIRL_URL = f'{BASE_URL}/user/FitGirl/'
DATA_FILE = 'torrents_data.json'
RSS_FILE = 'fitgirl_torrents.xml'
MAX_TORRENTS = 10  # Only process the 10 most recent torrents

def get_soup(url):
    """Make a request to the URL and return a BeautifulSoup object."""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_torrent_links():
    """Get torrent links from the FitGirl user page."""
    soup = get_soup(FITGIRL_URL)
    if not soup:
        return []
    
    links = []
    try:
        table = soup.find('table', class_='table-list')
        if not table:
            return []
        
        # Extract torrent links from rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            for cell in row.find_all('td'):
                for link in cell.find_all('a', href=True):
                    if '/torrent/' in link['href']:
                        links.append({
                            'name': link.text.strip(),
                            'url': BASE_URL + link['href']
                        })
                        break  # Found the torrent link in this row, move to next row
    except Exception as e:
        print(f"Error parsing page: {e}")
    
    return links[:MAX_TORRENTS]  # Return only the most recent torrents

def get_magnet_link(torrent_url):
    """Extract the magnet link from a torrent page."""
    soup = get_soup(torrent_url)
    if not soup:
        return None
    
    try:
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('magnet:'):
                return link['href']
    except Exception as e:
        print(f"Error extracting magnet link: {e}")
    
    return None

def load_data():
    """Load existing torrent data from file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            print(f"Error reading {DATA_FILE}")
    return {}

def save_data(data):
    """Save torrent data to file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_rss_feed(torrents_data):
    """Create an RSS feed from the torrent data."""
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    # Add channel metadata
    ET.SubElement(channel, 'title').text = 'FitGirl Repacks Torrents'
    ET.SubElement(channel, 'link').text = FITGIRL_URL
    ET.SubElement(channel, 'description').text = 'Latest torrents from FitGirl Repacks'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Sort torrents by date_added (newest first)
    sorted_torrents = sorted(
        [(url, torrent) for url, torrent in torrents_data.items() if 'magnet' in torrent and torrent['magnet']],
        key=lambda x: x[1].get('date_added', ''),
        reverse=True
    )[:MAX_TORRENTS]
    
    # Add items for each torrent
    for url, torrent in sorted_torrents:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = torrent['name']
        ET.SubElement(item, 'link').text = url
        ET.SubElement(item, 'enclosure', {
            'url': torrent['magnet'],
            'type': 'application/x-bittorrent'
        })
        ET.SubElement(item, 'pubDate').text = torrent.get('date_added', 
                                                         datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        ET.SubElement(item, 'description').text = f"FitGirl Repack: {torrent['name']}"
    
    # Save to file
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  "))
    
    print(f"RSS feed created with {len(sorted_torrents)} torrents")

def main():
    print("Starting FitGirl torrent scraper...")
    
    # Load existing data and get new torrents
    torrents_data = load_data()
    torrent_links = get_torrent_links()
    
    if not torrent_links:
        print("No torrents found")
        return
    
    print(f"Found {len(torrent_links)} torrents")
    new_count = 0
    
    # Process torrents
    for torrent in torrent_links:
        url = torrent['url']
        
        # Skip if we already have this torrent with a magnet link
        if url in torrents_data and 'magnet' in torrents_data[url] and torrents_data[url]['magnet']:
            print(f"Already have: {torrent['name']}")
            continue
        
        print(f"New torrent: {torrent['name']}")
        new_count += 1
        
        # Get magnet link
        magnet = get_magnet_link(url)
        
        if magnet:
            print(f"Found magnet: {magnet[:50]}...")
            torrents_data[url] = {
                'name': torrent['name'],
                'magnet': magnet,
                'date_added': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
            save_data(torrents_data)  # Save after each successful magnet link
        
        # Be nice to the server
        time.sleep(random.uniform(1, 3))
    
    # Create RSS feed
    create_rss_feed(torrents_data)
    print(f"Finished. Found {new_count} new torrents.")

if __name__ == "__main__":
    main()
