import urllib
import requests
import re
import sys
from bs4 import BeautifulSoup

def get_html(url, render_first=False):
    html = ""
    if render_first:
        print "Rendering", url
        r = Render(url)
        print "Successfully rendered."
        html = r.frame.toHtml()
        html = unicode(html.toUtf8(), encoding="UTF-8").encode('utf8')
    else:
        print "Making get request to", url
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            print "OK"
            html = r.text.encode('utf8')
        else:
            print "request.get returned non-OK status"
            return None
    return html

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

years = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
seasons = ["winter", "fall", "summer", "spring"]

for year in years:
    for season in seasons:
        print str(year)+"_"+season+".txt"
        get_season_anime(year, season, str(year)+"_"+season+".txt")