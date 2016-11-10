import requests
import re
import sys
from bs4 import BeautifulSoup
import time
from datetime import datetime

rank_regex = re.compile(r"#(\d+)")
number_regex = re.compile(r"[\d,]+")
hours_regex = re.compile(r"(\d+) hr\.")
min_regex = re.compile(r"(\d+) min\.")
sec_regex = re.compile(r"(\d+) sec\.")

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

# Returns an int version of a comma seperated number in a string
# Assumes that the string has a number in it.
# e.g. "Members  \n      433,312"
def extract_comma_number(str):
    return int(number_regex.search(str).group(0).replace(",", ""))

#these are the stats found on the stat page of an anime
#Example: https://myanimelist.net/anime/30/Neon_Genesis_Evangelion/stats
def getGeneralStatistics(soup, aggregate_dict={}):
    return aggregate_dict

# Returns (type, id) where type is str in ["anime", "manga"], and id an int
def getCategoryAndIDFromUrl(url):
    url = str(url)
    result = url.split("myanimelist.net/")
    if(len(result) > 1):
        result = result[1].split("/")
        content_category = result[0]
        content_id = int(result[1])
        return (content_category, content_id)

#these are generic info like the producers and the source found in the
#sidebar of an anime page
#Example https://myanimelist.net/anime/30/Neon_Genesis_Evangelion
def getGeneralInformation(soup, aggregate_dict={}):
    # Title
    title = soup.find("h1", class_="h1").get_text()
    aggregate_dict["title"] = title

    # Score
    score_tag = soup.find("div", class_="fl-l score")
    score_users = extract_comma_number(score_tag["data-user"])
    score_value = float(score_tag.get_text().strip())
    aggregate_dict["score_users"] = score_users
    aggregate_dict["score"] = score_value

    # Rank
    rank_text = soup.find("span", class_="numbers ranked").get_text()
    rank_value = int(rank_regex.search(rank_text).group(1))
    aggregate_dict["rank"] = rank_value

    # Popularity
    popularity_text = soup.find("span", class_="numbers popularity").get_text()
    popularity_value = int(rank_regex.search(popularity_text).group(1))
    aggregate_dict["popularity"] = popularity_value

    # Members
    members_text = soup.find("span", class_="numbers members").get_text().strip()
    members_value = int(extract_comma_number(members_text))
    aggregate_dict["members"] = members_value

    # Information section
    info_soup = soup.find("h2", string=lambda s: s.strip() == "Information")
    info_soup = info_soup.find_next_sibling("div")
    text = info_soup.get_text()

    # Info/Type
    if "Type" in text:
        type_text = text.split("Type:")[1].strip()
        aggregate_dict["type"] = type_text
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["type"] = None


    # Info/Episodes
    if "Episodes" in text:
        episodes_value = int(text.split("Episodes:")[1].strip())
        aggregate_dict["episodes"] = episodes_value
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["episodes"] = None


    # Info/Status
    if "Status" in text:
        status_text = text.split("Status:")[1].strip()
        aggregate_dict["status"] = status_text
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["status"] = None

    # Info/Aired
    aired_start = None
    aired_end = None
    if "Aired" in text:
        aired_text = info_soup.get_text().split("Aired:")[1].strip()
        if "to" in aired_text:
            start_end_split = aired_text.split(" to ")
            aired_start = datetime.strptime(start_end_split[0], "%b %d, %Y")
            aired_end = datetime.strptime(start_end_split[1], "%b %d, %Y")
        else:
            aired_start = datetime.strptime(aired_text, "%b %d, %Y")
            aired_end = aired_start
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    aggregate_dict["aired_start"] = aired_start
    aggregate_dict["aired_end"] = aired_end

    # Info/Premiered
    if "Premiered" in text: 
        premiered_text = text.split("Premiered:")[1].strip()
        aggregate_dict["premiered"] = premiered_text
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["premiered"] = None

    # Info/Broadcast
    if "Broadcast" in text:
        broadcast_text = text.split("Broadcast:")[1].strip()
        aggregate_dict["broadcast"] = broadcast_text
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["broadcast"] = None


    # Info/Producers
    if "Producers" in text:
        producers_text = text.split("Producers:")[1].strip()
        producers_list = producers_text.split(", ")
        aggregate_dict["producers"] = producers_list
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["producers"] = None

    # Info/Licensors
    if "Licensors" in text:
        licensors_text = text.split("Licensors:")[1].strip()
        licensors_list = licensors_text.split(", ")
        aggregate_dict["licensors"] = licensors_list
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["licensors"] = None

    # Info/Studios
    if "Studios" in text:
        studios_text = text.split("Studios:")[1].strip()
        studios_list = studios_text.split(", ")
        aggregate_dict["studios"] = studios_list
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["studios"] = studios_list

    # Info/Source
    if "Source" in text:
        source_text = text.split("Source:")[1].strip()
        aggregate_dict["source"] = source_text
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["source"] = None

    # Info/Genres
    if "Genres" in text:
        genres_text = text.split("Genres:")[1].strip()
        genres_list = genres_text.split(", ")
        aggregate_dict["genres"] = genres_list
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["genres"] = None

    # Info/Duration
    if "Duration" in text:
        duration_text = text.split("Duration:")[1].strip()
        mins = 0.0
        # Hours
        match = hours_regex.search(duration_text)
        if match is not None:
            mins += float(match.group(1)) * 60.0
        # Minutes
        match = min_regex.search(duration_text)
        if match is not None:
            mins += float(match.group(1))
        # Seconds
        match = sec_regex.search(duration_text)
        if match is not None:
            mins += float(match.group(1)) / 60.0
        aggregate_dict["duration"] = mins
        info_soup = info_soup.find_next_sibling("div")
        text = info_soup.get_text()
    else:
        aggregate_dict["duration"] = None

    # Info/Rating
    if "Rating" in text:
        rating_text = text.split("Rating:")[1].strip()
        rating_shorthand = rating_text.split(" - ")[0].strip()
        aggregate_dict["rating"] = rating_shorthand
    else:
        aggregate_dict["rating"] = None

    return aggregate_dict

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

