#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import json
from influxdb import InfluxDBClient
import bs4
from bs4 import BeautifulSoup
import requests
import pprint
from datetime import date, datetime

def pushToInflux(hostname, dbname, call, ccity, ccounty, ccured, cdead):
    client = InfluxDBClient(host=hostname, verify_ssl=False, database=dbname)
    client.create_database(dbname)
    influx_body = {}
    atime = datetime.now()
    influx_body["time"] =  atime.strftime('%Y-%m-%dT%H:%M:%SZ')
    fields = {"cases_all":call, "cases_city":ccity, "cases_county":ccounty, "cured":ccured, "dead": cdead}
    influx_body["fields"] = fields
    influx_body["measurement"] = "COVID19-KA"
    client.write_points([influx_body])


def crawlka(hostname, dbname, url):
    response = requests.get(url)
    html = response.content
    parsed = BeautifulSoup(html, "lxml")
    divelem = parsed.find_all('div', attrs={"class":"boxFact"})

    ccity = 0;
    ccounty = 0;
    ccured = 0;
    cdead = 0;

    for singlediv in divelem:
        pelem = singlediv.find_all('p')
        for item in pelem:
            text = item.get_text()
            case_field = text.split(':')
            if len(case_field) == 2:
                fid = case_field[0]
                if fid == "Stadt Karlsruhe":
                    ccity = int( case_field[1])
                if fid == "Landkreis Karlsruhe":
                    ccounty = int( case_field[1])
            else:
                cdratio = text.split(' ')
                fid = cdratio[1]
                if fid == "Genesen":
                    ccured = int(cdratio[0])
                if fid == "Todesfall":
                    cdead = int(cdratio[0])

    pushToInflux(hostname, dbname, ccity + ccounty, ccity, ccounty, ccured, cdead)
    
def copymap(img_out, url):
    response = requests.get(url)
    html = response.content
    elems = BeautifulSoup(html, "lxml").find_all('img')
    for item in elems:
        ctype = item.get('class')
        if ctype == None:
            url = item.get('src')
            imageres = requests.get(url)
            if imageres.status_code == 200:
                with open(img_out , "wb") as cimg:
                    for chunk in imageres :
                        cimg.write(chunk)

def app_main():
    """
    Main Entry Point - Argparsing und Anstoßen aller Tasks
    """
    PARSER = argparse.ArgumentParser(description='Collect Error-Messages from the ITS4 LogTable')
    PARSER.add_argument('--host', '-H', default="localhost", type=str, help="Hostname Influxdb")
    PARSER.add_argument('--db', '-n', default="covid19ka", type=str, help="Database Name Influxdb")
    PARSER.add_argument('--imgout', '-i', default="/var/www/html/covid/map.jpg", type=str, help="Database Name Influxdb")
    ARGS = PARSER.parse_args()
    crawlka(ARGS.host, ARGS.db, "https://corona.karlsruhe.de")
    copymap(ARGS.imgout, "https://corona.karlsruhe.de/aktuelle-fallzahlen")


if __name__ == "__main__":
    app_main()
