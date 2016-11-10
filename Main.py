import os
import json
import AnimePageFetcher
import SeasonLinkScraper

years = [2014]#, 2013, 2014, 2015]
seasons = ["winter", "fall", "summer", "spring"]


for year in years:
    for season in seasons:
        print "Starting on", str(year)+"_"+season
        fails = []

        directory = str(year)+"_"+season
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
        
        error_file_name = "failures_"+str(year)+"_"+season+".txt"
        error_path = os.path.join(directory, error_file_name)
        with open(error_path, 'w') as f:
            f.write("\n".join(fails))