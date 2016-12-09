import requests
import re
import sys
from bs4 import BeautifulSoup
import time
from datetime import datetime
import urllib

# Finds instances of #24332
rank_regex = re.compile(r"#(\d+)")

# Finds instances of 342,543,212
number_regex = re.compile(r"[\d,]+")

# Finds instances of 4 hr.
hours_regex = re.compile(r"(\d+) hr\.")

# Finds instances of 34 min.
min_regex = re.compile(r"(\d+) min\.")

# Finds instances of 12 sec.
sec_regex = re.compile(r"(\d+) sec\.")

# Finds <h2>Information</h2> 
info_regex = re.compile(r"<h2>\s*Information\s*</h2>")

# Finds <h2>Statistics</h2>
stats_regex = re.compile(r"<h2>\s*Statistics\s*</h2>")

# Finds <h2>External Links</h2>
stats_end_regex = re.compile(r'<div class="clearfix mauto mt16"')

# Finds <h2>Related Anime</h2>
related_anime_regex = re.compile(r"<h2>\s*Related Anime\s*</h2>")

# Finds <h2>Summary Stats</h2>
stats_summary_regex = re.compile(r"<h2>\s*Summary Stats\s*</h2>")

# Finds <h2>Score Stats</h2>
stats_score_regex = re.compile(r"<h2>\s*Score Stats\s*</h2>")

favorites_regex = re.compile(r"""<div>\s*<span class="dark_text">\s*Favorites:\s*</span>\s*([\d,]+)\s*</div>""")


# Returns an int version of a comma seperated number in a string
# Assumes that the string has a number in it.
# e.g. extract_comma_number()"Members  \n      433,312") returns 433312 (int)
def extract_comma_number(str):
    return int(number_regex.search(str).group(0).replace(",", ""))

def get_safe_url(url):
    url = url.encode("utf8")
    slash_index = url.rfind("/")
    url_title = url[slash_index+1:]
    if "%" not in url_title:
        url = url[:slash_index+1] + urllib.quote(url_title)
    return url

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
def getGeneralInformation(html, aggregate_dict={}):
    soup = BeautifulSoup(html, 'html.parser')

    # Title
    title = soup.find("h1", class_="h1").get_text()
    aggregate_dict["title"] = title

    # Score
    score_tag = soup.find("div", class_="fl-l score")
    score_users = extract_comma_number(score_tag["data-user"])
    score_value = 0.0
    try:
        score_value = float(score_tag.get_text().strip())
    except:
        score_value = 0.0
    aggregate_dict["score_users"] = score_users
    aggregate_dict["score"] = score_value

    # Rank
    rank_text = soup.find("span", class_="numbers ranked").get_text()
    rank_match = rank_regex.search(rank_text)
    if rank_match is None:
        aggregate_dict["rank"] = None
    else:
        rank_value = int(rank_match.group(1))
        aggregate_dict["rank"] = rank_value

    # Popularity
    popularity_text = soup.find("span", class_="numbers popularity").get_text()
    popularity_value = int(rank_regex.search(popularity_text).group(1))
    aggregate_dict["popularity"] = popularity_value

    # Members
    members_text = soup.find("span", class_="numbers members").get_text().strip()
    members_value = int(extract_comma_number(members_text))
    aggregate_dict["members"] = members_value

    # Synoposis
    synopsis_soup = soup.find("span", itemprop="description")
    if synopsis_soup is None:
        aggregate_dict["synopsis"] = None
    else:
        synopsis_text = " ".join(synopsis_soup.strings)
        aggregate_dict["synopsis"] = synopsis_text

    #RelatedAnime
    related_table = soup.find_all("table", class_="anime_detail_related_anime")[0]
    related_entries = [t['href'].strip() for t in related_table.find_all("a")]
    related_entries = filter(lambda x: "/anime/" in x, related_entries)
    related_titles = map(lambda x: x.split("/")[3], related_entries)
    aggregate_dict["related_titles"] = related_titles

    # Statistics/Favorites (we have everything else)
    favorites_match = favorites_regex.search(html)
    favorites_text = favorites_match.group(1)
    aggregate_dict["favorites"] = int(favorites_text.replace(",", ""))

    # Information section
    info_dict = extract_info_section(html)

    # Info/Type
    aggregate_dict["type"] = info_dict.get("Type")

    # Info/Episodes
    if "Episodes" in info_dict:
        episodes_value = 0
        # Some anime pages have "Unknown" for number of episodes.
        # 0 represents unknown, because no anime can truly have 0 episodes.
        try:
            episodes_value = int(info_dict["Episodes"])
        except:
            episodes_value = 0
        aggregate_dict["episodes"] = episodes_value
    else:
        aggregate_dict["episodes"] = None

    # Info/Status
    aggregate_dict["status"] = info_dict.get("Status")

    # Info/Aired
    aired_start = None
    aired_end = None
    if "Aired" in info_dict:
        aired_text = info_dict["Aired"]
        # Some animes are aired on one date. Others run for some time period.
        # Those that run over a duration have "to" in the text.
        if "to" in aired_text:
            start_end_split = aired_text.split("to")
            aired_start = parse_date(start_end_split[0])
            # Some currently running animes have ? for their end date.
            if "?" in start_end_split[1]:
                aired_end = None
            else:
                aired_end = parse_date(start_end_split[1])
        else:
            aired_start = parse_date(aired_text)
            aired_end = aired_start
    aggregate_dict["aired_start"] = aired_start
    aggregate_dict["aired_end"] = aired_end

    # Info/Premiered
    aggregate_dict["premiered"] = info_dict.get("Premiered")

    # Info/Broadcast
    aggregate_dict["broadcast"] = info_dict.get("Broadcast")


    # Info/Producers
    if "Producers" in info_dict:
        aggregate_dict["producers"] = parse_info_list(info_dict["Producers"])
    else:
        aggregate_dict["producers"] = None

    # Info/Licensors
    if "Licensors" in info_dict:
        aggregate_dict["licensors"] = parse_info_list(info_dict["Licensors"]) 
    else:
        aggregate_dict["licensors"] = None

    # Info/Studios
    if "Studios" in info_dict:
        aggregate_dict["studios"] = parse_info_list(info_dict["Studios"]) 
    else:
        aggregate_dict["studios"] = studios_list

    # Info/Source
    aggregate_dict["source"] = info_dict.get("Source")

    # Info/Genres
    if "Genres" in info_dict:
        aggregate_dict["genres"] = parse_info_list(info_dict["Genres"]) 
    else:
        aggregate_dict["genres"] = None

    # Info/Duration
    if "Duration" in info_dict:
        duration_text = info_dict["Duration"]
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
    else:
        aggregate_dict["duration"] = None

    # Info/Rating
    if "Rating" in info_dict:
        rating_text = info_dict["Rating"]
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
    COOLDOWN_IN_SECONDS = 0.5
    time.sleep(COOLDOWN_IN_SECONDS)


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
    getGeneralInformation(html, aggregate_data)
    return aggregate_data

