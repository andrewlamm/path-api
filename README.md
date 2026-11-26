# Path API

API for retrieving train data for the PATH (Port Authority Trans-Hudson) transit system.

More details about the app coming soonTM

## API Endpoints

Stations can be one of the following:
```
newark
harrison
journal_square
grove_street
exchange_place
world_trade_center
newport
hoboken
christopher_street
ninth_street
fourteenth_street
twenty_third_street
thirty_third_street
```
Directions can be either `to_ny` or `to_nj`

### Real-time Data
`/realtime`: Real-time data for all stations and direcitons, straight from the same RidePATH API
`/realtime/{station}`: Real-time data for a specific station
`/realtime/{station}/{direction}`: Real-time data for a specific station and direction
`/realtime_with_estimates{/station/{direction}}`: Real-time data for all stations and directions but include estimated trains (using ETAs of previous stations). Optional station and direction parameters to filter the results like above.

### Schedules
`/schedule/{station}`: Train schedule for a specific station. 
  - Add `/direction/{direction}` to filter by direction and/or
  - Add `/date/{date}` to filter by date (in YYYY-MM-DD format)

### Misc
`/stops`: List of all stations with some metadata
