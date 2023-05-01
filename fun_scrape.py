#!/usr/bin/python
#-*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import sys
import re
import time
import logging

from numpy import NaN

logger = logging.getLogger()


class recursionlimit:
    """context manager to set a specific recursion limit for a piece of code
    we are using this here, in order to additionally limit the recursions
    when reading a page which fails because of a network issue
    without this, we write a lot of logfiles as errors, especially if
    we are disconnected from the network for extended periods"""

    def __init__(self, newlimit):
        self.limit_inside = newlimit
        self.limit_outside = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit_inside)

    def __exit__(self, type_, value, tb):
        sys.setrecursionlimit(self.limit_outside)


def read_page(site, **kwargs):
    """read a page, in case of failure, repeat"""

    req = Request(site, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req) as conn:
            page = conn.read()
            return page
    except urllib.error.URLError as e:
        time.sleep(0.1)
        logger.exception(e)
        logging.error("ZamgScraping URLError: %s", e.reason)
        return read_page(site)


def extract_value(variable):
    try:
        var = float(variable)
    except ValueError:
        # if w.text == "n.v.":
        var = NaN 
    return var

def scr_Wien_all(page):
    """scrape relevant data"""
    data = {}
    soup = BeautifulSoup(page, features="html.parser")
    table = soup.find("table", attrs={"class": "dynPageTable"})

    rows = table.findAll("tr", {"class": "dynPageTableLine1"}) + table.findAll(
        "tr", {"class": "dynPageTableLine2"}
    )
    for x in rows:
        name = x.find("td", {"class": "wert"}).text
        name_corr = (
            name.replace(" ", "_", 5)
            .replace("ä", "ae", 3)
            .replace("ß", "ss", 3)
            .replace("-", "_", 5)
        )
        temperature = extract_value(
            x.find("td", {"class": "text_right wert selected"}).text[:-1]
        )
        humidity = extract_value(x.find("td", {"class": "text_center wert"}).text[:-2])

        w = x.findNext("td", {"class": "wert text_right"})
        wind = extract_value(w.text[:-4])

        p = w.findNext("td", {"class": "wert text_right"})
        precipitation = extract_value(p.text[:-3])

        sun = extract_value(x.find("td", {"class": "wert text_center"}).text[:-2])

        press = p.findNext("td", {"class": "wert text_right"})
        pressure = extract_value(press.text[:-4])

        data[name_corr] = dict(
            temperature=temperature,
            humidity=humidity,
            wind=wind,
            precipitation=precipitation,
            sun=sun,
            pressure=pressure,
        )
    return data


def scr_T(page):
    """scrape the time"""
    soup = BeautifulSoup(page, features="html.parser")
    string = soup.find("h2", {"class": "dynPageTextHead float_left no_margin_bottom"})
    date = re.findall(
        r"Aktuelle Messwerte der Wetterstationen von ([0-9]{2})", str(string)
    )
    try:
        d = float(date[0])
    except ValueError as e:
        logger.exception(e)
        d = scrape_time()
    return d


def apply_scraping(site, scrapefun):
    with recursionlimit(100):
        page = read_page(site)
        data = scrapefun(page)
        return data


def scrape_Wien_all():
    site = "https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien"
    return apply_scraping(site, scr_Wien_all)


def scrape_time():
    site = "https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/wien"
    return apply_scraping(site, scr_T)
