# Anime Trends Based on MyAnimeList

Authors: Stephen Chen, Roger Liu, Sean Reidy

Data analytics performed on MyAnimeList.

## Reports
Our final report can be found at Final_report.ipynb. It is fully runnable from start to finish so long as the contents of this repository are present. The bare minimums are:

* the `image/` folder
* `augmented_1998_2015_data.pkl` pickle file, which has all of the MAL anime data assembled.

Every other juypter notebook involves our individual analysis of data. Running those might be a difficult as we tended to move code blocks around during our work phases.

The Rcode/ folder contains R code that we used, primarily for text analysis.
 
## MAL Scraper

The Scraper consists of:

* `./AnimePageFetcher.py`
* `./SeasonLinkScraper.py`
* `./Main.py`

To collect a years of data, run

```python
python Main.py 2015 2014 2013
```

The arguments after `Main.py` are the years to collect.

Data is automatically stored at `data/<year>/`

Failures are logged in a `failures.txt` file.

`Main.py` also contains a few other functions to help validate and check for missing entries. The argument to those functions is the year of data to validate or check.