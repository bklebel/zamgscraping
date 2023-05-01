#!/usr/bin/python
#-*- coding:utf-8 -*-
import time
from copy import deepcopy
import sys
import logging


from fun_scrape import scrape_time
from fun_scrape import scrape_Wien_all

from fun_calculations import humidity_absolute

from prometheus_client import start_http_server
from prometheus_client import Gauge


root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


t0 = 0
names = [
    "Wien_Hohe_Warte",
    "Wien_Innere_Stadt",
    "Wien_Stammersdorf",
    "Wien_Donaufeld",
    "Wien_Unterlaa",
    "Wien_Mariabrunn",
    "Wien_Jubilaeumswarte",
    "Gross_Enzersdorf",
    "Schwechat_Flughafen",
    "Brunn_am_Gebirge",
]

# changed ' '  to '_', 'ä' to 'ae', 'ß' to 'ss', '-' to -_-
data = ["temperature", "humidity", "pressure", "wind", "sun", "precipitation"]
units = ["celsius", "percent", "hPa", "kmh", "percent", "percent"]

root.info("setting up Gauges")

prom_Gauges = {
    n: {
        d: Gauge(f"ZamgFinal_{d}_{n}_{u}", f"Current {d} at {n} according to ZAMG")
        for d, u in zip(data, units)
    }
    for n in names
}


for n in names:
    prom_Gauges[n]["humidity_absolute"] = Gauge(f"ZamgFinal_humidity_absolute_{n}_g_m3", f"Current absolute humidity at {n} according to ZAMG")

root.info("Gauges set") #" %s", prom_Gauges)

# first = True
try:
    while True:
        t = scrape_time()
        if t != t0:
            data = scrape_Wien_all()
            for place in data:
                for m in data[place]:
                    prom_Gauges[place][m].set(data[place][m])
                    root.debug("recorded: %s", (place, m, data[place][m])    )
                abs_hum = humidity_absolute(data[place]["humidity"], data[place]["temperature"])
                prom_Gauges[place]["humidity_absolute"].set(abs_hum)
                root.debug("recorded: %s", (place, "humidity absolute", abs_hum)    )
            t0 = deepcopy(t)
            try:
                first
            except NameError as e:
                first = False
                root.info("starting http server")
                start_http_server(8001)
        time.sleep(120)
except KeyboardInterrupt:
    pass
