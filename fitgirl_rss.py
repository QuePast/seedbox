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
BASE_URL = 'https://fitgirl-repacks.site'
DATA_FILE = 'torrents_data.json'
RSS_FILE = 'fitgirl_torrents.xml'
MAX_TORRENTS = 10  # Only process the 10 most recent torrents

def get_soup(url):
    """Make a request to the URL and return a BeautifulSoup object."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_recent_posts():
    """Get recent posts from FitGirl's website."""
    soup = get_soup(BASE_URL)
    if not soup:
        return []
    
    posts = []
    try:
        # Find all article elements (posts)
        articles = soup.find_all('article')
        
        for article in articles[:MAX_TORRENTS]:  # Limit to MAX_TORRENTS
            # Get the post title and URL
            title_element = article.find('h1', class_='entry-title')
            if not title_element or not title_element.find('a', href=True):
                continue
                
            title = title_element.find('a').text.strip()
            url = title_element.find('a')['href']
            
            # Skip non-game posts (like updates, upcoming, etc.)
            skip_keywords = ['upcoming', 'updates', 'moved', 'updated', 'schedule', 'site news']
            if any(keyword in title.lower() for keyword in skip_keywords):
                continue
                
            posts.append({
                'name': title,
                'url': url
            })
    except Exception as e:
        print(f"Error parsing recent posts: {e}")
    
    return posts

def extract_magnet_from_post(post_url):
    """Extract magnet link from a post page."""
    soup = get_soup(post_url)
    if not soup:
        return None
    
    try:
        # Find all links in the post
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if it's a magnet link
            if href.startswith('magnet:'):
                return href
    except Exception as e:
        print(f"Error extracting magnet link from {post_url}: {e}")
    
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
    ET.SubElement(channel, 'link').text = BASE_URL
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
    print("Starting FitGirl RSS feed generator...")
    
    # Load existing data
    torrents_data = load_data()
    
    # Get recent posts
    posts = get_recent_posts()
    if not posts:
        print("No posts found or couldn't access the website")
        return
    
    print(f"Found {len(posts)} recent posts")
    new_count = 0
    
    # Process posts
    for post in posts:
        url = post['url']
        
        # Skip if we already have this post with a magnet link
        if url in torrents_data and 'magnet' in torrents_data[url] and torrents_data[url]['magnet']:
            print(f"Already have: {post['name']}")
            continue
        
        print(f"New post: {post['name']}")
        new_count += 1
        
        # Extract magnet link
        magnet = extract_magnet_from_post(url)
        
        if magnet:
            print(f"Found magnet link for: {post['name']}")
            torrents_data[url] = {
                'name': post['name'],
                'magnet': magnet,
                'date_added': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
        else:
            print(f"No magnet link found for: {post['name']}")
        
        # Be nice to the server
        time.sleep(random.uniform(1, 3))
    
    # Save data
    save_data(torrents_data)
    
    # Create RSS feed
    create_rss_feed(torrents_data)
    
    print(f"Finished. Found {new_count} new posts.")

if __name__ == "__main__":
    main() 