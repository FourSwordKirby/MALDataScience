import SeasonLinkScraper
import AnimePageFetcher
import os
import json

years = [2014]#, 2013, 2014, 2015]
seasons = ["winter", "fall", "summer", "spring"]

for year in years:
    for season in seasons:
        print str(year)+"_"+season+".txt"

        directory = str(year)+"_"+season
        if not os.path.exists(directory):
            os.makedirs(directory)

        animeURLS = SeasonLinkScraper.get_season_anime(year, season)
        for url in animeURLS:
            dataset = AnimePageFetcher.getAllDataFromUrl(url)
            json.dumps(dataset, dataset["title"])
            AnimePageFetcher.cooldown()