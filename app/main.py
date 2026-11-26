import asyncio
import logging

import uvicorn

from app.api import app
from app.database import download_and_parse_database
from app.models import Direction, Station
from app.websocket_client import connect_to_websocket

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main():
  config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")

  server = uvicorn.Server(config)

  await asyncio.gather(
    server.serve(),
    asyncio.create_task(download_and_parse_database()),
    *[
      connect_to_websocket(station, direction)
      for direction in list(Direction)
      for station in list(Station)
    ],
  )


if __name__ == "__main__":
  asyncio.run(main())
