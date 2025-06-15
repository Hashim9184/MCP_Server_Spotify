import os
import webbrowser
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'

print("Spotify Authentication Helper")
print("============================")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("ERROR: Missing Spotify credentials!")
    print("Please make sure you have a .env file with SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
    exit(1)

print(f"Client ID: {SPOTIFY_CLIENT_ID[:5]}...{SPOTIFY_CLIENT_ID[-5:]}")
print(f"Client Secret: {SPOTIFY_CLIENT_SECRET[:3]}...{SPOTIFY_CLIENT_SECRET[-3:]}")
print(f"Redirect URI: {REDIRECT_URI}")
print("\nInitializing authentication...")

# Create the auth manager
auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='user-read-playback-state user-modify-playback-state user-read-currently-playing',
    open_browser=False,
    cache_path='.spotify_cache'
)

# Get the auth URL
auth_url = auth_manager.get_authorize_url()
print("\nPlease open this URL in your browser to authenticate with Spotify:")
print(auth_url)

# Open the URL in the default browser
webbrowser.open(auth_url)

print("\nAfter authenticating, you will be redirected to a URL that starts with:")
print(f"{REDIRECT_URI}?code=...")
print("\nPlease copy the entire URL and paste it here:")

# Wait for the user to paste the URL
callback_url = input("> ")

# Extract the code from the URL
code = None
if "?code=" in callback_url:
    code = callback_url.split("?code=")[1].split("&")[0]

if not code:
    print("ERROR: Could not extract code from URL")
    exit(1)

print("\nGetting access token...")
try:
    # Get the access token
    token_info = auth_manager.get_access_token(code)
    
    # Create a Spotify client to test the token
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Test the token with a simple API call
    user_info = sp.current_user()
    
    print("\nAuthentication successful!")
    print(f"Authenticated as: {user_info['display_name']} ({user_info['id']})")
    print(f"Token saved to: {os.path.abspath('.spotify_cache')}")
    print("\nYou can now run the Spotify MCP server.")
except Exception as e:
    print(f"\nERROR: Authentication failed: {str(e)}")
    exit(1) 