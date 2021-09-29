import time
from copy import deepcopy
import sys
import logging


from fun_scrape import scrape_time
from fun_scrape import scrape_Wien_all

from prometheus_client import start_http_server
from prometheus_client import Gauge


root = logging.getLogger()
root.setLevel(logging.INFO)

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
prom_Gauges = {
    n: {
        d: Gauge(f"ZamgFinal_{d}_{n}_{u}", f"Current {d} at {n} according to ZAMG")
        for d, u in zip(data, units)
    }
    for n in names
}


# first = True
try:
    while True:
        t = scrape_time()
        if t != t0:
            # temps = scrape_Wien_temps()
            data = scrape_Wien_all()
            for place in data:
                for m in data[place]:
                    prom_Gauges[place][m].set(data[place][m])
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
