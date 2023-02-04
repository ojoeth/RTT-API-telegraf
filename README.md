# RTT-API-telegraf
This program is a script meant to be called from Telegraf which queries RealTimeTrains' UK train API, and counts cancelled, late and on-time trains per-day in an sqlite database.
It outputs the data in a format readable from Telegraf and I intend to use it to feed in to Influx, and draw pretty graphs of cancelled trains in Grafana.

## Requirements
- telegraf
- python 3
- python module "requests"
- API account with realtimetrains

## Usage
- Clone this repository somewhere sensible (/opt/RTT_API will work)
- Install Telegraf (https://www.influxdata.com/time-series-platform/telegraf/)
- Set up Telegraf to report in to InfluxDB
- Put the following in your /etc/telegraf/telegraf.conf:

```toml
[[inputs.exec]]
commands = [ "/bin/bash /opt/RTT_API/run.sh rttapi_username rttapi_password stationcode"]
  timeout = "60s"
  name_suffix = "traindata"
  data_format = "logfmt"

```

- replace /opt/RTT_API/run.sh with the location of this repository
- replace rttapi_username and rttapi_password with your credentials from https://api.rtt.io
- replace stationcode with the station code of the station you wish to monitor (eg: bex for Bexhill). Find a list here: https://www.nationalrail.co.uk/stations_destinations/48541.aspx