import json 
import os
import numpy as np
import pandas as pd


rootdir = "data/"

'''
read_files_all

Reads each json file into pandas dataframe.
To get around the fact that genra tags are lists of unequal len, 
genra tags are cast to strings 

Args: 
dir - root dir of all json files from scraping 
write_csv - bool, copy dataframe to csv if true
remove_dupl - bool, if True does not add entry to dataframe if duplicate. 

Returns: 
all_data - dataframe of all json files 
'''


def read_files_all(dir = rootdir, write_csv = False, remove_dupl = True, verbose=False):
	count = 0
	data_frames = []
	all_genres, all_producers, all_licensors = get_all_lists(dir)
	for root, dirs, files in os.walk(dir):
		for name in files:
			with open(os.path.join(root, name)) as json_data:
				data = json.load(json_data)

				temp_genre_list = [x.lower() for x in data["genres"]]
				data["genres"] = str(data["genres"])
				data["producers"] = str(data["producers"])
				data["licensors"] = str(data["licensors"])
				data["studios"] = str(data["studios"])
				#hack to get around arrays of unequal size, I know it's slow
				#df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.iteritems() ]))
				df = pd.DataFrame(data, index=[0])

				# Genre Duumy Vars 
				for i in all_genres:
					df[i] = 0
				for j in temp_genre_list:
					df[j] = 1

				data_frames.append(df)
				count += 1
		if verbose: print "Finished", root
	assert(len(data_frames) == count)
	all_data = pd.concat(data_frames)

	if remove_dupl:
		all_data = all_data.drop_duplicates()

	if write_csv:
		all_data.to_csv("MALData.csv", encoding='utf-8')

	return (all_data, all_genres)



'''
all genres, unedeted

[u'Mystery', u'Psychological', u'Sci-Fi', u'Supernatural', u'Comedy', u'Shounen',
 u'Slice of Life', u'Ecchi', u'School', u'Seinen', u'Action', u'Fantasy', u'Drama',
  u'Hentai', u'Kids', u'Super Power', u'Shoujo', u'Shounen Ai', u'Parody', u'Adventure',
   u'Romance', u'Police', u'Horror', u'Martial Arts', u'Mecha', u'Military', u'Space', u'Sports', u'Magic',
    u'Harem', u'Historical', u'Game', u'Thriller', u'Yuri', u'Shoujo Ai', u'Yaoi', u'Demons', u'Music', u'Samurai',
     u'Vampire', u'Cars', u'Dementia', u'Josei', u'No genres have been added yet.']


'''

def get_all_lists(dir = rootdir):
	count = 0 
	all_genres = []
	all_producers = []
	all_licensors = []
	for root, dirs, files in os.walk(dir):
		for name in files:
			with open(os.path.join(root, name)) as json_data:
				data = json.load(json_data)
				genres = [x.lower() for x in data["genres"]]
				producers = [x.lower() for x in data["producers"]]
				licensors = [x.lower() for x in data["licensors"]]
				for n in xrange(len(genres)):
					#if genres[n] == "action":
					#	count += 1
					if genres[n] not in all_genres:
						all_genres.append(genres[n]) 
				for n in xrange(len(producers)):
					if producers[n] not in all_producers:
						all_producers.append(producers[n]) 
				for n in xrange(len(licensors)):
					if licensors[n] not in all_licensors:
						all_licensors.append(licensors[n]) 

	# Yea ... I dont want that in the project 		
	# SC: We'll remove in the analysis or something.
	# all_genres.remove("hentai")
	#print count
	return (all_genres, all_producers, all_licensors)

# TODO
''''
read_files_by_year

Reads each json file into diffrent pandas dataframes by the year
To get around the fact that genra tags are lists of unequal len, 
genra tags are cast to strings 

Args: 
dir - root dir of all json files from scraping 
write_csv - bool, copy dataframe to csv if true
remove_dupl - bool, if True does not add entry to dataframe if duplicate. 

Returns: 
all_data - list of dataframes of all json files.
'''

def read_files_by_year(dir = rootdir, write_csv = False, remove_dupl = True):
	pass


