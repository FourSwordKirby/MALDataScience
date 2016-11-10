import os
import json
import AnimePageFetcher
import SeasonLinkScraper

years = [2014]#, 2013, 2014, 2015]
seasons = ["winter", "fall", "summer", "spring"]

for year in years:
    for season in seasons:
        print str(year)+"_"+season+".txt"

        directory = str(year)+"_"+season
        if not os.path.exists(directory):
            os.makedirs(directory)

        animeURLS = SeasonLinkScraper.get_season_anime(year, season)
        AnimePageFetcher.cooldown()
        for url in animeURLS:
            dataset = AnimePageFetcher.getAllDataFromUrl(url)
            file_name = str(dataset["id"]) + ".json"
            path_name = os.path.join(directory, file_name)
            with open(path_name, 'w') as f:
                json.dump(dataset, f)
            AnimePageFetcher.cooldown()