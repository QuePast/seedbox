# FitGirl Repacks RSS Generator

I made this script as long time fitgirl torrent user as another form of donation. I wanted to automatically download torrents through RSS feed and seed them to very high ratio and then delete them. This is how my personal seedbox works.
This script generates an RSS feed with magnet links for the latest FitGirl Repacks by parsing the official RSS feed from https://fitgirl-repacks.site/feed/.

## Features

- Uses the official FitGirl Repacks RSS feed
- Extracts magnet links directly from the feed content
- Focuses only on the 8 most recent game repacks aka. "first page"
- Creates an RSS feed with magnet links for qBittorrent
- Automatically runs via GitHub Actions
- Stateless design - no local storage needed

## Automated RSS Feed

This script is automatically run every 1 hour via GitHub Actions to provide an up-to-date RSS feed of the latest FitGirl repacks.

### Using the RSS Feed in qBittorrent

1. Open qBittorrent
2. Go to View > RSS Reader
3. Click "New subscription"
4. Enter the following URL:
   ```
   https://raw.githubusercontent.com/QuePast/seedbox/main/fitgirl_torrents.xml
   ```
5. Set up auto-downloading rules as needed

The RSS feed contains magnet links for the 8 most recent FitGirl repacks and is updated every 6 hours.

### GitHub Actions Workflow

The script is automatically run using GitHub Actions:
- Runs every 1 hour
- Updates the RSS feed with the latest repacks
- Commits and pushes changes to this repository

You can also manually trigger the workflow by going to the Actions tab and running the "Update FitGirl RSS Feed" workflow.

## Requirements

- Python 3.6+
- Required packages: requests

## Local Usage

If you want to run the script locally:

1. Clone this repository
2. Install the required packages:
   ```
   pip install requests
   ```
3. Run the script:
   ```
   python fitgirl_rss.py
   ```

## How It Works

1. The script fetches the official RSS feed from FitGirl's website
2. It parses the feed to extract magnet links from the content
3. It filters out non-game posts (like updates, upcoming releases, etc.)
4. It generates an RSS feed with the magnet links
5. The RSS feed is committed to the repository

## Notes

- The script is set to process only the 8 most recent game repacks. You can change this by modifying the `MAX_TORRENTS` constant.
- The script includes retry logic to handle connection issues.
- Non-game posts (like updates, upcoming releases, etc.) are automatically filtered out.
- The script is stateless - it doesn't store any data between runs, making it simpler and more reliable.

## Disclaimer

This script is for educational purposes only. Only download content that you have the legal right to access. 