def cooldown():
    COOLDOWN_IN_SECONDS = 0.25
    time.sleep(COOLDOWN_IN_SECONDS)

def get_html(url, verbose=False):
    if verbose: print "Making get request to", url
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        if verbose: print "request.get returned non-OK status"
        return None
    else:
        if verbose: print "OK"
        return r.text.encode('utf8')

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

def load_html_from_file(file):
    with open(file, 'r') as f:
        html = f.read()
        return html

def do():
    with open("output.txt", 'r') as f:
        html = f.read()
        dl(html)
        print("Completed")

def bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)       # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)     # convert newlines to spaces
                                    # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html) # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html) # remove whitespaces after closing tags
    return html 

# Returns dictionary with data
def scrape_main_page(html, aggregate_data={}):
    soup = BeautifulSoup(html, 'html.parser')
    getGeneralInformation(soup, aggregate_data)
    return aggregate_data

def getAllDataFromUrl(url):
    html = get_html(url, True)
    html = bs_preprocess(html)
    # html = load_html_from_file("html_output.txt")
    data = {}

    # Page category and ID (i.e. ("anime", 345))
    # Used for primary keys
    page_category, page_id = getCategoryAndIDFromUrl(url)
    data["category"] = page_category
    data["id"] = page_id

    # Scrape data from the html of the main page
    try:
        scrape_main_page(html, data)
    except:
        print "[ERROR] Fetching data for '", data.get("title", url), "' ran into an issue."
    return data

print("Start")
url = "https://myanimelist.net/anime/34240/Shelter"
data = getAllDataFromUrl(url)
print data
print("Done")
