import time
from copy import deepcopy
import sys

from fun_scrape import scrape_time
from fun_scrape import scrape_innerestadt


from fun_scrape import read_page
from bs4 import BeautifulSoup
import re
# from prometheus_client import start_http_server
from prometheus_client import Gauge

names = ['Wien_Hohe_Warte', 'Wien_Innere_Stadt', 'Wien_Stammersdorf', 'Wien_Donaufeld', 'Wien_Unterlaa', 'Wien_Mariabrunn', 'Wien_Jubilaeumswarte', 'Gross_Enzersdorf', 'Schwechat_Flughafen', 'Brunn_am_Gebirge', ]
# ' '  to '_', 'ä' to 'ae', 'ß' to 'ss', '-' to -_-
data = ['temperature', 'humidity', 'pressure', 'wind', 'sun', 'precipitation']
units = ['celsius', 'percent', 'hPa', 'kmh', 'percent', 'percent']
prom_Gauges = {n: {Gauge(f'ZamgFinal_{d}_{n}_{u}', f'Current {d} at {n} according to ZAMG') for d, u in zip(data, units)}for n in names}


print(prom_Gauges)


def scr_Wien_all(page):
    data = {}
    soup = BeautifulSoup(page, features="html.parser")
    # print(soup.findAll('class="text_right wert selected"'))
    # print(soup)
    table = soup.find('table', attrs={'class': 'dynPageTable'})
    # print(table)

    rows = table.findAll('tr', {'class': 'dynPageTableLine1'}) + table.findAll('tr', {'class': 'dynPageTableLine2'})
    # print('')
    for x in rows:
        # print(x)
        name = x.find('td', {'class': 'wert'}).text 
        name_corr = name.replace(' ', '_', 5).replace('ä', 'ae', 3).replace('ß', 'ss', 3).replace('-', '_', 5)
        # print(x.find('td', {'class': 'wert'}).text)
        temperature = float(x.find('td', {'class': 'text_right wert selected'}).text[:-1]) 
        humidity = float(x.find('td', {'class': 'text_center wert'}).text[:-2]) 
        
        w = x.findNext('td', {'class': 'wert text_right'})
        wind = float(w.text[:-4])
        p = w.findNext('td', {'class': 'wert text_right'})
        precipitation = float(p.text[:-3])
        sun = float(x.find('td', {'class': 'wert text_center'}).text[:-2]) 
        press = p.findNext('td', {'class': 'wert text_right'})
        pressure = float(press.text[:-4]) 
        data[name_corr] = dict(
            temperature=temperature,
            humidity=humidity,
            wind=wind,
            precipitation=precipitation,
            sun=sun,
            pressure=pressure,
            )
        # print(float(x.find('td', {'class': 'text_right wert selected'}).text[:-1]))
    # print(data)
    return data

def scrape_Wien_temps():
    site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'
    page = read_page(site, scrape_Wien_temps)
    temps = scr_Wien(page)
    return temps

# prom_temp = Gauge('ZAMGscraping_temp_innereStadt_celsius', 'current temperature at Wien Innere Stadt according to ZAMG')

# start_http_server(8001)
# first = True
# try:
    # while True:
        # t = scrape_time()
        # if t != t0:
temp = scrape_Wien_temps()
# prom_temp.set(temp)
# t0 = deepcopy(t)
for key in temp:
    print(temp[key])
# print(temp)
# print(temp)
# try:
#     first
# except NameError as e:
#     first = False
#     sys.stderr.write('starting http server')
#     start_http_server(8001)            
#         time.sleep(120)
# except KeyboardInterrupt:
#     pass