# Returns dictionary with data
def scrape_stats_page(html, aggregate_data={}):
    getStatSummary(html, aggregate_data)
    getStatDistribution(html, aggregate_data)
    return aggregate_data

def getStatSummary(html, aggregate_dict={}):
    #soup = BeautifulSoup(html, 'html.parser')
    start_index = stats_summary_regex.search(html).end()
    end_index = stats_score_regex.search(html).start()
    subs = html[start_index:end_index]
    stat_soup = BeautifulSoup(html[start_index:end_index], 'html.parser')
    field_list = [t.get_text().strip() for t in stat_soup.find_all("div")]
    for field in field_list[:6]:
        t = "Users " + str(field.split(':')[0])
        count = str(field.split(':')[1]).replace(',','')
        aggregate_dict[t] = int(count)
    return aggregate_dict

def getStatDistribution(html, aggregate_dict={}):
    #soup = BeautifulSoup(html, 'html.parser')

    start_index = stats_score_regex.search(html).end()
    stat_soup = BeautifulSoup(html[start_index:], 'html.parser')
    table = stat_soup.find("table")
    field_list = [t.get_text().strip() for t in table.find_all("div")]
    field_list.reverse()
    field_list = filter(lambda x: "votes" in x, field_list)
    voteSum = 0
    for i in xrange(len(field_list)):
        idx = i+1
        key = "Score " + str(idx) + " votes"
        start_idx = field_list[i].index("(")+1
        end_idx = field_list[i].index(" vote")
        count = field_list[i][start_idx:end_idx]
        aggregate_dict[key] = int(count)
        voteSum += int(count)
    
    aggregate_dict["Total Votes"] = voteSum
    #aggregate_dict["Watching"] = score_users
    #aggregate_dict[""] = score_value

    return aggregate_dict


