import os
import json
import AnimePageFetcher
import SeasonLinkScraper

years = [2014]#, 2013, 2014, 2015]
seasons = ["winter", "fall", "summer", "spring"]

fail_filename_format = "failures_%s.txt"

def grab_data(years, seasons):
    for year in years:
        for season in seasons:
            group = str(year)+"_"+season
            fails = []

            directory = group
            if not os.path.exists(directory):
                os.makedirs(directory)

            animeURLS = SeasonLinkScraper.get_season_anime(year, season)
            AnimePageFetcher.cooldown()
            for url in animeURLS:
                success, dataset = AnimePageFetcher.getAllDataFromUrl(url)

                if not success:
                    safe_url = url
                    if dataset is not None:
                        safe_url = dataset.get("url", url)
                    fails.append(safe_url)
                    continue

                file_name = str(dataset["id"]) + ".json"
                path_name = os.path.join(directory, file_name)
                with open(path_name, 'w') as f:
                    json.dump(dataset, f)
                AnimePageFetcher.cooldown()
                
            if len(fails) > 0:
                error_file_name = fail_filename_format % group
                error_path = os.path.join(directory, error_file_name)
                with open(error_path, 'w') as f:
                    f.write("\n".join(fails))

def fix_fails(group):
    print "Starting to fix fails for group", group

    fname = fail_filename_format % group
    directory = group
    with open(os.path.join(directory, fname), 'r') as f:
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

        file_name = str(dataset["id"]) + ".json"
        path_name = os.path.join(directory, file_name)
        with open(path_name, 'w') as f:
            json.dump(dataset, f)
        AnimePageFetcher.cooldown()
    
    if len(fails) > 0:
        error_file_name = fail_filename_format % group
        error_path = os.path.join(directory, error_file_name)
        with open(error_path, 'w') as f:
            f.write("\n".join(fails))
    
    print "Done fixing fails for group", group
