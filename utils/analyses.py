#!/usr/bin/env python3

def cortex_mapping_analyses(topPath,groups,subjects,data_dir,img_dir,cortex_map_measures,colors_dict,colors):

	from compile_data import collectData
	from plotting import singleplotScatter, plotGroupStructureAverage

	# glasser regions
	cortex_glasser = collectData(topPath,"parc_stats_cortex","parc_MEAN.csv",data_dir,groups,subjects,'glasser')

	# clean up
	cortex_glasser = cortex_glasser[~cortex_glasser['structureID'].str.contains('unknown')]

	# plot data
	print("glasser")
	for measures in cortex_map_measures:
		print(measures)
		singleplotScatter(colors_dict,cortex_glasser[cortex_glasser['classID'] == groups[0]],cortex_glasser[cortex_glasser['classID'] == groups[1]],measures,measures,'structureID','subjectID','ravel','equality',True,img_dir,"cortex_map_glasser")
	plotGroupStructureAverage(groups,colors,cortex_glasser['structureID'].unique(),cortex_glasser,cortex_map_measures,'mean','sem',img_dir,'cortex_map_glasser')
	print("glasser complete")

	# aparc a2009s regions
	cortex_aparc = collectData(topPath,"parc_stats_cortex","aparc_MEAN.csv",data_dir,groups,subjects,'aparc-a2009s')

	# plot data
	print("aparc")
	for measures in cortex_map_measures:
		print(measures)
		singleplotScatter(colors_dict,cortex_aparc[cortex_aparc['classID'] == groups[0]],cortex_aparc[cortex_aparc['classID'] == groups[1]],measures,measures,'structureID','subjectID','ravel','equality',True,img_dir,"cortex_map_aparc")
	plotGroupStructureAverage(groups,colors,cortex_aparc['structureID'].unique(),cortex_aparc,cortex_map_measures,'mean','sem',img_dir,'cortex_map_aparc')
	print("aparc complete")

	return cortex_glasser, cortex_aparc

def tract_profile_analyses(topPath,groups,subjects,data_dir,img_dir,diff_micro_measures,colors_dict,num_nodes,colors):

	from compile_data import collectData
	from compile_data import computeMeanData
	from compile_data import cutNodes
	from plotting import singleplotScatter, plotGroupStructureAverage, plotProfiles

	### tract profiles
	track_data = collectData(topPath,"tractmeasures","output_FiberStats.csv",data_dir,groups,subjects,'wmaSeg')

	# cut nodes
	from compile_data import cutNodes
	track_data_cut = cutNodes(track_data,num_nodes,data_dir,"tractmeasures",'wmaSeg-cut')

	# compute mean data
	from compile_data import computeMeanData
	track_data_cut_mean = computeMeanData(data_dir,track_data_cut,"tractmeasures",'wmaSeg-cut-mean')

	# plot data
	print("wmaSeg")
	print('scatter')
	for measures in diff_micro_measures:
		print(measures)
		singleplotScatter(colors_dict,track_data_cut_mean[track_data_cut_mean['classID'] == groups[0]],track_data_cut_mean[track_data_cut_mean['classID'] == groups[1]],measures,measures,'structureID','subjectID','ravel','equality',True,img_dir,"track_scatter")
	
	print('group average per structure')
	plotGroupStructureAverage(groups,colors,track_data_cut_mean['structureID'].unique(),track_data_cut_mean,diff_micro_measures,'mean','sem',img_dir,'wmaSeg')
	
	# print('tract profiles')
	# plotProfiles(groups,colors,track_data_cut['structureID'].unique(),track_data_cut,[ f for f in diff_micro_measures if f not in ['length','count','volume'] ],'mean','sem',img_dir,'wmaSeg')

	print("wmaSeg complete")

	return track_data, track_data_cut, track_data_cut_mean

def network_analyses(topPath,groups,subjects,data_dir,img_dir,configs_dir,colormap):

	import numpy as np
	import pandas as pd
	from compile_data import aggregateMatrices, createColorDictionary
	from plotting import networkScatter

	# grab network labels
	with open(configs_dir+'/labels.txt','r') as labels:
		network_labels = labels.read().splitlines()

	# create data frame of labels and color dictionary
	labels = pd.DataFrame(network_labels,columns={'parcels'})

	if colormap == 'distinct':
		# grab distinct colormap
		with open(configs_dir+'/distinct_colors.txt','r') as colors: 
			distinct_colors = colors.read().split(",")
	else:
		distinct_colors = ""

	networks_dict = createColorDictionary(labels,'parcels',colormap,distinct_colors)

	# create hues array for scatterplot. data will be unraveled row-wise. hue is based on row-parcel
	structures_array = []
	for g in range(len(labels['parcels'])):
		structures_array = structures_array + [ labels['parcels'][g] for f in range(len(labels['parcels'])) ]

	### density
	networks_density = aggregateMatrices(topPath,'vm-networks','output/density.csv',data_dir,groups,subjects,'density')

	# identify thresholded matrix to index
	from compile_data import binarizeMatrices, findThresholdIndex
	binary_matrices = binarizeMatrices(networks_density)
	nonzero_index, study_nonzero_index = findThresholdIndex(binary_matrices,0.5)

	# threshold density matrices for each subject
	from compile_data import thresholdMatrices
	networks_density_thrs_matrices = thresholdMatrices(networks_density,study_nonzero_index)
	
	# compute mean and plot
	print("network density")
	networks_density_mean = {}
	for g in groups:
		networks_density_mean[g] = np.mean(networks_density_thrs_matrices[g],axis=0)
	networkScatter(networks_dict,structures_array,groups,subjects,networks_density_mean['run_1'],networks_density_mean['run_2'],'density',True,"equality",img_dir,'network-density-scatter')
	print("network density complete")

	### fa
	# grab data
	networks_fa = aggregateMatrices(topPath,'vm-networks','output/fa_mean.csv',data_dir,groups,subjects,'fa')
	
	# threshold data
	networks_fa_thrs_matrices = thresholdMatrices(networks_fa,study_nonzero_index)
	
	# compute mean and compute
	print("network fa")
	networks_fa_mean = {}
	for g in groups:
		networks_fa_mean[g] = np.mean(networks_fa_thrs_matrices[g],axis=0)
	networkScatter(networks_dict,structures_array,groups,subjects,networks_fa_mean['run_1'],networks_fa_mean['run_2'],'fa',True,"equality",img_dir,'network-fa-scatter')
	print("network fa complete")

	return networks_density, networks_fa, nonzero_index, study_nonzero_index, networks_density_thrs_matrices, networks_fa_thrs_matrices, networks_density_mean, networks_fa_mean
