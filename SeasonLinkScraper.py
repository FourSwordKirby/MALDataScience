import urllib
import requests
import re
import sys
import time
from bs4 import BeautifulSoup

def get_html(url, verbose=False):
    if verbose: sys.stdout.write("Making get request to " + url + " ... ")
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        if verbose:
            print "[ERROR] request.get returned non-OK status. Got:", r.status_code
        return None
    else:
        if verbose:
            sys.stdout.write("OK.\n")
            sys.stdout.flush()
        return r.text.encode('utf8')

def get_season_anime(year, season, out_file=""):
    base_url = "https://myanimelist.net/anime/season/"
    url = base_url + str(year) + "/" + season.lower()
    html = get_html(url)
    retries = 0
    while html is None:
        print "Retrying after", (retries+1) * 5, "seconds..."
        time.sleep((retries+1) * 5)
        html = get_html(url, True)
        retries += 1
        if retries >= 10:
            print "Cannot get seasonal data for", season, year
            return []
    soup = BeautifulSoup(html, 'html.parser')
    anime_titles = soup.findAll("a", class_="link-title")

    urls = []
    if(out_file != ""):
        f = open(out_file, 'w')

    for title in anime_titles:
        urls.append(title['href'])
        if(out_file != ""):
            f.write(title['href'].encode("utf8")+ "\n")

    return urls