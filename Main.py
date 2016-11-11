import os
import json
import AnimePageFetcher
import SeasonLinkScraper
import sys

data_directory = "data/"
fail_filename_format = "failures_%s.txt"

def grab_data(years, seasons=["winter", "fall", "summer", "spring"]):
    print "Starting MAL scrap session."
    for year in years:
        print "Starting on Year", year
        group = str(year)
        directory = os.path.join(data_directory, group)
        if not os.path.exists(directory):
            os.makedirs(directory)

        error_file_name = fail_filename_format % group
        error_path = os.path.join(directory, error_file_name)
        fail_file = open(error_path, 'a')     # 'a' for append. Capture all failures until fix
        for season in seasons:
            print "Starting", str(group)+"_"+season 
            animeURLS = SeasonLinkScraper.get_season_anime(year, season)
            AnimePageFetcher.cooldown()
            print "Got all urls."
            for url in animeURLS:
                success, dataset = AnimePageFetcher.getAllDataFromUrl(url)

                if not success:
                    safe_url = url
                    if dataset is not None:
                        safe_url = dataset.get("url", url)
                    fail_file.write(safe_url + "\n")
                    continue

                file_name = str(dataset["id"]) + ".json"
                path_name = os.path.join(directory, file_name)
                with open(path_name, 'w') as f:
                    json.dump(dataset, f)
                AnimePageFetcher.cooldown()
            fail_file.flush()
        fail_file.close()
        print "Done year", year

def fix_fails(group):
    group = str(group)
    print "Starting to fix fails for group", group

    directory = os.path.join(data_directory, group)
    error_file_name = fail_filename_format % group
    error_path = os.path.join(directory, error_file_name)
    if not os.path.isfile(error_path):
        print "Expected failure file", error_path, "does not exist."
        return
    with open(error_path, 'r') as f:
        urls = [l.strip() for l in f.readlines()]

    fails = []
    for url in urls:
        success, dataset = AnimePageFetcher.getAllDataFromUrl(url)

        if not success:
            safe_url = url
            if dataset is not None:
                safe_url = dataset.get("url", url)
            fails.append(safe_url)
            continue

        data_file_name = str(dataset["id"]) + ".json"
        data_path_name = os.path.join(directory, data_file_name)
        with open(data_path_name, 'w') as f:
            json.dump(dataset, f)
        AnimePageFetcher.cooldown()
    
    os.remove(error_path)
    if len(fails) > 0:
        with open(error_path, 'w') as f:    # Mode 'w' for overwrite, since we're trying to fix things.
            f.write("\n".join(fails))
    
    print "Done fixing fails for group", group

# Iterates through a folder and checks all json objects have the correct keys
def validate_existing(group):
    group = str(group)
    directory = os.path.join(data_directory, group)
    if not os.path.exists(directory):
        print "Directory for group %s does not exist" % group
        return

    error_file_name = fail_filename_format % group
    error_path = os.path.join(directory, error_file_name)
    error_file = open(error_path, 'a')

    print "Starting validation"
    dir_list = os.listdir(directory)
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(directory, filename)) as f:
            data = json.load(f)
            if not AnimePageFetcher.validate(data):
                print data["url"], "was not valid."
                error_file.write(data["url"] + "\n")

    error_file.close()
    print "Done validation"

def check_missing(year):
    group = str(year)
    directory = os.path.join(data_directory, group) 
    if not os.path.exists(directory):
        print "Directory for group %s does not exist" % group
        return
    dir_list = os.listdir(directory)

    error_file_name = fail_filename_format % group
    error_path = os.path.join(directory, error_file_name)
    fail_file = open(error_path, 'a')     # 'a' for append. Capture all failures until fix

    print "Checking missing"
    for season in ["winter","spring","summer","fall"]:
        print "Grabbing links for", str(group)+"_"+season 
        animeURLS = SeasonLinkScraper.get_season_anime(year, season)
        for url in animeURLS:
            url = AnimePageFetcher.get_safe_url(url)
            (cat, page_id) = AnimePageFetcher.getCategoryAndIDFromUrl(url)
            if str(page_id)+".json" not in dir_list:
                print "Missing", url
                fail_file.write(url + "\n")
        print "Done", str(group)+"_"+season 
    fail_file.close()


if len(sys.argv) > 1:
    grab_data([int(i) for i in sys.argv[1:]])
else:
    print "Use: python Main.py <year1> <year2>"
