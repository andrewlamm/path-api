from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import FastAPI

from app import state
from app.models import (
  ApiError,
  ApiSuccess,
  DayOfWeek,
  Direction,
  RealTimeArrival,
  RouteStopDetailsForStation,
  RouteStopDetailsForStationWithTimestamp,
  ServiceExceptionType,
  Station,
)

app = FastAPI()


async def serve_api(f):
  try:
    message = f()
    return {"success": True, "message": message}
  except Exception as e:  # noqa: BLE001
    return {"success": False, "error_message": str(e)}


def get_sorted_routes(
  routes: dict[tuple[Station, Direction], list[RealTimeArrival]],
  station: Station,
  direction: Direction,
):
  return sorted(
    routes.get((station, direction), []),
    key=lambda x: x["seconds_until_arrival"],
  )


@app.get(
  "/realtime",
  response_model=ApiSuccess[
    dict[Station, dict[Direction, list[RealTimeArrival]]]
  ]
  | ApiError,
)
async def get_realtimes():
  def f():
    return {
      station: {
        Direction.TO_NJ: get_sorted_routes(
          state.realtime_by_station_dir, station, Direction.TO_NJ
        ),
        Direction.TO_NY: get_sorted_routes(
          state.realtime_by_station_dir, station, Direction.TO_NY
        ),
      }
      for station in list(Station)
    }

  return await serve_api(f)


@app.get(
  "/realtime/{station}",
  response_model=ApiSuccess[dict[Direction, list[RealTimeArrival]]] | ApiError,
)
async def get_realtime_for_station(station: Station):
  def f():
    return {
      Direction.TO_NJ: get_sorted_routes(
        state.realtime_by_station_dir, station, Direction.TO_NJ
      ),
      Direction.TO_NY: get_sorted_routes(
        state.realtime_by_station_dir, station, Direction.TO_NY
      ),
    }

  return await serve_api(f)


@app.get(
  "/realtime/{station}/{direction}",
  response_model=ApiSuccess[list[RealTimeArrival]] | ApiError,
)
async def get_realtime_for_station_and_direction(
  station: Station, direction: Direction
):
  def f():
    return get_sorted_routes(state.realtime_by_station_dir, station, direction)

  return await serve_api(f)


@app.get(
  "/realtime_with_estimates",
  response_model=ApiSuccess[
    dict[Station, dict[Direction, list[RealTimeArrival]]]
  ]
  | ApiError,
)
async def get_realtime_with_estimates():
  def f():
    return {
      station: {
        Direction.TO_NJ: get_sorted_routes(
          state.realtime_with_estimates_by_station_dir, station, Direction.TO_NJ
        ),
        Direction.TO_NY: get_sorted_routes(
          state.realtime_with_estimates_by_station_dir, station, Direction.TO_NY
        ),
      }
      for station in list(Station)
    }

  return await serve_api(f)


@app.get(
  "/realtime_with_estimates/{station}",
  response_model=ApiSuccess[dict[Direction, list[RealTimeArrival]]] | ApiError,
)
async def get_realtime_with_estimates_for_station(station: Station):
  def f():
    return {
      Direction.TO_NJ: get_sorted_routes(
        state.realtime_with_estimates_by_station_dir, station, Direction.TO_NJ
      ),
      Direction.TO_NY: get_sorted_routes(
        state.realtime_with_estimates_by_station_dir, station, Direction.TO_NY
      ),
    }

  return await serve_api(f)


@app.get(
  "/realtime_with_estimates/{station}/{direction}",
  response_model=ApiSuccess[list[RealTimeArrival]] | ApiError,
)
async def get_realtime_with_estimates_for_station_and_direction(
  station: Station, direction: Direction
):
  def f():
    return get_sorted_routes(
      state.realtime_with_estimates_by_station_dir, station, direction
    )

  return await serve_api(f)


@app.get("/stops")
async def stops():
  def f():
    return state.stop_info_by_id

  return await serve_api(f)


def date_within_some_service_id_range(date: date):
  for service_dates in state.calendar_service_ids.values():
    if (
      date >= service_dates["start_date"] and date <= service_dates["end_date"]
    ):
      return True
  return False


def service_ids_for_date(date: date):
  service_ids = set()

  for service_id, service_dates in state.calendar_service_ids.items():
    if (  # noqa: SIM102
      date >= service_dates["start_date"] and date <= service_dates["end_date"]
    ):
      if service_dates["valid_for"][DayOfWeek.of_int(date.weekday())]:
        service_ids.add(service_id)

  for exception in state.calendar_exceptions.get(date, []):
    if exception["type_"] == ServiceExceptionType.ADD:
      service_ids.add(exception["service_id"])
    elif exception["type_"] == ServiceExceptionType.REMOVE:
      service_ids.remove(exception["service_id"])
    else:
      raise Exception(f"Unknown exception_type: {exception['type_']}")  # noqa: TRY002

  return service_ids


