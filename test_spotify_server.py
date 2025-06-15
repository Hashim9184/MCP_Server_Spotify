import requests
import json
import sys

BASE_URL = "http://localhost:8888"

def test_health():
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_search(query):
    print(f"\nTesting search for '{query}'...")
    try:
        response = requests.get(f"{BASE_URL}/search", params={"q": query})
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            tracks = response.json().get("tracks", [])
            if tracks:
                print("Found tracks:")
                for i, track in enumerate(tracks, 1):
                    print(f"{i}. {track['name']} by {track['artist']} (URI: {track['uri']})")
                return True, tracks[0]['uri'] if tracks else None
            else:
                print("No tracks found")
                return False, None
        else:
            print(f"Response: {response.json()}")
            return False, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, None

def test_play(track_uri):
    print(f"\nTesting play track '{track_uri}'...")
    try:
        response = requests.post(f"{BASE_URL}/play", json={"track_uri": track_uri})
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_current_track():
    print("\nTesting current track...")
    try:
        response = requests.get(f"{BASE_URL}/current_track")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            track = response.json()
            print(f"Currently playing: {track['name']} by {track['artist']}")
            print(f"Progress: {track['progress_ms']/1000:.1f}s / {track['duration_ms']/1000:.1f}s")
            return True
        else:
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_pause():
    print("\nTesting pause...")
    try:
        response = requests.post(f"{BASE_URL}/pause")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_next():
    print("\nTesting next track...")
    try:
        response = requests.post(f"{BASE_URL}/next")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_previous():
    print("\nTesting previous track...")
    try:
        response = requests.post(f"{BASE_URL}/previous")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    print("Spotify MCP Server Test")
    print("======================")
    
    # Test health
    if not test_health():
        print("\nServer health check failed. Make sure the server is running.")
        return
    
    # Test search
    search_query = "Bohemian Rhapsody"
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
    
    success, track_uri = test_search(search_query)
    if not success or not track_uri:
        print("\nSearch test failed or no tracks found.")
        return
    
    # Test play
    if not test_play(track_uri):
        print("\nPlay test failed.")
        return
    
    # Wait a moment for the track to start playing
    import time
    print("\nWaiting 3 seconds for track to start playing...")
    time.sleep(3)
    
    # Test current track
    test_current_track()
    
    # Test pause
    test_pause()
    
    # Wait a moment
    print("\nWaiting 2 seconds...")
    time.sleep(2)
    
    # Test next
    test_next()
    
    # Wait a moment
    print("\nWaiting 2 seconds...")
    time.sleep(2)
    
    # Test previous
    test_previous()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 