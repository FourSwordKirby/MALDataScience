import json 
import os
import numpy as np
import pandas as pd


rootdir = "data/"


def read_files(dir = rootdir, write_csv = False):
	count = 0
	data_frames = []

	for root, dirs, files in os.walk(dir):
		for name in files:
			with open(os.path.join(root, name)) as json_data:
				data = json.load(json_data)
				
				data["genres"] = str(data["genres"])
				data["producers"] = str(data["producers"])
				data["licensors"] = str(data["licensors"])
				#hack to get around arrays of unequal size, I know it's slow
				#df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.iteritems() ]))

				df = pd.DataFrame(data)
				data_frames.append(df)
				count += 1
	assert(len(data_frames) == count)
	all_data = pd.concat(data_frames)

	if write_csv:
		all_data.to_csv("MALData.csv", encoding='utf-8')

	return all_data



read_files("data", write_csv = True)