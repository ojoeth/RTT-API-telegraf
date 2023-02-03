# RTT-API-telegraf
This program is a script meant to be called from Telegraf which queries RealTimeTrains' API, and counts cancelled, late and on-time trains per-day in an sqlite database.
It outputs the data in a format readable from Telegraf and I intend to use it to feed in to Influx, and draw pretty graphs of cancelled trains in Grafana.
