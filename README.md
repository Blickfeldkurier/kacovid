# KaCovid

Python-Script to get the Case Numbers from https://corona.karlsruhe.de 
an push them into a Influx-DB

## Depenencies
* bs4
* influxdb InfluxDBClient

## Instalation

Add Cron-Job
```
42 23 * * * /opt/kacovid/KaCovid.py -i /var/www/covid/19 -H localhost
```
