import asyncio
from datetime import date

from app.models import (
  Direction,
  RealTimeArrival,
  RouteDetails,
  RouteStopDetailsForStation,
  ServiceException,
  ServiceIdDates,
  Station,
  StationInfo,
)

realtime_by_station_dir: dict[
  tuple[Station, Direction], list[RealTimeArrival]
] = {}

read_data_lock = asyncio.Lock()
realtime_with_estimates_by_station_dir: dict[
  tuple[Station, Direction], list[RealTimeArrival]
] = {}

database_checksum = None

stop_info_by_id: dict[str, StationInfo] = {}

calendar_service_ids: dict[str, ServiceIdDates] = {}
calendar_exceptions: dict[date, list[ServiceException]] = {}

schedules_by_service_id: dict[str, list[RouteDetails]] = {}
stop_times_for_service_id_and_stop_id: dict[
  str, dict[tuple[Station, Direction], list[RouteStopDetailsForStation]]
] = {}
