import urllib
import requests
import re
import sys
from bs4 import BeautifulSoup

def get_html(url, verbose=False):
    if verbose: print "Making get request to", url
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        if verbose: print "request.get returned non-OK status"
        return None
    else:
        if verbose: print "OK"
        return r.text.encode('utf8')


def get_season_anime(year, season, out_file=""):
    base_url = "https://myanimelist.net/anime/season/"
    html = get_html(base_url + str(year) + "/" + season.lower())
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