def get_schedule_for_station_and_date(station: Station, date: date):
  def format_to_timestamp(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return time.fromisoformat(f"{hours:02}:{minutes:02}:{seconds:02}")

  def routes_to_timestamps(
    routes: list[RouteStopDetailsForStation],
  ) -> list[RouteStopDetailsForStationWithTimestamp]:
    sorted_routes = sorted(
      routes, key=lambda x: x["departure_seconds_after_midnight"]
    )

    return [
      {
        "trip_id": route["trip_id"],
        "trip_headsign": route["trip_headsign"],
        "arrival_time": format_to_timestamp(
          route["arrival_seconds_after_midnight"]
        ),
        "departure_time": format_to_timestamp(
          route["departure_seconds_after_midnight"]
        ),
      }
      for route in sorted_routes
    ]

  def routes_for_direction(direction: Direction):
    if not date_within_some_service_id_range(date):
      raise Exception(  # noqa: TRY002
        f"Currently there is no schedule provided for date: {date}"
      )

    DAY_SECONDS = 60 * 60 * 24

    service_ids = service_ids_for_date(date)

    prev_date = date + timedelta(days=-1)
    prev_service_ids = service_ids_for_date(prev_date)

    routes_from_prev_day_past_midnight = []
    for service_id in prev_service_ids:
      if (
        station,
        direction,
      ) in state.stop_times_for_service_id_and_stop_id.get(service_id, {}):
        routes_from_prev_day_past_midnight.extend(
          [
            route.copy()
            for route in state.stop_times_for_service_id_and_stop_id[
              service_id
            ][(station, direction)]
            if route["departure_seconds_after_midnight"] >= DAY_SECONDS
          ]
        )
    for route in routes_from_prev_day_past_midnight:
      route["arrival_seconds_after_midnight"] -= DAY_SECONDS
      route["departure_seconds_after_midnight"] -= DAY_SECONDS

    routes_from_today_before_midnight = []
    for service_id in service_ids:
      routes_from_today_before_midnight.extend(
        [
          route.copy()
          for route in state.stop_times_for_service_id_and_stop_id.get(
            service_id, {}
          ).get((station, direction), [])
          if route["departure_seconds_after_midnight"] < DAY_SECONDS
        ]
      )

    return (
      routes_from_prev_day_past_midnight + routes_from_today_before_midnight
    )

  schedule = {
    Direction.TO_NJ: routes_to_timestamps(
      routes_for_direction(Direction.TO_NJ)
    ),
    Direction.TO_NY: routes_to_timestamps(
      routes_for_direction(Direction.TO_NY)
    ),
  }
  return schedule


@app.get(
  "/schedule/{station}",
  response_model=ApiSuccess[
    dict[Direction, list[RouteStopDetailsForStationWithTimestamp]]
  ]
  | ApiError,
)
async def get_schedule_for_station(station: Station):
  def f():
    today = datetime.now(ZoneInfo("America/New_York")).date()
    return get_schedule_for_station_and_date(station, today)

  return await serve_api(f)


@app.get(
  "/schedule/{station}/direction/{direction}",
  response_model=ApiSuccess[list[RouteStopDetailsForStationWithTimestamp]]
  | ApiError,
)
async def get_schedule_for_station_and_direction(
  station: Station, direction: Direction
):
  def f():
    today = datetime.now(ZoneInfo("America/New_York")).date()

    schedule_for_station = get_schedule_for_station_and_date(station, today)
    return schedule_for_station.get(direction, [])

  return await serve_api(f)


@app.get(
  "/schedule/{station}/date/{date}",
  response_model=ApiSuccess[
    dict[Direction, list[RouteStopDetailsForStationWithTimestamp]]
  ]
  | ApiError,
)
async def get_schedule_for_station_and_date_endpoint(
  station: Station, date: date
):
  def f():
    return get_schedule_for_station_and_date(station, date)

  return await serve_api(f)


@app.get(
  "/schedule/{station}/date/{date}/direction/{direction}",
  response_model=ApiSuccess[list[RouteStopDetailsForStationWithTimestamp]]
  | ApiError,
)
async def get_schedule_for_station_and_date_and_direction_endpoint(
  station: Station, date: date, direction: Direction
):
  def f():
    schedule_for_station = get_schedule_for_station_and_date(station, date)
    return schedule_for_station.get(direction, [])

  return await serve_api(f)
