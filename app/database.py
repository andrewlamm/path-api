import asyncio
import io
import logging
import os
import sqlite3
import zipfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import aiofiles
import aiohttp
import state
from models import (
  DayOfWeek,
  Direction,
  RouteDetails,
  RouteStopDetailsForStation,
  ServiceException,
  ServiceExceptionType,
  ServiceIdDates,
  Station,
  StationInfo,
)

logger = logging.getLogger(__name__)

FETCH_URL = "https://path-mppprod-app.azurewebsites.net/api/v3/Config/Fetch"
DATAFILE_URL = "https://path-mppprod-app.azurewebsites.net/api/v3/file/datafile"

# Hard coded constants from the RidePATH app. Note that the db checksum is different
# from the checksum we receive from the fetch endpoint; I'm not sure exactly why
AUTH_KEY = "a9fc79c6-a434-4124-a7d6-6b3008105bf9"
DB_CHECKSUM = "A45AD870A7E2C5981AE1D235183C26D8"
SCRIPT_CHECKSUM = "EEE8EFEC7A991933381391711CCF307B"

APP_VERSION = "6.2.2"
APP_INSTALL_ID = "5f5cb413ed19218f"

DATABASE_PATH = "data/path.db"


async def fetch_checksum(session):
  response = await session.get(
    FETCH_URL,
    headers={
      "AuthKey": AUTH_KEY,
      "AppVersion": APP_VERSION,
      "AppInstallId": APP_INSTALL_ID,
      "dbChecksum": DB_CHECKSUM,
      "scriptChecksum": SCRIPT_CHECKSUM,
    },
  )

  data = await response.json()

  db_update = data.get("data").get("db-update")

  if db_update is not None:
    return db_update.get("db-checksum")
  return None


async def fetch_datafile(session, checksum):
  response = await session.post(
    DATAFILE_URL,
    headers={
      "Content-Type": "application/json; charset=utf-8",
      "AuthKey": AUTH_KEY,
      "AppVersion": APP_VERSION,
    },
    json={"checksum": checksum, "type": "database"},
  )

  content = await response.read()

  with zipfile.ZipFile(io.BytesIO(content)) as z:
    logger.info(f"Files in ZIP: {z.namelist()}")

    bad_file = z.testzip()
    if bad_file:
      raise Exception(f"Corrupt ZIP member: {bad_file}")  # noqa: TRY002

    for filename in z.namelist():
      if filename.endswith(".db"):
        os.makedirs("data", exist_ok=True)

        with z.open(filename) as src:
          async with aiofiles.open(DATABASE_PATH, "wb") as dst:
            await dst.write(src.read())

        logger.info("Database extracted!")
        return

    raise Exception("No .db file found in ZIP")  # noqa: TRY002