# Returns pair (success, data)
# If success if False, then some error occurred and data may be None or corrupted.
def getAllDataFromUrl(url):
    success = True

    # Make URL
    url = get_safe_url(url)
    data = {}
    data["url"] = url
    # Get main page html
    try:
        html = get_html(url, True)
        retries = 0
        while html is None:
            print "Retrying after 5 seconds..."
            time.sleep(5)
            html = get_html(url, True)
            retries += 1
            if retries >= 3:
                return (False, data)
        html = bs_preprocess(html)
    except:
        return (False, data)

    # Page category and ID (i.e. ("anime", 345))
    # Used for primary keys
    page_category, page_id = getCategoryAndIDFromUrl(url)
    data["category"] = page_category
    data["id"] = page_id

    # Scrape data from the html of the main page
    try:
        scrape_main_page(html, data)
    except Exception as e:
        print "[ERROR] Fetching '", data.get("title", url), "' terminated early. Exception:", e.message
        success = False

   # Get stat html
    stat_url = url + "/stats"
    try:
        html = get_html(stat_url, True)
        retries = 0
        while html is None:
            print "Retrying fetching stats after 5 seconds..."
            time.sleep(5)
            html = get_html(url, True)
            retries += 1
            if retries >= 3:
                return (False, data)
        html = bs_preprocess(html)
    except:
        return (False, data)

   # Scrape data from the html of the stats page
    try:
        scrape_stats_page(html, data)
    except Exception as e:
        print "[ERROR] Fetching '", data.get("title", url), "' stats terminated early. Exception:", e.message
        success = False

    return (success, data)

# Returns the data in the Information section as a dict.
# The keys are the bolded text, and the values are everything that follows.
# e.g. if d is the return dictionary, and the page had
#           "Type:\n Music\n    Episodes:\n    1   \n Licensors: \n     None found, add some\n"
#      you would get:
#         d["Type"] = "Music"
#         d["Episodes"] = "1"
#         d["Licensors"] = "None found, add some"          
def extract_info_section(html):
    info_match = info_regex.search(html)
    stat_match = stats_regex.search(html)
    info_html = html[info_match.end():stat_match.start()]
    info_soup = BeautifulSoup(info_html, 'html.parser')
    info_list = [t.get_text().strip() for t in info_soup.find_all("div")]
    info_dict = {}
    for info in info_list:
        try:
            split_data = info.split(":", 1)
            key, value = split_data[0].strip(), split_data[1].strip()
            info_dict[key] = value
        except:
            print "[ERROR] Cannot split Information field. Got:", info
    return info_dict

def extract_stat_section(html):
    start_index = stats_regex.search(html).end()
    end_index = stats_end_regex.search(html).start()
    subs = html[start_index:end_index]
    stat_soup = BeautifulSoup(html[start_index:end_index], 'html.parser')
    field_list = [t.get_text().strip() for t in stat_soup.find_all("div")]
    field_dict = {}
    for field in field_list:
        try:
            split_data = field.split(":", 1)
            key, value = split_data[0].strip(), split_data[1].strip()
            field_dict[key] = value
        except:
            print "[ERROR] Cannot split Statistics field. Got:", field
    
    return field_dict

def parse_info_list(str):
    if "none found" in str.lower():
        return []
    else:
        return str.split(",")

def parse_date(s):
    try:
        return datetime.strptime(s.strip(), "%b %d, %Y").isoformat()
    except:
        print "[WARNING] Could not parse date normally. Got:", s
    try:
        d = datetime.strptime(s.strip(), "%b, %Y").isoformat()
        print "[WARNING] Using alternative:", d
        return d
    except:
        print "[WARNING] Could not get month, year format."
    try:
        d = datetime.strptime(s.strip(), "%Y").isoformat()
        print "[WARNING] Using alternative:", d
        return d
    except:
        print "[WARNING] Could not parse date at all. Returning None."
        return d

def example():
    print("Start")
    url = "https://myanimelist.net/anime/13391/Rakuen_Tsuihou__Expelled_from_Paradise"
    data = getAllDataFromUrl(url)
    print data[1]
    print("Done")

needed_keys = set([
    'rating',
    'studios',
    'members',
    'rank',
    'episodes',
    'duration',
    'id',
    'category',
    'genres',
    'title',
    'source',
    'score',
    'type',
    'status',
    'broadcast',
    'favorites',
    'producers',
    'licensors',
    'url',
    'popularity',
    'score_users',
    'premiered',
    'aired_end',
    'aired_start',
    'synopsis'
])

def validate(data):
    return needed_keys.issubset(set(data.keys()))