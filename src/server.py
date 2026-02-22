#!/usr/bin/env python3
"""
Rejseplanen MCP Server

A FastMCP server providing integration with the Rejseplanen.dk API 2.0
for Danish public transportation journey planning.

API Documentation: https://labs.rejseplanen.dk/hc/da/articles/21554723926557-Om-API-2-0
"""

import os
import sys
from typing import Optional, Dict, Any, List
import requests
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "Rejseplanen MCP Server",
    dependencies=["requests"]
)

# Rejseplanen API configuration
REJSEPLANEN_API_BASE = "https://xmlopen.rejseplanen.dk/bin/rest.exe"
REQUEST_TIMEOUT = 30  # seconds


def make_api_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a request to the Rejseplanen API with error handling.
    
    Args:
        endpoint: API endpoint path (e.g., 'location', 'trip')
        params: Query parameters for the request
    
    Returns:
        JSON response from the API
    
    Raises:
        Exception: If the API request fails
    """
    # Always request JSON format
    params['format'] = 'json'
    
    url = f"{REJSEPLANEN_API_BASE}/{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(f"Request to Rejseplanen API timed out after {REQUEST_TIMEOUT} seconds")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Rejseplanen API request failed: {str(e)}")
    except ValueError as e:
        raise Exception(f"Failed to parse JSON response: {str(e)}")


@mcp.tool()
def location_search(query: str) -> Dict[str, Any]:
    """
    Search for stations, stops, and addresses in Denmark by name.
    Returns location IDs needed for trip searches and departure boards.
    
    Args:
        query: Search query for location/station name (e.g., "København H", "Aarhus H")
    
    Returns:
        Dictionary containing:
        - LocationList: Array of matching locations with:
          - id: Location ID (use for trip_search and departure_board)
          - name: Location name
          - x: Longitude coordinate
          - y: Latitude coordinate
          - type: Location type (e.g., 'ST' for station, 'ADR' for address)
    
    Example:
        location_search(query="København H")
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    
    params = {'input': query.strip()}
    return make_api_request('location', params)


@mcp.tool()
def trip_search(
    origin_id: str,
    dest_id: str,
    date: Optional[str] = None,
    time: Optional[str] = None,
    use_train: bool = True,
    use_bus: bool = True,
    use_metro: bool = True,
    use_ferry: bool = True
) -> Dict[str, Any]:
    """
    Search for public transport trips between two locations in Denmark.
    Returns journey options with departure/arrival times, transfers, and detailed route information.
    
    Args:
        origin_id: Origin location ID (from location_search)
        dest_id: Destination location ID (from location_search)
        date: Date in DD.MM.YY format (optional, defaults to today)
        time: Time in HH:MM format (optional, defaults to now)
        use_train: Include trains in search (default: True)
        use_bus: Include buses in search (default: True)
        use_metro: Include metro in search (default: True)
        use_ferry: Include ferries in search (default: True)
    
    Returns:
        Dictionary containing:
        - TripList: Array of trip options with:
          - Trip: Journey details including:
            - Leg: Individual journey legs with transport type, departure/arrival times
            - duration: Total journey time
            - changes: Number of transfers
    
    Example:
        trip_search(origin_id="008600626", dest_id="008600053")
    """
    if not origin_id or not origin_id.strip():
        raise ValueError("origin_id is required")
    if not dest_id or not dest_id.strip():
        raise ValueError("dest_id is required")
    
    params = {
        'originId': origin_id.strip(),
        'destId': dest_id.strip(),
    }
    
    if date:
        params['date'] = date
    if time:
        params['time'] = time
    
    # Transport mode filters (0 = exclude, 1 = include)
    params['useTog'] = '1' if use_train else '0'
    params['useBus'] = '1' if use_bus else '0'
    params['useMetro'] = '1' if use_metro else '0'
    params['useFerry'] = '1' if use_ferry else '0'
    
    return make_api_request('trip', params)


@mcp.tool()
def departure_board(
    station_id: str,
    date: Optional[str] = None,
    time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get real-time departure information from a specific station or stop.
    Shows upcoming departures with times, lines, and destinations.
    
    Args:
        station_id: Station/stop ID (from location_search)
        date: Date in DD.MM.YY format (optional, defaults to today)
        time: Time in HH:MM format (optional, defaults to now)
    
    Returns:
        Dictionary containing:
        - DepartureBoard: Array of departures with:
          - Departure: Individual departure details:
            - name: Line name/number
            - type: Transport type (e.g., 'TOG', 'BUS', 'M')
            - direction: Destination
            - date: Departure date
            - time: Scheduled departure time
            - rtTime: Real-time departure time (if available)
            - track: Platform/track number
    
    Example:
        departure_board(station_id="008600626")
    """
    if not station_id or not station_id.strip():
        raise ValueError("station_id is required")
    
    params = {'id': station_id.strip()}
    
    if date:
        params['date'] = date
    if time:
        params['time'] = time
    
    return make_api_request('departureBoard', params)


@mcp.tool()
def nearby_stops(
    latitude: float,
    longitude: float,
    max_radius: int = 1000,
    max_number: int = 10
) -> Dict[str, Any]:
    """
    Find public transport stops near a given GPS coordinate.
    Useful for finding the nearest stations to a location.
    
    Args:
        latitude: Latitude coordinate (e.g., 55.6761 for Copenhagen)
        longitude: Longitude coordinate (e.g., 12.5683 for Copenhagen)
        max_radius: Maximum search radius in meters (default: 1000, max: 10000)
        max_number: Maximum number of results to return (default: 10, max: 50)
    
    Returns:
        Dictionary containing:
        - StopLocation: Array of nearby stops with:
          - id: Stop ID (use for departure_board)
          - name: Stop name
          - x: Longitude
          - y: Latitude
          - distance: Distance from search point in meters
    
    Example:
        nearby_stops(latitude=55.6761, longitude=12.5683, max_radius=500)
    """
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    
    # Validate and limit radius
    if max_radius < 1:
        raise ValueError("max_radius must be at least 1 meter")
    if max_radius > 10000:
        max_radius = 10000  # API limit
    
    # Validate and limit number of results
    if max_number < 1:
        raise ValueError("max_number must be at least 1")
    if max_number > 50:
        max_number = 50  # Reasonable limit
    
    params = {
        'coordX': str(longitude),
        'coordY': str(latitude),
        'maxRadius': str(max_radius),
        'maxNumber': str(max_number)
    }
    
    return make_api_request('stopsNearby', params)


@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """
    Get information about this MCP server including version, environment, and capabilities.
    
    Returns:
        Dictionary containing server metadata
    """
    return {
        "server_name": "Rejseplanen MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": sys.version.split()[0],
        "api_base": REJSEPLANEN_API_BASE,
        "transport": "HTTP (Stateless)",
        "tools": [
            "location_search",
            "trip_search",
            "departure_board",
            "nearby_stops",
            "get_server_info"
        ],
        "description": "MCP server for Danish public transportation via Rejseplanen.dk API 2.0"
    }


if __name__ == "__main__":
    # Get port from environment variable (used by Render and other cloud platforms)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Listen on all interfaces for cloud deployment
    
    print(f"🚆 Starting Rejseplanen MCP Server on {host}:{port}")
    print(f"📍 API Endpoint: http://{host}:{port}/mcp")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print(f"🔧 Python Version: {sys.version.split()[0]}")
    print("\n✅ Server ready to accept connections...\n")
    
    # Run the FastMCP server with HTTP transport
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True  # Required for cloud deployment
    )