async def read_from_database():
  def parse_date(date_str):
    return datetime.strptime(date_str, "%Y%m%d").date()

  def time_to_seconds_after_midnight(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

  with sqlite3.connect(DATABASE_PATH) as conn:
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
      'SELECT stop_id, stop_name, stop_lat, stop_lon FROM "gtfs.base.stops"'
    )
    rows = cursor.fetchall()
    stop_info_by_id: dict[str, StationInfo] = {
      row["stop_id"]: {
        "station": Station.of_path_api_string(row["stop_name"]),
        "stop_lat": float(row["stop_lat"]),
        "stop_lon": float(row["stop_lon"]),
      }
      for row in rows
    }

    cursor.execute(
      'SELECT service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date FROM "gtfs.base.calendar"'
    )
    rows = cursor.fetchall()
    calendar_service_ids: dict[str, ServiceIdDates] = {
      row["service_id"]: {
        "start_date": parse_date(row["start_date"]),
        "end_date": parse_date(row["end_date"]),
        "valid_for": {
          DayOfWeek.MONDAY: row["monday"] == "1",
          DayOfWeek.TUESDAY: row["tuesday"] == "1",
          DayOfWeek.WEDNESDAY: row["wednesday"] == "1",
          DayOfWeek.THURSDAY: row["thursday"] == "1",
          DayOfWeek.FRIDAY: row["friday"] == "1",
          DayOfWeek.SATURDAY: row["saturday"] == "1",
          DayOfWeek.SUNDAY: row["sunday"] == "1",
        },
      }
      for row in rows
    }

    cursor.execute(
      'SELECT service_id, date, exception_type FROM "gtfs.base.calendar_dates"'
    )
    rows = cursor.fetchall()
    calendar_exceptions: dict[date, list[ServiceException]] = {}
    for row in rows:
      row_date = parse_date(row["date"])
      if row_date not in calendar_exceptions:
        calendar_exceptions[row_date] = []

      exception_type = None
      if int(row["exception_type"]) == 1:
        exception_type = ServiceExceptionType.ADD
      elif int(row["exception_type"]) == 2:
        exception_type = ServiceExceptionType.REMOVE
      else:
        raise Exception(f"Unknown exception_type: {row['exception_type']}")  # noqa: TRY002

      calendar_exceptions[row_date].append(
        {
          "service_id": row["service_id"],
          "type_": exception_type,
        }
      )

    cursor.execute(
      'SELECT service_id, trip_id, route_long_name, trip_headsign, stop_id, arrival_time, departure_time, stop_sequence, direction_id FROM "gtfs.custom.vw_schedules" ORDER BY trip_id, stop_sequence'
    )
    rows = cursor.fetchall()
    schedules_by_service_id: dict[str, list[RouteDetails]] = {}
    stop_times_for_service_id_and_stop_id: dict[
      str, dict[tuple[Station, Direction], list[RouteStopDetailsForStation]]
    ] = {}
    for row in rows:
      service_id = row["service_id"]
      trip_id = row["trip_id"]
      stop_id = row["stop_id"]
      arrival_seconds_after_midnight = time_to_seconds_after_midnight(
        row["arrival_time"]
      )
      departure_seconds_after_midnight = time_to_seconds_after_midnight(
        row["departure_time"]
      )
      direction_id = int(row["direction_id"])
      route_long_name = row["route_long_name"]
      trip_headsign = row["trip_headsign"]

      direction = None
      if direction_id == 0:
        direction = Direction.TO_NY
      elif direction_id == 1:
        direction = Direction.TO_NJ
      else:
        raise Exception(f"Unknown direction_id: {direction_id}")  # noqa: TRY002

      if service_id not in schedules_by_service_id:
        schedules_by_service_id[service_id] = []

      if service_id not in stop_times_for_service_id_and_stop_id:
        stop_times_for_service_id_and_stop_id[service_id] = {}

      if (
        len(schedules_by_service_id[service_id]) == 0
        or schedules_by_service_id[service_id][-1]["trip_id"] != trip_id
      ):
        schedules_by_service_id[service_id].append(
          {
            "trip_id": trip_id,
            "route_long_name": route_long_name,
            "trip_headsign": trip_headsign,
            "direction": direction,
            "stops": [],
          }
        )

      schedules_by_service_id[service_id][-1]["stops"].append(
        {
          "stop_id": stop_id,
          "arrival_seconds_after_midnight": arrival_seconds_after_midnight,
          "departure_seconds_after_midnight": departure_seconds_after_midnight,
        }
      )

      station = stop_info_by_id[stop_id]["station"]

      if (station, direction) not in stop_times_for_service_id_and_stop_id[
        service_id
      ]:
        stop_times_for_service_id_and_stop_id[service_id][
          (station, direction)
        ] = []

      stop_times_for_service_id_and_stop_id[service_id][
        (station, direction)
      ].append(
        {
          "trip_id": trip_id,
          "trip_headsign": trip_headsign,
          "arrival_seconds_after_midnight": arrival_seconds_after_midnight,
          "departure_seconds_after_midnight": departure_seconds_after_midnight,
        }
      )

    state.stop_info_by_id = stop_info_by_id
    state.calendar_service_ids = calendar_service_ids
    state.calendar_exceptions = calendar_exceptions
    state.schedules_by_service_id = schedules_by_service_id
    state.stop_times_for_service_id_and_stop_id = (
      stop_times_for_service_id_and_stop_id
    )


async def download_and_parse_database():
  tz = ZoneInfo("America/New_York")
  while True:
    try:
      async with aiohttp.ClientSession() as session:
        checksum = await fetch_checksum(session)
        if checksum is None:
          logger.info("No database update available.")
          return

        if checksum == state.database_checksum:
          logger.info("Database is already up to date.")
          return

        logger.info(f"Fetching new database with checksum: {checksum}")
        await fetch_datafile(session, checksum)
        state.database_checksum = checksum

        await read_from_database()

        # wait until next day 12am
        now = datetime.now(tz)
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time(), tzinfo=tz)

        seconds = (midnight - now).total_seconds()
        logger.info(f"Next database update in {seconds / 3600:.2f} hours")

        await asyncio.sleep(seconds)
    except Exception as e:  # noqa: BLE001
      logger.error(f"Read from database failed, retrying after 30 seconds: {e}")
      await asyncio.sleep(30)
