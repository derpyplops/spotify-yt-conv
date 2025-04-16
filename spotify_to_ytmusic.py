import os
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic, OAuthCredentials
from dotenv import load_dotenv
import re
from tqdm import tqdm
import logging
from datetime import datetime

def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extract the Spotify playlist ID from a URL.
    
    Args:
        url (str): Spotify playlist URL
        
    Returns:
        Optional[str]: Playlist ID if found, None otherwise
    """
    # Match Spotify playlist URLs
    pattern = r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def convert_spotify_to_ytmusic(spotify_playlist_url: str) -> Optional[str]:
    """
    Convert a Spotify playlist to a YouTube Music playlist.
    
    Args:
        spotify_playlist_url (str): The URL of the Spotify playlist to convert
        
    Returns:
        Optional[str]: The URL of the created YouTube Music playlist, or None if conversion fails
    """
    # Set up logging
    log_filename = f"conversion_failures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    
    # Load environment variables
    load_dotenv()
    
    # Extract playlist ID
    playlist_id = extract_playlist_id(spotify_playlist_url)
    if not playlist_id:
        print("Invalid Spotify playlist URL. Please provide a valid Spotify playlist URL.")
        return None
    
    try:
        # Initialize Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope='playlist-read-private'
        ))
        
        # Initialize YouTube Music client
        try:
            print("\nDebug - Initializing YouTube Music client...")
            # First try with browser.json if it exists
        
            print("Using browser.json for authentication")
            ytmusic = YTMusic("browser.json")
            print("YouTube Music client initialized successfully")
        except Exception as e:
            print(f"\nError initializing YouTube Music client: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                print("\nAPI Response details:")
                print(f"Status code: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"Response headers: {getattr(e.response, 'headers', 'N/A')}")
                if hasattr(e.response, 'text'):
                    print(f"Response text: {e.response.text}")
            return None

        # Get Spotify playlist details
        try:
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist['name']
            playlist_description = playlist.get('description', '')
        except spotipy.SpotifyException as e:
            print(f"Error accessing Spotify playlist: {str(e)}")
            return None
        
        # Get all tracks from the playlist
        tracks = []
        try:
            results = sp.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])
        except spotipy.SpotifyException as e:
            print(f"Error fetching playlist tracks: {str(e)}")
            return None
        
        if not tracks:
            print("No tracks found in the playlist.")
            return None
        
        # Create a new YouTube Music playlist
        try:
            print("Creating YouTube Music playlist with:")
            print(f"Title: {playlist_name}")
            print(f"Description length: {len(playlist_description)}")
            print(f"Description preview: {playlist_description[:100]}...")
            
            # Ensure playlist name is not empty and within length limits
            if not playlist_name or len(playlist_name) > 150:
                playlist_name = "Converted Spotify Playlist"
            
            # Ensure description is within length limits
            description = f"Converted from Spotify playlist: {playlist_name}"
            if playlist_description:
                description += f"\n{playlist_description[:500]}"  # Truncate if too long
            
            # Check if playlist already exists
            existing_playlists = ytmusic.get_library_playlists()
            ytmusic_playlist_id = None
            
            for existing_playlist in existing_playlists:
                if existing_playlist['title'] == playlist_name:
                    ytmusic_playlist_id = existing_playlist['playlistId']
                    print(f"Found existing playlist with ID: {ytmusic_playlist_id}")
                    break
            
            if not ytmusic_playlist_id:
                # Create the YouTube Music playlist if it doesn't exist
                ytmusic_playlist_id = ytmusic.create_playlist(
                    title=playlist_name,
                    description=description,
                    privacy_status="PRIVATE"  # Explicitly set privacy status
                )
                print(f"Created new playlist with ID: {ytmusic_playlist_id}")
            
            # Get existing tracks in the playlist to avoid duplicates
            existing_tracks = set()
            try:
                playlist_tracks = ytmusic.get_playlist(ytmusic_playlist_id)['tracks']
                for track in playlist_tracks:
                    existing_tracks.add(track['videoId'])
                print(f"Found {len(existing_tracks)} existing tracks in the playlist")
            except Exception as e:
                print(f"Warning: Could not fetch existing tracks: {str(e)}")
            
        except Exception as e:
            print(f"\nError handling playlist: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                print("\nAPI Response details:")
                print(f"Status code: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"Response headers: {getattr(e.response, 'headers', 'N/A')}")
                if hasattr(e.response, 'text'):
                    print(f"Response text: {e.response.text}")
            return None
        
        # Search and add each track to YouTube Music playlist
        added_tracks = 0
        skipped_tracks = 0
        total_tracks = len(tracks)
        print(f"\nStarting to add {total_tracks} tracks to the playlist...")
        
        for track in tqdm(tracks, desc="Converting tracks", unit="track"):
            track_info = track['track']
            if not track_info:  # Skip if track is None (can happen with deleted tracks)
                logging.info(f"Skipped track - Track info is None")
                continue
                
            # Create search query
            artist_name = track_info['artists'][0]['name']
            track_name = track_info['name']
            search_query = f"{track_name} {artist_name}"
            
            try:
                # Search for the track on YouTube Music
                search_results = ytmusic.search(search_query, filter="songs", limit=1)
                
                if search_results:
                    video_id = search_results[0]['videoId']
                    
                    # Check if track already exists in playlist
                    if video_id in existing_tracks:
                        skipped_tracks += 1
                        continue
                        
                    ytmusic.add_playlist_items(ytmusic_playlist_id, [video_id])
                    existing_tracks.add(video_id)  # Add to our tracking set
                    added_tracks += 1
                else:
                    logging.info(f"No match found for: {track_name} by {artist_name}")
            except Exception as e:
                logging.error(f"Error adding track '{track_name}' by '{artist_name}': {str(e)}")
                continue
        
        print(f"\nConversion complete!")
        print(f"Successfully added {added_tracks} new tracks")
        print(f"Skipped {skipped_tracks} existing tracks")
        print(f"Total tracks in playlist: {len(existing_tracks)}")
        print(f"Failed conversions logged to: {log_filename}")
        return f"https://music.youtube.com/playlist?list={ytmusic_playlist_id}"
    
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        print("\nInitializing YouTube Music client with browser authentication...")
        if not os.path.exists("browser.json"):
            print("Error: browser.json not found")
            return
            
        ytmusic = YTMusic("browser.json")
        
        # Then try to get playlists
        print("\nTesting playlist access...")
        playlists = ytmusic.get_library_playlists(limit=5)
        print("\nFound playlists:")
        for playlist in playlists:
            print(f"- {playlist['title']} (ID: {playlist['playlistId']})")

        print("Enter the Spotify playlist URL. It should look like")
        print("https://open.spotify.com/playlist/3rhmVUKcG2...")
        spotify_playlist_url = input("URL:")
        convert_spotify_to_ytmusic(spotify_playlist_url)
            

    except Exception as e:
        print(f"\nError: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print("\nAPI Response details:")
            print(f"Status code: {getattr(e.response, 'status_code', 'N/A')}")
            print(f"Response headers: {getattr(e.response, 'headers', 'N/A')}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    main() 