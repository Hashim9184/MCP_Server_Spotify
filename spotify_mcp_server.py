import os
import sys
import json
import logging
import time
from flask import Flask, request, jsonify, Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import threading

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("spotify_mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Disable Flask's built-in logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Load environment variables
logger.info("Loading environment variables")
load_dotenv()

app = Flask(__name__)

# Disable Flask's default output
app.logger.disabled = True
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'

logger.info(f"Client ID available: {bool(SPOTIFY_CLIENT_ID)}")
logger.info(f"Client Secret available: {bool(SPOTIFY_CLIENT_SECRET)}")

# Global variable to store the Spotify client
sp = None
auth_manager = None

def initialize_spotify():
    global sp, auth_manager
    try:
        logger.info("Initializing Spotify client")
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope='user-read-playback-state user-modify-playback-state user-read-currently-playing',
            open_browser=False,
            cache_path='.spotify_cache'
        )
        
        # Check if we have a cached token
        token_info = auth_manager.get_cached_token()
        
        if not token_info or auth_manager.is_token_expired(token_info):
            logger.info("No valid token found, need to authenticate")
            auth_url = auth_manager.get_authorize_url()
            logger.info(f"Please visit this URL to authenticate: {auth_url}")
            
            # Create a simple HTML page with the auth URL
            with open('auth.html', 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Spotify Authentication</title>
                </head>
                <body>
                    <h1>Spotify Authentication Required</h1>
                    <p>Please click the link below to authenticate with Spotify:</p>
                    <a href="{auth_url}" target="_blank">Authenticate with Spotify</a>
                </body>
                </html>
                """)
            
            logger.info("Created auth.html file with authentication link")
            
            # Wait for authentication to complete
            for _ in range(60):  # Wait up to 5 minutes
                token_info = auth_manager.get_cached_token()
                if token_info and not auth_manager.is_token_expired(token_info):
                    break
                time.sleep(5)
            
            if not token_info or auth_manager.is_token_expired(token_info):
                logger.error("Authentication timed out")
                return False
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        logger.info("Spotify client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing Spotify client: {str(e)}")
        return False

# Initialize Spotify on startup
initialize_spotify()

# Periodically check and refresh the token
def token_refresh_thread():
    global sp, auth_manager
    while True:
        try:
            if auth_manager:
                token_info = auth_manager.get_cached_token()
                if token_info and auth_manager.is_token_expired(token_info):
                    logger.info("Refreshing expired token")
                    auth_manager.refresh_access_token(token_info['refresh_token'])
                    sp = spotipy.Spotify(auth_manager=auth_manager)
                    logger.info("Token refreshed successfully")
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in token refresh thread: {str(e)}")
            time.sleep(30)  # Wait a bit before retrying

# Start the token refresh thread
refresh_thread = threading.Thread(target=token_refresh_thread, daemon=True)
refresh_thread.start()

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        try:
            auth_manager.get_access_token(code)
            global sp
            sp = spotipy.Spotify(auth_manager=auth_manager)
            return "Authentication successful! You can close this window."
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
            return f"Authentication failed: {str(e)}"
    return "No code provided"

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check endpoint called")
    if sp:
        try:
            # Try a simple API call to verify the connection
            devices = sp.devices()
            return jsonify({"status": "healthy", "spotify_client": "connected"})
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            # Try to reinitialize the client
            if initialize_spotify():
                return jsonify({"status": "recovered", "message": "Reinitialized Spotify client"})
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    else:
        # Try to initialize the client
        if initialize_spotify():
            return jsonify({"status": "recovered", "message": "Initialized Spotify client"})
        return jsonify({"status": "unhealthy", "spotify_client": "disconnected"}), 500

@app.route('/play', methods=['POST'])
def play_track():
    try:
        logger.info("Play track endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        data = request.get_json()
        track_uri = data.get('track_uri')
        
        if not track_uri:
            logger.warning("No track URI provided")
            return jsonify({"error": "No track URI provided"}), 400
            
        logger.info(f"Playing track: {track_uri}")
        sp.start_playback(uris=[track_uri])
        return jsonify({"status": "success", "message": "Track started playing"})
    except Exception as e:
        logger.error(f"Error playing track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/pause', methods=['POST'])
def pause_track():
    try:
        logger.info("Pause track endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        sp.pause_playback()
        return jsonify({"status": "success", "message": "Playback paused"})
    except Exception as e:
        logger.error(f"Error pausing track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/next', methods=['POST'])
def next_track():
    try:
        logger.info("Next track endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        sp.next_track()
        return jsonify({"status": "success", "message": "Skipped to next track"})
    except Exception as e:
        logger.error(f"Error skipping to next track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/previous', methods=['POST'])
def previous_track():
    try:
        logger.info("Previous track endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        sp.previous_track()
        return jsonify({"status": "success", "message": "Skipped to previous track"})
    except Exception as e:
        logger.error(f"Error skipping to previous track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/current_track', methods=['GET'])
def get_current_track():
    try:
        logger.info("Current track endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        current_playback = sp.current_playback()
        if current_playback and current_playback['item']:
            track = current_playback['item']
            return jsonify({
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "uri": track['uri'],
                "progress_ms": current_playback['progress_ms'],
                "duration_ms": track['duration_ms']
            })
        logger.warning("No track currently playing")
        return jsonify({"error": "No track currently playing"}), 404
    except Exception as e:
        logger.error(f"Error getting current track: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_tracks():
    try:
        logger.info("Search tracks endpoint called")
        if not sp:
            if not initialize_spotify():
                return jsonify({"error": "Spotify client not initialized"}), 500
        
        query = request.args.get('q')
        if not query:
            logger.warning("No search query provided")
            return jsonify({"error": "No search query provided"}), 400
            
        logger.info(f"Searching for: {query}")
        results = sp.search(q=query, type='track', limit=5)
        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "uri": track['uri']
            })
        return jsonify({"tracks": tracks})
    except Exception as e:
        logger.error(f"Error searching tracks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auth', methods=['GET'])
def auth_page():
    try:
        auth_url = auth_manager.get_authorize_url()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Authentication</title>
        </head>
        <body>
            <h1>Spotify Authentication Required</h1>
            <p>Please click the link below to authenticate with Spotify:</p>
            <a href="{auth_url}" target="_blank">Authenticate with Spotify</a>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"Error generating auth page: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    logger.info("Starting Spotify MCP Server on port 8888")
    app.run(host='0.0.0.0', port=8888, debug=False, threaded=True) 