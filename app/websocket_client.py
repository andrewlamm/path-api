import asyncio
import datetime
import json
import logging

import aiohttp
import state
import websockets
from estimate_trains import estimate_trains
from models import Direction, RealTimeArrival, Station

logger = logging.getLogger(__name__)


TOKEN_REQUEST_URL = "https://panynj-path-af-tb.azurewebsites.net/api/tokenrequest?TKrTIgWSdgikIrqvftckyOh"
API_KEY = "57bec8f4-8ba4-408a-9d53-8d545281badd"
APP_VERSION = "6.2.2"


async def get_token(session, station: Station, direction: Direction):
  response = await session.post(
    TOKEN_REQUEST_URL,
    headers={"Authorization": f"Bearer {API_KEY}", "AppVersion": APP_VERSION},
    json={
      "station": Station.to_path_api_string(station),
      "direction": Direction.to_path_api_string(direction),
    },
  )
  return await response.json()


async def negotiate_connection_token(session, url, token):
  response = await session.post(
    url,
    params={"hub": "pany", "negotiateVersion": "1"},
    headers={
      "Authorization": f"Bearer {token}",
      "User-Agent": "Microsoft SignalR/9.0",
    },
  )
  data = await response.json()
  return data["connectionToken"]


async def get_websocket_url(session, station: Station, direction: Direction):
  token_data = await get_token(session, station, direction)

  url = token_data["Url"]
  token = token_data["AccessToken"]

  negotiate_url = f"{url.split('?')[0]}negotiate"

  connection_token = await negotiate_connection_token(
    session, negotiate_url, token
  )

  websocket_url = (
    f"{url.replace('https', 'wss')}&id={connection_token}&access_token={token}"
  )

  return websocket_url


async def connect_to_websocket(station: Station, direction: Direction):
  while True:
    try:
      websocket_url = None

      async with aiohttp.ClientSession() as session:
        websocket_url = await get_websocket_url(session, station, direction)

      async with websockets.connect(websocket_url) as ws:
        await ws.send('{"protocol":"json","version":1}\x1e')

        logger.info(
          f"Connected to websocket for {station}, {direction}, waiting for messages..."
        )
        loaded = False

        while True:
          raw_message = await ws.recv()
          data = json.loads(raw_message.strip())
          event_type = data.get("type")

          if event_type == 1:
            if not loaded:
              logger.info(f"Received first message for {station}, {direction}")
              loaded = True

            trains_raw = json.loads(data["arguments"][1])["messages"]

            trains: list[RealTimeArrival] = [
              {
                "seconds_until_arrival": int(train["secondsToArrival"]),
                "arrival_time_message": train["arrivalTimeMessage"],
                "line_colors": train["lineColor"].split(","),
                "headsign": train["headSign"],
                "last_updated": datetime.datetime.fromisoformat(
                  train["lastUpdated"]
                ),
                "is_estimated": False,
              }
              for train in trains_raw
            ]

            state.realtime_by_station_dir[(station, direction)] = trains

            await estimate_trains()
    except Exception as e:  # noqa: BLE001
      logger.error(f"Connection failed ({station}, {direction}): {e}")
      await asyncio.sleep(3)
