from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
# from urllib.error import URLError
import urllib
import re
import time
import sys
import logging
logger = logging.getLogger()


def read_page(site, scrapefun, **kwargs):

    req = Request(site,  headers={
                  'User-Agent': 'Mozilla/5.0'})
    try:
        with urlopen(req) as conn:
            page = conn.read()
            return page
    except urllib.error.URLError as e:
        time.sleep(0.1)
        logger.exception(e)
        logging.error('ZamgScraping URLError: {}'.format(e.reason))
        return scrapefun()


# def scr_Wien(page):
#     temps = dict()
#     soup = BeautifulSoup(page, features="html.parser")
#     # print(soup.findAll('class="text_right wert selected"'))
#     # print(soup)
#     table = soup.find('table', attrs={'class': 'dynPageTable'})
#     # print(table)

#     rows = table.findAll('tr', {'class': 'dynPageTableLine1'}) + \
#         table.findAll('tr', {'class': 'dynPageTableLine2'})
#     # print('')
#     for x in rows:
#         # print(x)
#         name = x.find('td', {'class': 'wert'}).text
#         name_corr = name.replace(' ', '_', 5).replace(
#             'ä', 'ae', 3).replace('ß', 'ss', 3).replace('-', '_', 5)
#         # print(x.find('td', {'class': 'wert'}).text)
#         value = float(
#             x.find('td', {'class': 'text_right wert selected'}).text[:-1])
#         temps[name_corr] = value
#         # print(float(x.find('td', {'class': 'text_right wert selected'}).text[:-1]))

#     return temps


# def scrape_Wien_temps():
#     site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'
#     page = read_page(site, scrape_Wien_temps)
#     temps = scr_Wien(page)
#     return temps


def scr_Wien_all(page):
    data = {}
    soup = BeautifulSoup(page, features="html.parser")
    # print(soup.findAll('class="text_right wert selected"'))
    # print(soup)
    table = soup.find('table', attrs={'class': 'dynPageTable'})
    # print(table)

    rows = table.findAll('tr', {'class': 'dynPageTableLine1'}) + \
        table.findAll('tr', {'class': 'dynPageTableLine2'})
    # print('')
    for x in rows:
        # print(x)
        name = x.find('td', {'class': 'wert'}).text
        name_corr = name.replace(' ', '_', 5).replace(
            'ä', 'ae', 3).replace('ß', 'ss', 3).replace('-', '_', 5)
        # print(x.find('td', {'class': 'wert'}).text)
        temperature = float(
            x.find('td', {'class': 'text_right wert selected'}).text[:-1])
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


def scrape_Wien_all():
    site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'
    page = read_page(site, scrape_Wien_all)
    data = scr_Wien_all(page)
    return data


def scr_T(page):
    soup = BeautifulSoup(page, features="html.parser")
    string = soup.find(
        'h2', {'class': 'dynPageTextHead float_left no_margin_bottom'})
    date = re.findall(
        r'Aktuelle Messwerte der Wetterstationen von ([0-9]{2})', str(string))
    # print(date[0])
    try:
        d = float(date[0])
    except ValueError as e:
        logger.exception(e)
        d = scrape_time()
    return d


def scrape_time():
    site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'
    page = read_page(site, scrape_time)
    d = scr_T(page)
    return d


# def scrape_innerestadt_():

#     site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'

#     req = Request(site,  headers={
#                   'User-Agent': 'Mozilla/5.0'})
#     try:
#         with urlopen(req) as conn:
#             page = conn.read()
#             soup = BeautifulSoup(page, features="html.parser")
#             # print(soup.findAll('class="text_right wert selected"'))
#             # print(soup)
#             table = soup.find('table', attrs={'class': 'dynPageTable'})
#             # print(table)
#             rows = table.find('tr', {'class': 'dynPageTableLine1'})
#             values = rows.find('td', {'class': 'text_right wert selected'})
#             temp = re.search(r'([0-9]+.[0-9])', str(values))
#             # print(float(temp.group()))
#         try:
#             temperature = float(temp.group())
#         except ValueError as e:
#             logger.exception(e)
#             temperature = scrape_innerestadt()
#         return temperature
#     except URLError:
#         return scrape_innerestadt()


# def scrape_time():

#     site = 'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien'

#     req = Request(site,  headers={
#                   'User-Agent': 'Mozilla/5.0'})

#     with urlopen(req) as conn:
#         page = conn.read()
#         soup = BeautifulSoup(page, features="html.parser")
#         string = soup.find(
#             'h2', {'class': 'dynPageTextHead float_left no_margin_bottom'})
#         date = re.findall(
#             r'Aktuelle Messwerte der Wetterstationen von ([0-9]{2})', str(string))
#         # print(date[0])
#         d = float(date[0])
#         return d
