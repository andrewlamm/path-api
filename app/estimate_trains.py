import logging
from datetime import datetime
from typing import TypedDict

from app import state
from app.models import DefinedHeadsign, Direction, RealTimeArrival, Station
from app.station_deltas import STATION_DELTAS

logger = logging.getLogger(__name__)


# Temporary classes to represent estimated stations used
class RealTimeEstimate(TypedDict):
  estimated_stations_used: list[Station]
  estimated_delta_used: int


class RealTimeArrivalEstimate(TypedDict):
  seconds_until_arrival: int
  arrival_time_message: str
  line_colors: list[str]
  headsign: str
  last_updated: datetime
  estimated_from: None | RealTimeEstimate


def get_estimate_buffer(curr_arrival):
  if curr_arrival >= 1200:
    # If train is more than 20m away, buffer of 5m
    return 120
  # Otherwise if more than 15m away, buffer of 3m
  if curr_arrival >= 900:
    return 90
  # Otherwise buffer of 2m
  return 120


async def estimate_trains():
  realtime_with_estimates: dict[
    tuple[Station, Direction], list[RealTimeArrivalEstimate]
  ] = {}
  async with state.read_data_lock:
    for station in list(Station):
      for direction in list(Direction):
        realtime_with_estimates[(station, direction)] = []

        for train in state.realtime_by_station_dir.get(
          (station, direction), []
        ):
          train_copy: RealTimeArrivalEstimate = {
            "seconds_until_arrival": train["seconds_until_arrival"],
            "arrival_time_message": train["arrival_time_message"],
            "line_colors": train["line_colors"],
            "headsign": train["headsign"],
            "last_updated": train["last_updated"],
            "estimated_from": None,
          }
          realtime_with_estimates[(station, direction)].append(train_copy)

    for (station, direction), trains in realtime_with_estimates.items():
      for train in trains:
        headsign = DefinedHeadsign.of_str(train["headsign"])

        if headsign is None:
          logger.error(f"Unknown headsign: {train['headsign']}")
          continue

        next_stations = STATION_DELTAS[station].get(headsign)
        if next_stations is None:
          logger.error(f"No next stations for {station} to {headsign}")
          continue

        for next_station, delta in next_stations.items():
          if next_station == DefinedHeadsign.to_final_station(headsign):
            continue

          estimated_arrival = (
            train["last_updated"].timestamp()
            + train["seconds_until_arrival"]
            + delta
          )

          found = False

          for target_direction in list(Direction):
            for target_train in realtime_with_estimates[
              (next_station, target_direction)
            ]:
              target_headsign = target_train["headsign"]

              if target_headsign != headsign:
                continue

              target_arrival = (
                target_train["last_updated"].timestamp()
                + target_train["seconds_until_arrival"]
              )

              estimate_buffer = get_estimate_buffer(
                target_train["seconds_until_arrival"]
              )

              if abs(
                target_arrival - estimated_arrival
              ) <= estimate_buffer and (
                target_train["estimated_from"] is None
                or station
                not in target_train["estimated_from"]["estimated_stations_used"]
              ):
                if target_train["estimated_from"] is None:
                  target_train["estimated_from"] = {
                    "estimated_stations_used": [station],
                    "estimated_delta_used": delta,
                  }
                else:
                  target_train["estimated_from"][
                    "estimated_stations_used"
                  ].append(station)
                  target_train["estimated_from"]["estimated_delta_used"] = min(
                    delta,
                    target_train["estimated_from"]["estimated_delta_used"],
                  )

                found = True
                break

            if found:
              break

          # If no match found, add an estimated train message
          if not found:
            new_train: RealTimeArrivalEstimate = {
              "seconds_until_arrival": train["seconds_until_arrival"] + delta,
              "last_updated": train["last_updated"],
              "arrival_time_message": f"{(train['seconds_until_arrival'] + delta) // 60} min (Est from {station})",
              "headsign": train["headsign"],
              "line_colors": train["line_colors"],
              "estimated_from": {
                "estimated_stations_used": [station],
                "estimated_delta_used": delta,
              },
            }
            realtime_with_estimates[(next_station, direction)].append(new_train)

    output: dict[tuple[Station, Direction], list[RealTimeArrival]] = {}
    for (station, direction), trains in realtime_with_estimates.items():
      output[(station, direction)] = []

      for train in trains:
        cleaned_train: RealTimeArrival = {
          "seconds_until_arrival": train["seconds_until_arrival"],
          "arrival_time_message": train["arrival_time_message"],
          "line_colors": train["line_colors"],
          "headsign": train["headsign"],
          "last_updated": train["last_updated"],
          "is_estimated": train["estimated_from"] is not None,
        }
        output[(station, direction)].append(cleaned_train)

    state.realtime_with_estimates_by_station_dir = output
