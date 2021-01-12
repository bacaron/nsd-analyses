#!/usr/bin/env python3
aaa
import os,sys,glob
from matplotlib import colors as mcolors
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

### setting up variables and adding paths
print("setting up variables")

# load config.json
with open('config.json','r') as config_f:
	config = json.load(config_f)

# set up variables from config
topPath = config['topPath']
scripts_dir = topPath+'/'+config['scriptsPath']
utils_dir = scripts_dir+'/'+config['utilsPath']
configs_dir = scripts_dir+'/'+config['configsPath']
groups = config['groups'].split()
diff_measures = config['diffusion_measures'].split()
colors_array = config['colors'].split()
num_nodes = config['number_of_nodes']

# make topPath directory if not already existing
if not os.path.isdir(topPath):
	os.mkdir(topPath)

# set up utils, data and img directories
data_dir = topPath+'/data/'
if not os.path.exists(data_dir):
	os.mkdir(data_dir)
img_dir = topPath+'/img/'
if not os.path.exists(img_dir):
	os.mkdir(img_dir)
sys.path.insert(0,scripts_dir)
sys.path.insert(1,utils_dir)

colors = {}
subjects = {}

# loop through groups and identify subjects and set color schema for each group
for g in range(len(groups)):
	# set subjects array
	subjects[groups[g]] =  [f.split(topPath+'/')[1] for f in glob.glob(topPath+'/*subj*') if os.path.isdir(f)]
	subjects[groups[g]].sort()

	# set colors array
	colors_name = colors_array[g]
	colors[groups[g]] = colors_array[g]
print("setting up variables complete")

### create subjects.csv
print("creating subjects.csv")
from compile_data import collectSubjectData
subjects_data = collectSubjectData(topPath,data_dir,groups,subjects,colors)
print("creating subjects.csv complete")

# create subjects color dictionary for scatterplots
from compile_data import createColorDictionary
colors_dict = createColorDictionary(subjects_data,'subjectID','jet')

### generate snr plot
print("plotting snr data")
# grab data
from compile_data import collectSNRData
snr = collectSNRData(topPath,data_dir,groups,subjects)

# plot data
from plotting import plotSNR
plotSNR(list(snr['snr']),list(snr['subjectID']),list(subjects_data['colors']),dir_out=img_dir)
print("plotting snr data complete")

### cortex mapping results
print("plotting cortex mapping results")
from analyses import cortex_mapping_analyses
cortex_glasser, cortex_aparc = cortex_mapping_analyses(topPath,groups,subjects,data_dir,img_dir,diff_measures+['volume','thickness'],colors_dict,colors)
print("plotting cortex mapping results complete")

### tract profilometry results
print("plotting tract profilometry results")
from analyses import tract_profile_analyses
track_data, track_data_cut, track_data_cut_mean = tract_profile_analyses(topPath,groups,subjects,data_dir,img_dir,diff_measures+['length','volume','count'],colors_dict,num_nodes,colors)
print("plotting tract profilometry results complete")

### network analyses
print("plotting network results")
from analyses import network_analyses
networks_density, networks_fa, nonzero_index, study_nonzero_index, networks_density_thrs_matrices, networks_fa_thrs_matrices, networks_density_mean, networks_fa_mean = network_analyses(topPath,groups,subjects,data_dir,img_dir,configs_dir,'distinct')
print("plotting network results complete")
