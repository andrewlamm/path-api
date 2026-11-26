from __future__ import annotations

from datetime import date, datetime, time
from enum import StrEnum
from typing import TypedDict, TypeVar

from pydantic import BaseModel


class Station(StrEnum):
  NEWARK = "newark"
  HARRISON = "harrison"
  JOURNAL_SQUARE = "journal_square"
  GROVE_STREET = "grove_street"
  EXCHANGE_PLACE = "exchange_place"
  WORLD_TRADE_CENTER = "world_trade_center"
  NEWPORT = "newport"
  HOBOKEN = "hoboken"
  CHRISTOPHER_STREET = "christopher_street"
  NINTH_STREET = "ninth_street"
  FOURTEENTH_STREET = "fourteenth_street"
  TWENTY_THIRD_STREET = "twenty_third_street"
  THIRTY_THIRD_STREET = "thirty_third_street"

  @classmethod
  def to_path_api_string(cls, station: Station) -> str:
    match station:
      case cls.NEWARK:
        return "Newark"
      case cls.HARRISON:
        return "Harrison"
      case cls.JOURNAL_SQUARE:
        return "Journal Square"
      case cls.GROVE_STREET:
        return "Grove Street"
      case cls.EXCHANGE_PLACE:
        return "Exchange Place"
      case cls.WORLD_TRADE_CENTER:
        return "World Trade Center"
      case cls.NEWPORT:
        return "Newport"
      case cls.HOBOKEN:
        return "Hoboken"
      case cls.CHRISTOPHER_STREET:
        return "Christopher Street"
      case cls.NINTH_STREET:
        return "9th Street"
      case cls.FOURTEENTH_STREET:
        return "14th Street"
      case cls.TWENTY_THIRD_STREET:
        return "23rd Street"
      case cls.THIRTY_THIRD_STREET:
        return "33rd Street"

  @classmethod
  def of_path_api_string(cls, s: str) -> Station:
    match s:
      case "Newark":
        return cls.NEWARK
      case "Harrison":
        return cls.HARRISON
      case "Journal Square":
        return cls.JOURNAL_SQUARE
      case "Grove Street":
        return cls.GROVE_STREET
      case "Exchange Place":
        return cls.EXCHANGE_PLACE
      case "World Trade Center":
        return cls.WORLD_TRADE_CENTER
      case "Newport":
        return cls.NEWPORT
      case "Hoboken":
        return cls.HOBOKEN
      case "Christopher Street":
        return cls.CHRISTOPHER_STREET
      case "9th Street":
        return cls.NINTH_STREET
      case "14th Street":
        return cls.FOURTEENTH_STREET
      case "23rd Street":
        return cls.TWENTY_THIRD_STREET
      case "33rd Street":
        return cls.THIRTY_THIRD_STREET
      case _:
        raise Exception(f"Invalid station string: {s}")  # noqa: TRY002


class Direction(StrEnum):
  TO_NY = "to_ny"
  TO_NJ = "to_nj"

  @classmethod
  def to_path_api_string(cls, direction: Direction) -> str:
    match direction:
      case cls.TO_NY:
        return "New York"
      case cls.TO_NJ:
        return "New Jersey"


class DefinedHeadsign(StrEnum):
  NEWARK = "Newark"
  JOURNAL_SQUARE = "Journal Square"
  WORLD_TRADE_CENTER = "World Trade Center"
  HOBOKEN = "Hoboken"
  THIRTY_THIRD_STREET = "33rd Street"
  JOURNAL_SQUARE_VIA_HOBOKEN = "Journal Square via Hoboken"
  THIRTY_THIRD_VIA_HOBOKEN = "33rd Street via Hoboken"

  @classmethod
  def of_str(cls, s: str) -> DefinedHeadsign | None:
    match s:
      case "Newark":
        return cls.NEWARK
      case "Journal Square":
        return cls.JOURNAL_SQUARE
      case "World Trade Center":
        return cls.WORLD_TRADE_CENTER
      case "Hoboken":
        return cls.HOBOKEN
      case "33rd Street":
        return cls.THIRTY_THIRD_STREET
      case "Journal Square via Hoboken":
        return cls.JOURNAL_SQUARE_VIA_HOBOKEN
      case "33rd Street via Hoboken":
        return cls.THIRTY_THIRD_VIA_HOBOKEN
      case _:
        return None

  @classmethod
  def to_final_station(cls, headsign: DefinedHeadsign) -> Station:
    match headsign:
      case cls.NEWARK:
        return Station.NEWARK
      case cls.JOURNAL_SQUARE | cls.JOURNAL_SQUARE_VIA_HOBOKEN:
        return Station.JOURNAL_SQUARE
      case cls.WORLD_TRADE_CENTER:
        return Station.WORLD_TRADE_CENTER
      case cls.HOBOKEN:
        return Station.HOBOKEN
      case cls.THIRTY_THIRD_STREET | cls.THIRTY_THIRD_VIA_HOBOKEN:
        return Station.THIRTY_THIRD_STREET


class RealTimeArrival(TypedDict):
  seconds_until_arrival: int
  arrival_time_message: str
  line_colors: list[str]
  headsign: str
  last_updated: datetime
  is_estimated: bool


class DayOfWeek(StrEnum):
  MONDAY = "monday"
  TUESDAY = "tuesday"
  WEDNESDAY = "wednesday"
  THURSDAY = "thursday"
  FRIDAY = "friday"
  SATURDAY = "saturday"
  SUNDAY = "sunday"

  @classmethod
  def of_int(cls, x: int) -> DayOfWeek:
    if x == 0:
      return cls.MONDAY
    elif x == 1:
      return cls.TUESDAY
    elif x == 2:
      return cls.WEDNESDAY
    elif x == 3:
      return cls.THURSDAY
    elif x == 4:
      return cls.FRIDAY
    elif x == 5:
      return cls.SATURDAY
    elif x == 6:
      return cls.SUNDAY
    else:
      raise Exception(f"Invalid day of week integer: {x}")  # noqa: TRY002


class ServiceIdDates(TypedDict):
  start_date: date
  end_date: date
  valid_for: dict[DayOfWeek, bool]


class StationInfo(TypedDict):
  station: Station
  stop_lat: float
  stop_lon: float


class ServiceExceptionType(StrEnum):
  ADD = "add"
  REMOVE = "remove"


class ServiceException(TypedDict):
  service_id: str
  type_: ServiceExceptionType


class RouteStopDetails(TypedDict):
  stop_id: str
  # We use seconds after midnight instead of time objects because the we can have times that are greater than 24 hours (e.g. 25:30:00)
  arrival_seconds_after_midnight: int
  departure_seconds_after_midnight: int


class RouteStopDetailsForStation(TypedDict):
  trip_id: str
  trip_headsign: str
  arrival_seconds_after_midnight: int
  departure_seconds_after_midnight: int


class RouteStopDetailsForStationWithTimestamp(TypedDict):
  trip_id: str
  trip_headsign: str
  arrival_time: time
  departure_time: time


class RouteDetails(TypedDict):
  trip_id: str
  route_long_name: str
  trip_headsign: str
  direction: Direction
  stops: list[RouteStopDetails]


T = TypeVar("T")


class ApiSuccess[T](BaseModel):
  success: bool = True
  message: T


class ApiError(BaseModel):
  success: bool = False
  error_message: str
