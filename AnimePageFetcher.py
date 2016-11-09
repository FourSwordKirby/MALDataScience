import urllib
import requests
import re
import sys
from bs4 import BeautifulSoup


def prog(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    sys.stdout.write("%2d%%, " % percent)
    sys.stdout.flush()

def dl(html):
    soup = BeautifulSoup(html, 'html.parser')
    file_name = soup.find("div", class_="fileName").get_text().strip()
    js_script = soup.find("div", class_="download_link").text
    match = re.search(r"http://.+?.mp3", js_script)
    dl_link = match.group(0)
    print("Downloading from", dl_link)
    print("Saving as", file_name)
    urllib.request.urlretrieve(dl_link, file_name, reporthook=prog)
    print("\nDone download.")

#these are the stats found on the stat page of an anime
#Example: https://myanimelist.net/anime/30/Neon_Genesis_Evangelion/stats
def getGeneralStatistics(html):
    return

#these are generic info like the producers and the source found in the
#sidebar of an anime page
#Example https://myanimelist.net/anime/30/Neon_Genesis_Evangelion
def getGeneralInformation(html):
    return

#Fetches the production staff associated with a show
#Example: https://myanimelist.net/anime/30/Neon_Genesis_Evangelion/characters#staff
def getStaff(html):
    return

#Fetches the characters and voice actors associted with a show
#Example: https://myanimelist.net/anime/30/Neon_Genesis_Evangelion/characters
def getCharactersAndJapaneseCast(html):
    return

#Fetches the list of other related anime, same series etc.
def getRelatedTitles(html):
    return

def get_html(url, out_file, render_first=False):
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

def save_html(url, out_file, render_first=False):
    html = ""
    print "Making get request to", url
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        print "OK"
        html = r.text.encode('utf8')
    else:
        print "request.get returned non-OK status"
        return None
    print "Writing html to", out_file
    print "Type is", type(html)
    with open(out_file, 'w') as f:
        soup = BeautifulSoup(html, 'html.parser')
        html = soup.prettify()
        f.write(html.encode("utf8"))
        return html

def do():
    with open("output.txt", 'r') as f:
        html = f.read()
        dl(html)
        print("Completed")


print("Start")
url = "https://myanimelist.net/anime/30/Neon_Genesis_Evangelion"
out = "html_output.txt"
result = save_html(url, out, True)
print("Done")
