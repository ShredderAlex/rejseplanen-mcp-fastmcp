# Rejseplanen MCP Server (FastMCP)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp)

A [FastMCP](https://github.com/jlowin/fastmcp) server providing integration with the Rejseplanen.dk API 2.0 for Danish public transportation journey planning. This Python-based MCP server uses HTTP transport and can be deployed to cloud platforms like Render and Railway.

## 🚆 Features

This MCP server exposes five tools for interacting with Danish public transport data:

### 🔍 `location_search`
Search for stations, stops, and addresses in Denmark by name.
- **Input**: Search query (station/stop name)
- **Output**: List of matching locations with IDs, coordinates, and types
- **Use case**: Find location IDs needed for trip searches
- **Example**: `location_search(query="København H")`

### 🚄 `trip_search`
Search for public transport journeys between two locations.
- **Input**: Origin ID, destination ID, optional date/time, transport mode filters
- **Output**: Journey options with departure/arrival times, transfers, and detailed routes
- **Use case**: Plan trips using trains, buses, metro, and ferries
- **Example**: `trip_search(origin_id="008600626", dest_id="008600053")`

### 📋 `departure_board`
Get real-time departure information from a specific station.
- **Input**: Station/stop ID, optional date/time
- **Output**: Upcoming departures with times, lines, destinations, and real-time updates
- **Use case**: Check when the next train/bus leaves from a station
- **Example**: `departure_board(station_id="008600626")`

### 📍 `nearby_stops`
Find public transport stops near GPS coordinates.
- **Input**: Latitude, longitude, optional radius and result limit
- **Output**: List of nearby stops with distances and details
- **Use case**: Find the nearest station to a location
- **Example**: `nearby_stops(latitude=55.6761, longitude=12.5683, max_radius=500)`

### ℹ️ `get_server_info`
Get information about the MCP server.
- **Output**: Server version, environment, available tools, and configuration
- **Use case**: Check server status and capabilities

## 🚀 Quick Start

### Local Development

#### Prerequisites
- Python 3.11 or higher
- pip or conda

#### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp.git
   cd rejseplanen-mcp-fastmcp
   ```

2. **Create virtual environment** (recommended):
   ```bash
   # Using conda
   conda create -n rejseplanen-mcp python=3.11
   conda activate rejseplanen-mcp
   
   # OR using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python src/server.py
   ```

   The server will start on `http://localhost:8000`

#### Testing with MCP Inspector

1. **Start the server** (in one terminal):
   ```bash
   python src/server.py
   ```

2. **Launch MCP Inspector** (in another terminal):
   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. **Connect to server**:
   - Open http://localhost:3000 in your browser
   - Select **"Streamable HTTP"** as transport type
   - Enter URL: `http://localhost:8000/mcp` (**NOTE THE `/mcp` PATH!**)
   - Click Connect

4. **Test the tools**:
   - Try `location_search` with query "København H"
   - Use the returned ID in `departure_board` or `trip_search`

## ☁️ Cloud Deployment

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp)

#### Option 1: One-Click Deploy
Click the "Deploy to Render" button above.

#### Option 2: Manual Deployment

1. Fork this repository to your GitHub account
2. Create a [Render](https://render.com) account
3. From your Render dashboard:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub account
   - Select your forked repository
   - Render will automatically detect the `render.yaml` configuration
   - Click **"Create Web Service"**

4. Your server will be available at:
   ```
   https://your-service-name.onrender.com/mcp
   ```

#### Using render.yaml (Infrastructure as Code)

The repository includes a `render.yaml` file for automated deployment:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click **Apply**

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp)

#### Option 1: One-Click Deploy
Click the "Deploy on Railway" button above.

#### Option 2: Manual Deployment

