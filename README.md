# Spotify MCP Server for Claude Desktop

A Message Control Protocol (MCP) server that enables Claude Desktop to control Spotify playback through natural language commands.

## Features

- Control Spotify playback (play, pause, next, previous)
- Search for tracks
- Get current track information
- Automatic token refresh
- Robust error handling and logging
- Easy authentication process

## Prerequisites

- Python 3.7 or higher
- Spotify Premium account
- Spotify Developer account
- Claude Desktop

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spotify-mcp-server.git
cd spotify-mcp-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Spotify Developer credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Add `http://localhost:8888/callback` as a redirect URI
   - Copy your Client ID and Client Secret

4. Create a `.env` file:
```bash
cp .env.example .env
```
Then edit `.env` and add your Spotify credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

## Usage

1. Authenticate with Spotify:
```bash
python authenticate_spotify.py
```
Follow the prompts to complete authentication.

2. Start the MCP server:
```bash
python run_spotify_server.py
```

3. Configure Claude Desktop:
   - Copy `claude_mcp_config.json` to Claude Desktop's MCP configuration directory:
     - Windows: `%APPDATA%\Claude Desktop\mcp\`
     - macOS: `~/Library/Application Support/Claude Desktop/mcp/`
     - Linux: `~/.config/Claude Desktop/mcp/`
   - Restart Claude Desktop

4. Use Claude Desktop to control Spotify with commands like:
   - "Play Bohemian Rhapsody on Spotify"
   - "Pause the music"
   - "Skip to next track"
   - "What song is currently playing?"

## Testing

Run the test script to verify the server is working:
```bash
python test_spotify_server.py
```

## Project Structure

```
spotify-mcp-server/
├── README.md
├── requirements.txt
├── .env.example
├── claude_mcp_config.json
├── spotify_mcp_server.py      # Main server implementation
├── run_spotify_server.py      # Server wrapper script
├── authenticate_spotify.py    # Authentication helper
└── test_spotify_server.py     # Test script
```

## Logging

The server generates several log files:
- `spotify_mcp_server.log`: Main server logs
- `server_output.log`: Server stdout/stderr
- `wrapper_error.log`: Wrapper script errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spotipy](https://github.com/spotipy-dev/spotipy) - Python library for the Spotify Web API
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Claude Desktop](https://claude.ai/) - AI assistant 