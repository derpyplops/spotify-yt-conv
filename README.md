# Spotify to YouTube Music Playlist Converter

A Python tool that converts Spotify playlists to YouTube Music playlists. This tool allows you to easily transfer your favorite playlists between these two music streaming platforms.

## Prerequisites

- Python 3.x
- UV package manager
- Spotify Developer Account
- YouTube Music account
- Browser authentication file for YouTube Music (`browser.json`)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/spotify-yt-conv.git
cd spotify-yt-conv
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Create a `.env` file in the project root with your Spotify API credentials:
```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
```

4. Set up YouTube Music authentication:
   - Follow the [ytmusicapi documentation](https://ytmusicapi.readthedocs.io/en/latest/setup.html) to create your `browser.json` file
   - Place the `browser.json` file in the project root directory

## Usage

1. Run the script:
```bash
python spotify_to_ytmusic.py
```

2. When prompted, enter the Spotify playlist URL you want to convert. The URL should look like:
```
https://open.spotify.com/playlist/3rhmVUKcG2...
```

3. The script will:
   - Create a new YouTube Music playlist
   - Convert all tracks from the Spotify playlist
   - Show progress as it converts each track
   - Display a summary of the conversion results
   - Provide the URL of the newly created YouTube Music playlist
