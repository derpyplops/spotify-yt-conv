# Spotify to YouTube Music Playlist Converter

This script allows you to convert your Spotify playlists to YouTube Music playlists.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Spotify API credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Get your Client ID and Client Secret
   - Add a redirect URI (e.g., http://localhost:8888/callback)
   - Create a `.env` file with the following content:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=your_redirect_uri
   ```

3. Set up YouTube Music authentication:
   - Run the following command in your terminal:
   ```bash
   python -c "from ytmusicapi import YTMusic; YTMusic.setup(filepath='oauth.json')"
   ```
   - Follow the instructions to complete the authentication process
   - This will create an `oauth.json` file in your current directory

## Usage

1. Run the script:
```bash
python spotify_to_ytmusic.py
```

2. When prompted, enter the Spotify playlist URL you want to convert
   - The URL should look like: `https://open.spotify.com/playlist/37i9dQZF1DX5KpP2LN299J`

3. The script will create a new private playlist in your YouTube Music account and add all the matching songs it finds

## Notes

- The script creates the YouTube Music playlist as private by default
- Some songs might not be found on YouTube Music due to different naming or availability
- The script handles pagination for Spotify playlists of any size
- Error handling is implemented to prevent crashes due to API issues or missing tracks 