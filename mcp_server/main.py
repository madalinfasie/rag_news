import requests
import settings
from fastmcp import FastMCP

mcp = FastMCP("Weather")

WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1/current.json"


@mcp.tool()
def current_weather(location: str) -> dict:
    """Get the current weather information for a given location"""
    print(f"Current weather tool called for location {location}")

    res = requests.get(
        WEATHER_API_BASE_URL,
        params={
            "q": location,
            "aqi": "yes",
            "key": settings.WEATHER_API_KEY,
        },
    )

    res.raise_for_status()

    return res.json().get("current", {})


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
