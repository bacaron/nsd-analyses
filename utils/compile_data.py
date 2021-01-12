#!/usr/bin/env python

import os,glob,sys
import numpy as np
import pandas as pd
import json

### subjects
def collectSubjectData(topPath,dataPath,groups,subjects,colors):

	# set up variables
	data_columns = ['subjectID','classID','colors']
	data =  pd.DataFrame([],columns=data_columns)

	# populate structure
	data['subjectID'] = [ f for g in groups for f in subjects[g] ]
	data['classID'] = [ g for g in groups for f in range(len(subjects[g]))]
	data['colors'] = [ colors[c] for c in colors for f in subjects[c]]

	# output data structure for records and any further analyses
	if not os.path.exists(dataPath):
		os.mkdir(dataPath)

	data.to_csv(dataPath+'subjects.csv',index=False)

	return data

### color dictionary
def createColorDictionary(data,measure,colorPalette,values):
	import seaborn as sns

	keys = data[measure].unique()

	if not values:
		if colorPalette is 'jet':
			import matplotlib
			from matplotlib import cm
			from matplotlib.colors import ListedColormap, LinearSegmentedColormap

			jet = cm.get_cmap('jet',len(keys))
			values_rgb = jet(np.linspace(0,1,len(keys)))
			values = [ matplotlib.colors.to_hex(values_rgb[i]) for i in range(len(values_rgb)) ]
		else:
			values = sns.color_palette(colorPalette,len(keys))
			values = values.as_hex()

	colors_dict = dict(zip(keys,values))

	return colors_dict

### load parcellation stats data 
def collectData(topPath,foldername,filename,dataPath,groups,subjects,savename):
	
	data =  pd.DataFrame([])

	for g in range(len(groups)):
		for s in range(len(subjects[groups[g]])):
			tmpdata = pd.read_csv(topPath+'/'+subjects[groups[g]][s]+'/'+groups[g]+'/'+foldername+'/'+filename)
			tmpdata['subjectID'] = [ str(f) for f in tmpdata['subjectID'] ]
			tmpdata['classID'] = [ groups[g] for f in range(len(tmpdata['subjectID'])) ]
			data = data.append(tmpdata,ignore_index=True)

	# output data structure for records and any further analyses
	if not os.path.exists(dataPath):
		os.mkdir(dataPath)

	data.to_csv(dataPath+'/'+foldername+'-'+savename+'.csv',index=False)

	return data

### cut nodes
def cutNodes(data,num_nodes,dataPath,foldername,savename):
	# identify inner n nodes based on num_nodes input
	total_nodes = len(data['nodeID'].unique())
	cut_nodes = int((total_nodes - num_nodes) / 2)

	# remove cut_nodes from dataframe
	data = data[data['nodeID'].between((cut_nodes)+1,(num_nodes+cut_nodes))]

	# replace empty spaces with nans
	data = data.replace(r'^\s+$', np.nan, regex=True)

	# output data structure for records and any further analyses
	if not os.path.exists(dataPath):
		os.mkdir(dataPath)

	data.to_csv(dataPath+'/'+foldername+'-'+savename+'.csv',index=False)

	return data

### snr data
def load_snr_stat(snr_json):

	dim = len(snr_json["SNR in b0, X, Y, Z"])
	snr_data = np.zeros(dim)
	for i in range(dim):
	    snr_data[i] = float(snr_json["SNR in b0, X, Y, Z"][i])
	    
	return snr_data

def collectSNRData(topPath,dataPath,groups,subjects):
	from compile_data import load_snr_stat
	import json

	# set up variables
	snr = []
	data = pd.DataFrame([])
	data_columns = ['subjectID','snr']

	for g in range(len(groups)):
		for s in range(len(subjects[groups[g]])):
			filepath = str(topPath+'/'+str(subjects[groups[g]][s])+'/'+groups[g]+'/snr/output/snr.json')
			with open(filepath) as filepath_j:
				config = json.load(filepath_j)
			snr.append(load_snr_stat(config))

	data['subjectID'] = [ f for g in groups for f in subjects[g] ]
	data['snr'] = snr

	# output data structure for records and any further analyses
	if not os.path.exists(dataPath):
		os.mkdir(dataPath)

	data.to_csv(dataPath+'snr.csv',index=False)

	return data

# compute mean data
def computeMeanData(dataPath,data,foldername,savename):

	# make mean data frame
	data_mean =  data.groupby(['subjectID','classID','structureID']).mean().reset_index()
	data_mean['nodeID'] = [ 1 for f in range(len(data_mean['nodeID'])) ]

	# output data structure for records and any further analyses
	if not os.path.exists(dataPath):
		os.mkdir(dataPath)
	
	data_mean.to_csv(dataPath+'/'+foldername+'-'+savename+'.csv',index=False)

	return data_mean

### networks
# aggregate network matrices measures
def aggregateMatrices(topPath,foldername,filename,dataPath,groups,subjects,savename):
	import os,sys
	import json
	import csv
	import numpy as np

	networks = {}
	
	for g in range(len(groups)):
		networks[groups[g]] = []
		for s in range(len(subjects[groups[g]])):
			tmpdata = np.genfromtxt(os.path.join(topPath+'/'+subjects[groups[g]][s]+'/'+groups[g]+'/'+foldername+'/'+filename), delimiter=',')
			networks[groups[g]].append(tmpdata)

	return networks

# compute binarized matrix
def binarizeMatrices(matrices):

	bin_matrices = {}
	for g in matrices.keys():
		bin_matrices[g] = np.array(matrices[g])

		for i in range(len(bin_matrices[g])):
			bin_matrices[g][i][bin_matrices[g][i] > 0] = 1

	return bin_matrices

# identify thresholded indices
def findThresholdIndex(binary_matrices,threshold):

	nonzero_index = {}
	sum_array = {}

	for g in binary_matrices.keys():
		nonzero_index[g] = np.zeros(np.shape(binary_matrices[g][0]))
		sum_array[g] = binary_matrices[g][0]

		for i in range(len(binary_matrices[g])):
			if i > 0:
				sum_array[g] = np.add(sum_array[g],binary_matrices[g][i])

		for m in range(np.shape(sum_array[g])[0]):
			for n in range(np.shape(sum_array[g])[1]):
				if sum_array[g][m][n] >= threshold:
					nonzero_index[g][m][n] = 1
				else:
					nonzero_index[g][m][n] = 0
	
	study_nonzero_index = np.zeros(np.shape(nonzero_index[list(binary_matrices.keys())[0]]))
	for m in range(np.shape(study_nonzero_index)[0]):
		for n in range(np.shape(study_nonzero_index)[1]):
			if nonzero_index[list(binary_matrices.keys())[0]][m][n] == nonzero_index[list(binary_matrices.keys())[1]][m][n]:
				study_nonzero_index[m][n] = nonzero_index[list(binary_matrices.keys())[0]][m][n]
			else:
				study_nonzero_index[m][n] = 0

	return nonzero_index, study_nonzero_index

# threshold matrix
def thresholdMatrices(matrices,study_nonzero_index):

	thrs_matrices = {}

	for g in matrices.keys():
		thrs_matrices[g] = np.zeros(np.shape(matrices[g]))
		
		for i in range(len(matrices[g])):
			thrs_matrices[g][i] = np.multiply(matrices[g][i],study_nonzero_index)

	return thrs_matrices