1. Fork this repository to your GitHub account
2. Sign up/login to [Railway](https://railway.app)
3. Create a new project
4. Connect your GitHub repository
5. Railway will automatically detect the `railway.json` configuration
6. (Optional) Set environment variables if needed:
   - **Key**: `REJSEPLANEN_API_KEY` (if API key required in future)
   - **Value**: Your API key
7. Deploy!

Your server will be available at the Railway-provided URL with the `/mcp` endpoint.

#### Using railway.json (Infrastructure as Code)

The repository includes a `railway.json` file that configures:
- Build system (NIXPACKS)
- Start command: `python src/server.py`
- Restart policy with automatic retries

**Note**: The server uses only pure Python dependencies (no Rust compilation required), ensuring fast and reliable builds on Railway's platform.

### Other Deployment Options

This server can be deployed to any platform that supports Python web applications:

- **Heroku**: Add a `Procfile` with `web: python src/server.py`
- **Google Cloud Run**: Build with Docker, expose port 8000
- **AWS Elastic Beanstalk**: Deploy as Python application
- **Fly.io**: Create `fly.toml` configuration

## 🔌 Integration

### With Poke

Connect your deployed MCP server to [Poke](https://poke.com):

1. Go to [poke.com/settings/connections](https://poke.com/settings/connections)
2. Add a new connection:
   - **Name**: `Rejseplanen`
   - **URL**: `https://your-service-name.onrender.com/mcp` (or Railway URL)
   - **Type**: Streamable HTTP
3. Save the connection

**Testing the integration:**
```
Tell the subagent to use the "Rejseplanen" integration's "location_search" tool to find København H
```

**Tip**: If Poke doesn't call the right tools after renaming, send `clearhistory` to delete message history.

### With Claude Desktop (Advanced)

For local HTTP server integration with Claude Desktop, you need a proxy/adapter since Claude Desktop expects stdio transport. Consider using the TypeScript version ([rejseplanen-mcp-server](https://github.com/ShredderAlex/rejseplanen-mcp-server)) for direct Claude Desktop integration.

## 📖 API Reference

This server uses the **Rejseplanen API 2.0**:
- **Base URL**: `https://xmlopen.rejseplanen.dk/bin/rest.exe`
- **Documentation**: [Rejseplanen API 2.0 Docs](https://labs.rejseplanen.dk/hc/da/articles/21554723926557-Om-API-2-0)
- **Format**: JSON responses
- **Rate Limits**: Public API - please use responsibly

## 🎯 Example Workflows

### 1. Find and Plan a Trip
```python
# Step 1: Search for origin
location_search(query="København H")
# Returns: {"LocationList": {"StopLocation": [{"id": "008600626", "name": "København H", ...}]}}

# Step 2: Search for destination
location_search(query="Aarhus H")
# Returns: {"LocationList": {"StopLocation": [{"id": "008600053", "name": "Aarhus H", ...}]}}

# Step 3: Plan the trip
trip_search(origin_id="008600626", dest_id="008600053")
# Returns journey options with times and transfers
```

### 2. Find Nearby Station and Check Departures
```python
# Step 1: Find nearby stops (e.g., at Copenhagen Airport)
nearby_stops(latitude=55.6301, longitude=12.6475, max_radius=500)
# Returns nearby stations with distances

# Step 2: Check departures from the nearest station
departure_board(station_id="008600856")
# Returns upcoming departures with real-time info
```

### 3. Check Current Departures
```python
# Direct lookup if you know the station name
location_search(query="Nørreport")
# Use returned ID for departure board
departure_board(station_id="returned_id")
```

## 🛠️ Development

### Project Structure
```
rejseplanen-mcp-fastmcp/
├── src/
│   └── server.py          # Main FastMCP server implementation
├── .gitignore             # Python gitignore patterns
├── README.md              # This file
├── railway.json           # Railway deployment configuration
├── render.yaml            # Render deployment configuration
└── requirements.txt       # Python dependencies
```

### Adding New Tools

To add a new tool, use the `@mcp.tool()` decorator:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Tool description that will appear in MCP clients.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)
    
    Returns:
        Description of return value
    """
    # Your implementation here
    return {"result": "data"}
```

### Environment Variables

- `PORT`: Server port (default: 8000)
- `ENVIRONMENT`: Environment name (development/production)
- `PYTHON_VERSION`: Python version for deployment
- `REJSEPLANEN_API_KEY`: (Optional) API key if required by Rejseplanen API

## 🧪 Testing

### Manual Testing
```bash
# Start server
python src/server.py

# In another terminal, test with curl
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_server_info", "arguments": {}}}'
```

### With MCP Inspector
See "Testing with MCP Inspector" section above.

## 📊 Monitoring

When deployed to cloud platforms:
- **Render**: View logs in the Render dashboard, monitor memory and CPU usage
- **Railway**: Access logs and metrics in the Railway dashboard
- **Health Check**: Server responds at `/mcp` endpoint

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Alexander Schröder

## 🙏 Acknowledgments

- [Rejseplanen.dk](https://www.rejseplanen.dk/) for providing the public transport API
- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [InteractionCo/mcp-server-template](https://github.com/InteractionCo/mcp-server-template) for the deployment template

## 🆚 Comparison with TypeScript Version

This repository also has a TypeScript/Node.js version: [rejseplanen-mcp-server](https://github.com/ShredderAlex/rejseplanen-mcp-server)

| Feature | FastMCP (This) | TypeScript Version |
|---------|----------------|-------------------|
| **Language** | Python | TypeScript/Node.js |
| **Framework** | FastMCP | @modelcontextprotocol/sdk |
| **Transport** | HTTP (cloud-ready) | stdio (local) |
| **Best For** | Cloud deployment, Poke | Claude Desktop |
| **Deployment** | Render, Railway, etc. | Local npm install |
| **Testing** | MCP Inspector | Claude Desktop |

Choose this version if you want:
- ✅ Cloud deployment capability
- ✅ Integration with Poke or web-based MCP clients
- ✅ Python ecosystem and simplicity
- ✅ HTTP API access

Choose the TypeScript version if you want:
- ✅ Direct Claude Desktop integration
- ✅ Local-only operation
- ✅ Node.js ecosystem
- ✅ stdio transport

## 🔗 Links

- **GitHub Repository**: https://github.com/ShredderAlex/rejseplanen-mcp-fastmcp
- **TypeScript Version**: https://github.com/ShredderAlex/rejseplanen-mcp-server
- **Rejseplanen API Docs**: https://labs.rejseplanen.dk/hc/da/articles/21554723926557-Om-API-2-0
- **FastMCP**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io/
- **Render**: https://render.com
- **Railway**: https://railway.app
- **Poke**: https://poke.com
