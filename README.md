# FitGirl Torrents RSS Generator

This script scrapes the FitGirl user page on 1337x.to, extracts magnet links directly from torrent pages, and generates an RSS feed that can be used with qBittorrent for automatic downloads.

## Features

- Scrapes the FitGirl user page on 1337x.to
- Extracts magnet links directly from torrent pages
- Focuses only on the 10 most recent torrents
- Stores torrent data in a JSON file for persistence
- Creates an RSS feed with magnet links for qBittorrent
- Respects the website by using random delays between requests

## Automated RSS Feed

This script is automatically run every 30 minutes via GitHub Actions to provide an up-to-date RSS feed of the latest FitGirl torrents.

### Using the RSS Feed in qBittorrent

1. Open qBittorrent
2. Go to View > RSS Reader
3. Click "New subscription"
4. Enter the following URL:
   ```
   https://raw.githubusercontent.com/QuePast/seedbox/main/fitgirl_torrents.xml
   ```
5. Set up auto-downloading rules as needed

The RSS feed contains magnet links for the 10 most recent FitGirl torrents and is updated every 30 minutes.

### GitHub Actions Workflow

The script is automatically run using GitHub Actions:
- Runs every 30 minutes
- Updates the RSS feed with the latest torrents
- Commits and pushes changes to this repository

You can also manually trigger the workflow by going to the Actions tab and running the "Update FitGirl RSS Feed" workflow.

## Requirements

- Python 3.6+
- Required packages: requests, beautifulsoup4

## Installation

1. Clone or download this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Run the script:

```
python main.py
```

2. The script will:
   - Check for new torrents on the FitGirl user page
   - Extract magnet links for new torrents
   - Create/update an RSS feed file (`fitgirl_torrents.xml`)
   - Store torrent data in `torrents_data.json`

3. Set up qBittorrent to use the RSS feed:
   - Open qBittorrent
   - Go to View > RSS Reader
   - Click "New subscription"
   - Enter the path to your `fitgirl_torrents.xml` file as a URL (use the file:// protocol)
   - Set up auto-downloading rules as needed

## Scheduling

You can set up a scheduled task (using cron on Linux or Task Scheduler on Windows) to run the script periodically to check for new torrents.

### Windows Task Scheduler Example

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger (e.g., daily)
4. Set the action to "Start a program"
5. Browse to your Python executable and add the path to the script as an argument

## Notes

- The script is set to process only the 10 most recent torrents. You can change this by modifying the `MAX_TORRENTS` constant.
- The script uses random delays between requests to avoid being blocked.
- Torrent data is saved after each torrent is processed to avoid data loss if the script crashes.

## Disclaimer

This script is for educational purposes only. Only download content that you have the legal right to access. 