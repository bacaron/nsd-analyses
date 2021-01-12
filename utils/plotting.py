#!/usr/bin/env python3

import os, sys

### scatter plot related scripts
# groups data by input measure and computes mean for each value in that column. x_stat is a pd dataframe, with each row being a single value, and each column being a different ID value or measure
def averageWithinColumn(x_stat,y_stat,x_measure,y_measure,measure):
	
	X = x_stat.groupby(measure).mean()[x_measure].tolist()
	Y = y_stat.groupby(measure).mean()[y_measure].tolist()

	return X,Y

# groups data by input measure and creates an array by appending data into x and y arrays. x_stat and y_stat are pd dataframes, with each row being a single value, and each column being a different ID value or measure
# designed for test retest. x_stat and y_stat should have the same number of rows. but more importantly, should correspond to the same source (i.e. subject)
# can be same pd.dataframe, but indexing of specific subject groups
def appendWithinColumn(x_stat,y_stat,x_measure,y_measure,measure):

	X,Y = [np.array([]),np.array([])]
	for i in range(len(x_stat[measure].unique())):
		x = x_stat[x_stat[measure] == x_stat[measure].unique()[i]][x_measure]
		y = y_stat[y_stat[measure] == y_stat[measure].unique()[i]][y_measure]

		if np.isnan(x).any() or np.isnan(y).any():
			print("skipping %s due to nan" %x_stat[measure].unique()[i])
		else:
			# checks to make sure the same data
			if len(x) == len(y):
				X = np.append(X,x)
				Y = np.append(Y,y)

	return X,Y

# unravels networks. x_stat and y_stat should be S x M, where S is the number of subjects and M is the adjacency matrix for that subject
def ravelNetwork(x_stat,y_stat):
	
	import numpy as np

	X = np.ravel(x_stat).tolist()
	Y = np.ravel(y_stat).tolist()

	return X,Y

# unravels nonnetwork data. x_stat and y_stat should be pd dataframes. x_measure and y_measure are the measure to unrvavel. 
# designed for test retest. x_stat and y_stat should have the same number of rows. but more importantly, should correspond to the same source (i.e. subject)
# can be same pd.dataframe, but indexing of specific subject groups
def ravelNonNetwork(x_stat,y_stat,x_measure,y_measure):
	
	X = x_stat[x_measure].to_list()
	Y = y_stat[y_measure].to_list()

	return X,Y

# wrapper function to call either of the above scripts based on user input
def setupData(x_data,y_data,x_measure,y_measure,ravelAverageAppend,isnetwork,measure):
	
	x_stat = x_data
	y_stat = y_data
	
	if ravelAverageAppend == 'average':
		X,Y = averageWithinColumn(x_stat,y_stat,x_measure,y_measure,measure)
	elif ravelAverageAppend == 'append':
		X,Y = appendWithinColumn(x_stat,y_stat,x_measure,y_measure,measure)
	elif ravelAverageAppend == 'ravel':
		if isnetwork == True:
			X,Y = ravelNetwork(x_stat,y_stat)
		else:
			X,Y = ravelNonNetwork(x_stat,y_stat,x_measure,y_measure)

	return x_stat,y_stat,X,Y

# function to shuffle data and colors
def shuffleDataAlg(X,Y,hues):
	
	from sklearn.utils import shuffle

	X,Y,hues = shuffle(X,Y,hues)

	return X,Y,hues

# simple display or figure save function
def saveOrShowImg(dir_out,x_measure,y_measure,img_name):
	import os,sys 
	import matplotlib.pyplot as plt
	# save or show plot
	if dir_out:
		if not os.path.exists(dir_out):
			os.mkdir(dir_out)

		if x_measure == y_measure:
			img_name_eps = img_name+'_'+x_measure+'.eps'
			img_name_png = img_name+'_'+x_measure+'.png'
		else:
			img_name_eps = img_name+'_'+x_measure+'_vs_'+y_measure+'.eps'
			img_name_png = img_name+'_'+x_measure+'_vs_'+y_measure+'.png'			

		plt.savefig(os.path.join(dir_out, img_name_eps))
		plt.savefig(os.path.join(dir_out, img_name_png))       
	else:
		plt.show()

	plt.close()

# uses seaborn's relplot function to plot data for each unique value in a column of a pandas dataframe (ex. subjects, structureID). useful for supplementary figures or sanity checking or preliminary results
# column measure is the measure within which each unique value will have its own plot. hue_measure is the column to use for coloring the data. column_wrap is how many panels you want per row
# trendline, depending on user input, can either be the linear regression between x_data[x_measure] and y_data[y_measure] or the line of equality
# dir_out and img_name are the directory where the figures should be saved and the name for the image. will save .eps and .png
# if want to view plot instead of save, set dir_out=""
def relplotScatter(x_data,y_data,x_measure,y_measure,column_measure,hue_measure,column_wrap,trendline,dir_out,img_name):
	
	import os,sys
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	from sklearn.metrics import mean_squared_error

	# grab data: CANNOT BE AVERAGE
	[x_stat,y_stat,X,Y] = setupData(x_data,y_data,x_measure,y_measure,'ravel',False,hue_measure)
	
	p = sns.relplot(x=X,y=Y,col=x_stat[column_measure],hue=x_stat[hue_measure],kind="scatter",s=100,col_wrap=column_wrap)
	
	# setting counter. looping through axes to add important info and regression lines
	i = 0
	for ax in p.axes.flat:
		x_lim,y_lim = [ax.get_xlim(),ax.get_ylim()]

		if trendline == 'equality':
			ax.plot(x_lim,y_lim,ls="--",c='k')
		elif trendline == 'linreg':
			m,b = np.polyfit(p.data[p.data[column_measure] == x_stat[column_measure].unique()[i]]['x'],p.data[p.data[column_measure] == y_stat[column_measure].unique()[i]]['y'],1)
			ax.plot(ax.get_xticks(),m*ax.get_xticks() + b)
			plt.text(0.1,0.7,'y = %s x + %s' %(str(np.round(m,4)),str(np.round(b,4))),fontsize=12,verticalalignment="top",horizontalalignment="left",transform=ax.transAxes)

		ax.set_xlim(x_lim)
		ax.set_ylim(y_lim)
		ax.set_xlabel(x_measure)
		ax.set_ylabel(y_measure)

		# compute correlation for each subject and add to plots
		corr = np.corrcoef(p.data[p.data[column_measure] == x_stat[column_measure].unique()[i]]['x'],p.data[p.data[column_measure] == y_stat[column_measure].unique()[i]]['y'])[1][0]
		plt.text(0.1,0.9,'r = %s' %str(np.round(corr,4)),fontsize=12,verticalalignment="top",horizontalalignment="left",transform=ax.transAxes)
		
		# compute rmse for each subject and add to plots
		rmse = np.sqrt(mean_squared_error(p.data[p.data[column_measure] == x_stat[column_measure].unique()[i]]['x'],p.data[p.data[column_measure] == y_stat[column_measure].unique()[i]]['y']))
		plt.text(0.1,0.8,'rmse = %s' %str(np.round(rmse,4)),fontsize=12,verticalalignment="top",horizontalalignment="left",transform=ax.transAxes)

		# update counter
		i = i+1

	# save image or show image
	saveOrShowImg(dir_out,x_measure,y_measure,img_name)

# uses seaborn's scatter function to plot data from x_data[x_measure] and y_data[y_measure]. useful for publication worthy figure
# column measure is the measure within which data will be summarized. hue_measure is the column to use for coloring the data. 
# ravelAverageAppend is a string value of either 'append' to use the append function, 'ravel' to use the ravel function, or 'average' to use the average function
# trendline, depending on user input, can either be the linear regression between x_data[x_measure] and y_data[y_measure] or the line of equality
# dir_out and img_name are the directory where the figures should be saved and the name for the image. will save .eps and .png
# if want to view plot instead of save, set dir_out=""
def singleplotScatter(colors_dict,x_data,y_data,x_measure,y_measure,column_measure,hue_measure,ravelAverageAppend,trendline,shuffleData,dir_out,img_name):
	
	import os,sys
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	from sklearn.metrics import mean_squared_error

	# grab data
	[x_stat,y_stat,X,Y] = setupData(x_data,y_data,x_measure,y_measure,ravelAverageAppend,False,column_measure)
	colors = sns.color_palette('colorblind',len(x_stat[hue_measure]))
	
	if ravelAverageAppend == 'average':
		if isinstance(x_stat[hue_measure].unique()[0],str):
			hues = x_stat[hue_measure].unique().tolist()
		else:
			hues = x_stat.groupby(column_measure).mean()[hue_measure].tolist()
	else:
		hues = list(x_stat[hue_measure])

	if shuffleData == True:
		X,Y,hues = shuffleDataAlg(X,Y,hues)
	
	if colors_dict:
		p = sns.scatterplot(x=X,y=Y,hue=hues,s=100,palette=colors_dict,legend=False)
	else:
		p = sns.scatterplot(x=X,y=Y,hue=hues,s=100)					

	# set x and ylimits, plot line of equality, and legend
	if x_measure == y_measure:
		p.axes.axis('square')
		y_ticks = p.axes.get_yticks()
		p.axes.set_xticks(y_ticks)
		p.axes.set_yticks(p.axes.get_xticks())
		p.axes.set_ylim(p.axes.get_xlim())
		p.axes.set_xlim(p.axes.get_xlim())

	x_lim,y_lim = [p.axes.get_xlim(),p.axes.get_ylim()]

	# trendline: either equality or linear regression
	if trendline == 'equality':
		p.plot(x_lim,y_lim,ls="--",c='k')
	elif trendline == 'linreg':
		m,b = np.polyfit(X,Y,1)
		p.plot(p.get_xticks(),m*p.get_xticks() + b,c='k')
		plt.text(0.1,0.7,'y = %s x + %s' %(str(np.round(m,4)),str(np.round(b,4))),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# compute correlation for each subject and add to plots
	corr = np.corrcoef(X,Y)[1][0]
	plt.text(0.1,0.9,'r = %s' %str(np.round(corr,4)),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# compute rmse for each subject and add to plots
	rmse = np.sqrt(mean_squared_error(X,Y))
	plt.text(0.1,0.8,'rmse = %s' %str(np.round(rmse,4)),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# set title and x and y labels
	plt.title('%s vs %s' %(x_measure,y_measure),fontsize=20)
	plt.xlabel(x_measure,fontsize=18)
	plt.ylabel(y_measure,fontsize=18)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)

	# remove top and right spines from plot
	p.axes.spines["top"].set_visible(False)
	p.axes.spines["right"].set_visible(False)

	# save image or show image
	saveOrShowImg(dir_out,x_measure,y_measure,img_name)

# uses seaborn's scatter function to plot data from x_data[x_measure] and y_data[y_measure] for network correlations. useful for publication worthy figure
# column measure is the measure within which data will be summarized.
# ravelAverageAppend is a string value of either 'append' to use the append function, 'ravel' to use the ravel function, or 'average' to use the average function
# trendline, depending on user input, can either be the linear regression between x_data[x_measure] and y_data[y_measure] or the line of equality
# dir_out and img_name are the directory where the figures should be saved and the name for the image. will save .eps and .png
# if want to view plot instead of save, set dir_out=""
def networkScatter(colors_dict,hues,groups,subjects,x_data,y_data,network_measure,shuffleData,trendline,dir_out,img_name):

	import os,sys
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	from sklearn.metrics import mean_squared_error
			
	# generate new figure for each
	p = plt.figure()

	# grab data
	[x_stat,y_stat,X,Y] = setupData(x_data,y_data,"","","ravel",True,"")

	# additional network setup
	# hues = sns.color_palette(colormap,len(X))
	# hues = hues.as_hex()
	# keys = [ i for i in range(len(X)) ]
	# colors_dict = dict(zip(hues,hues))
	
	if shuffleData == True:
		X,Y,hues = shuffleDataAlg(X,Y,hues)
	
	# if colors_dict:
		# p = sns.scatterplot(x=X,y=Y,hue=hues,s=100,palette=colors_dict,legend=False)
	# else:
	p = sns.scatterplot(x=X,y=Y,hue=hues,s=100,palette=colors_dict,legend=False)

	# set x and ylimits, plot line of equality, and legend
	p.axes.axis('square')
	y_ticks = p.axes.get_yticks()
	p.axes.set_xticks(y_ticks)
	p.axes.set_yticks(p.axes.get_xticks())
	p.axes.set_ylim(p.axes.get_xlim())
	p.axes.set_xlim(p.axes.get_xlim())

	x_lim,y_lim = [p.axes.get_xlim(),p.axes.get_ylim()]

	# trendline: either equality or linear regression
	if trendline == 'equality':
		p.plot(x_lim,y_lim,ls="--",c='k')
	elif trendline == 'linreg':
		m,b = np.polyfit(X,Y,1)
		p.plot(p.get_xticks(),m*p.get_xticks() + b,c='k')
		plt.text(0.1,0.7,'y = %s x + %s' %(str(np.round(m,4)),str(np.round(b,4))),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# compute correlation for each subject and add to plots
	corr = np.corrcoef(X,Y)[1][0]
	plt.text(0.1,0.9,'r = %s' %str(np.round(corr,4)),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# compute rmse for each subject and add to plots
	rmse = np.sqrt(mean_squared_error(X,Y))
	plt.text(0.1,0.8,'rmse = %s' %str(np.round(rmse,4)),fontsize=16,verticalalignment="top",horizontalalignment="left",transform=p.axes.transAxes)

	# set title and x and y labels
	plt.title('%s %s vs %s' %(network_measure,groups[0],groups[1]),fontsize=20)
	plt.xlabel(groups[0],fontsize=18)
	plt.ylabel(groups[1],fontsize=18)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)

	# remove top and right spines from plot
	p.axes.spines["top"].set_visible(False)
	p.axes.spines["right"].set_visible(False)

	# save image or show image
	saveOrShowImg(dir_out,network_measure+'_'+groups[0],network_measure+'_'+groups[1],img_name)

# uses matplotlib.pyplot's hist2d function to plot data from x_data[x_measure] and y_data[y_measure]. useful for supplementary figure or debugging or publication worthy figure
# column measure is the measure within which data will be summarized. hue_measure is the column to use for coloring the data. 
# ravelAverageAppend is a string value of either 'append' to use the append function, 'ravel' to use the ravel function, or 'average' to use the average function
# trendline, depending on user input, can either be the linear regression between x_data[x_measure] and y_data[y_measure] or the line of equality
# dir_out and img_name are the directory where the figures should be saved and the name for the image. will save .eps and .png
# if want to view plot instead of save, set dir_out=""
def plot2dHist(x_data,y_data,x_measure,y_measure,column_measure,hue_measure,ravelAverageAppend,trendline,shuffleData,dir_out,img_name):
	
	import os,sys
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	from sklearn.metrics import mean_squared_error

	# grab data
	[x_stat,y_stat,X,Y] = setupData(x_data,y_data,x_measure,y_measure,ravelAverageAppend,False,column_measure)

	if ravelAverageAppend == 'average':
		if isinstance(x_stat[hue_measure].unique()[0],str):
			hues = x_stat[hue_measure].unique().tolist()
		else:
			hues = x_stat.groupby(column_measure).mean()[hue_measure].tolist()
	else:
		hues = list(x_stat[hue_measure])

	if shuffleData == True:
		X,Y,hues = shuffleDataAlg(X,Y,hues)
		

	# generate new figure for each
	p = plt.figure()

	plt.hist2d(x=X,y=Y,cmin=1,density=False,bins=(len(X)/10),cmap='magma',vmax=(len(X)/10))
	plt.colorbar()			

	# set title and x and y labels
	
	plt.title('%s vs %s' %(x_measure,y_measure),fontsize=20)
	plt.xlabel(x_measure,fontsize=18)
	plt.ylabel(y_measure,fontsize=18)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)

	# # remove top and right spines from plot
	# p.axes.spines["top"].set_visible(False)
	# p.axes.spines["right"].set_visible(False)

	# save image or show image
	saveOrShowImg(dir_out,x_measure,y_measure,img_name)

### tract profile data
# uses matplotlib.pyplot's plot and fill_between functions to plot tract profile data from stat. useful for publication worthy figure
# requires stat to be formatted in way of AFQ_Brwoser and Yeatman et al 2018 () 'nodes.csv' files
# groups is a list array of names of groups found in 'classID' of stat to plot
# colors is a dictionary with the classID from groups set as the key and a color name as the value. will use these colors in profiles
# tracks is a list array that will be looped through to make plots. if only one track is wanted, set structures=['structure_name'], with 'structure_name' being the name of the track in the 'structureID' field of stat
# stat is the pandas dataframe with all of the profile data. each row is a node for a track for a subject
# diffusion_measures is a list array of the column measures found within stat. was developed with diffusion MRI metrics in mind, but can be any measure
# summary_method is a string of either 'mean' to plot the average profile data, 'max' to plot max, 'min' to plot min, and 'median' to plot median
# error_method is a string of either 'std' for the error bars to be set to the standard deviation or 'sem' for standard error of mean
# dir_out and imgName are the directory where the figures should be saved and the name for the image. will save .pdf and .png
# if want to view plot instead of save, set dir_out=""
def plotProfiles(groups,colors,structures,stat,diffusion_measures,summary_method,error_method,dir_out,imgName):

	import matplotlib.pyplot as plt
	import os,sys
	import seaborn as sns
	from scipy import stats
	import numpy as np

	# loop through all structures
	for t in structures:
		print(t)
		# loop through all measures
		for dm in diffusion_measures:
			print(dm)
			# set up output names
			img_out=str('profiles_'+t+'_'+dm+'_'+summary_method+'_'+error_method+'_'+imgName+'.pdf').replace(' ','_')
			img_out_png=str('profiles_'+t+'_'+dm+'_'+summary_method+'_'+error_method+'_'+imgName+'.png').replace(' ','_')

			# generate figures
			fig = plt.figure(figsize=(15,15))
			fig.patch.set_visible(False)
			p = plt.subplot()

			# set title and catch array for legend handle
			plt.title("%s Profiles %s: %s" %(summary_method,t,dm),fontsize=20)

			# loop through groups and plot profile data
			for g in range(len(groups)):
				# x is nodes
				x = stat['nodeID'].unique()

				# y is summary (mean, median, max, main) profile data
				if summary_method == 'mean':
					y = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).mean()[dm][t]
				elif summary_method == 'median':
					y = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).median()[dm][t]
				elif summary_method == 'max':
					y = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).max()[dm][t]
				elif summary_method == 'min':
					y = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).min()[dm][t]

				# error bar is either: standard error of mean (sem), standard deviation (std)
				if error_method == 'sem':
					err = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).std()[dm][t] / np.sqrt(len(stat[stat['classID'] == groups[g]]['subjectID'].unique()))
				else:
					err = stat[stat['classID'] == groups[g]].groupby(['structureID','nodeID']).std()[dm][t]

				# plot summary
				plt.plot(x,y,color=colors[groups[g]],linewidth=5,label=groups[g])

				# plot shaded error
				plt.fill_between(x,y-err,y+err,alpha=0.2,color=colors[groups[g]],label='1 %s %s' %(error_method,groups[g]))

			# set up labels and ticks
			plt.xlabel('Location',fontsize=18)
			plt.ylabel(dm,fontsize=18)
			plt.xticks([x[0],x[-1]],['Begin','End'],fontsize=16)
			plt.legend(fontsize=16)
			y_lim = plt.ylim()
			plt.yticks([np.round(y_lim[0],2),np.mean(y_lim),np.round(y_lim[1],2)],fontsize=16)
			
			# remove top and right spines from plot
			p.axes.spines["top"].set_visible(False)
			p.axes.spines["right"].set_visible(False)

			# save or show plot
			if dir_out:
				if not os.path.exists(dir_out):
					os.mkdir(dir_out)

				plt.savefig(os.path.join(dir_out, img_out))
				plt.savefig(os.path.join(dir_out, img_out_png))       
			else:
				plt.show()

			plt.close(fig)

### generic data plots
## structure average
# uses matplotlib.pyplot's errobar function to plot group average data for each structure with errorbars. useful for publication worthy figure
# requires stat to be formatted in similar way of AFQ_Brwoser and Yeatman et al 2018 () 'nodes.csv' files
# groups is a list array of names of groups found in 'classID' of stat to plot
# colors is a dictionary with the classID from groups set as the key and a color name as the value. will use these colors in profiles
# tracks is a list array that will be looped through to make plots. if only one track is wanted, set structures=['structure_name'], with 'structure_name' being the name of the structure in the 'structureID' field of stat
# stat is the pandas dataframe with all of the profile data. each row is a node for a track for a subject
# diffusion_measures is a list array of the column measures found within stat. was developed with diffusion MRI metrics in mind, but can be any measure
# summary_method is a string of either 'mean' to plot the average profile data, 'max' to plot max, 'min' to plot min, and 'median' to plot median
# error_method is a string of either 'std' for the error bars to be set to the standard deviation or 'sem' for standard error of mean
# dir_out and imgName are the directory where the figures should be saved and the name for the image. will save .pdf and .png
# if want to view plot instead of save, set dir_out=""
def plotGroupStructureAverage(groups,colors,structures,stat,diffusion_measures,summary_method,error_method,dir_out,save_name):

	import os,sys
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	from scipy import stats

	for dm in diffusion_measures:
		print(dm)
		# set up output names
		img_out=str('group_'+save_name+'_'+dm+'_'+summary_method+'_'+error_method+'.pdf').replace(' ','_')
		img_out_png=str('group_'+save_name+'_'+dm+'_'+summary_method+'_'+error_method+'.png').replace(' ','_')

		# generate figures
		fig = plt.figure(figsize=(15,15))
		fig.patch.set_visible(False)
		p = plt.subplot()

		# set y range
		p.set_ylim([0,(len(structures)*len(groups))+len(groups)])

		# set spines and ticks, and labels
		p.yaxis.set_ticks_position('left')
		p.xaxis.set_ticks_position('bottom')
		p.set_xlabel(dm,fontsize=18)
		p.set_ylabel("Structures",fontsize=18)
		if len(groups) < 3:
			if len(groups) == 2:
				p.set_yticks(np.arange(1.5,(len(structures)*len(groups)),step=len(groups)))
			else:
				p.set_yticks(np.arange(1,len(structures)+1,step=1))
		else:
			p.set_yticks(np.arange((len(groups)-1),(len(structures)*len(groups)),step=len(groups)))
		p.set_yticklabels(structures,fontsize=16)
		plt.xticks(fontsize=16)

		# set title
		plt.title("%s Group-Summary: %s" %(summary_method,dm),fontsize=20)

		# loop through structures
		for t in range(len(structures)):
			# loop through groups
			for g in range(len(groups)):
				# x is summary (mean, median, max, main) profile data
				if summary_method == 'mean':
					x = stat[stat['classID'] == groups[g]].groupby('structureID').mean()[dm][structures[t]]
				elif summary_method == 'median':
					x = stat[stat['classID'] == groups[g]].groupby('structureID').median()[dm][structures[t]]
				elif summary_method == 'max':
					x = stat[stat['classID'] == groups[g]].groupby('structureID').max()[dm][structures[t]]
				elif summary_method == 'min':
					x = stat[stat['classID'] == groups[g]].groupby('structureID').min()[dm][structures[t]]

				# y is location on y axis
				y = (len(groups)*(t+1)-len(groups))+(g+1)
				
				# error bar is either: standard error of mean (sem), standard deviation (std)
				if error_method == 'sem':
					err = stat[stat['classID'] == groups[g]].groupby('structureID').std()[dm][structures[t]] / np.sqrt(len(stat[stat['classID'] == groups[g]]['subjectID'].unique()))
				else:
					err = stat[stat['classID'] == groups[g]].groupby('structureID').std()[dm][structures[t]]

				# plot data
				if t == 0:
					p.errorbar(x=x,y=y,xerr=err,barsabove=True,ecolor='black',color=colors[groups[g]],marker='o',ms=10,label=groups[g])
				else:
					p.errorbar(x=x,y=y,xerr=err,barsabove=True,ecolor='black',color=colors[groups[g]],marker='o',ms=10)

		# add legend
		plt.legend(fontsize=16)

		# remove top and right spines from plot
		p.axes.spines["top"].set_visible(False)
		p.axes.spines["right"].set_visible(False)

		# save or show plot
		if dir_out:
			if not os.path.exists(dir_out):
				os.mkdir(dir_out)

			plt.savefig(os.path.join(dir_out, img_out))
			plt.savefig(os.path.join(dir_out, img_out_png))       
		else:
			plt.show()

## plotting snr data from dipy's snr app
def plotSNR(all_stat,all_sub,colors,dir_out):
	
	import matplotlib.pyplot as plt
	import os,sys
	import numpy as np
	from matplotlib import colors as mcolors

	# generate figures
	fig = plt.figure(figsize=(10,10))
	p = plt.subplot()

	# set up output names
	img_out='snr.eps'
	img_out_png='snr.png'

	all_sub.append("")
	all_sub.reverse()
	all_stat.reverse()
	colors.reverse()

	xmin = 0
	xmax = 80
	p.set_xlim([xmin, xmax])
	ymin = 1
	ymax = len(all_sub)
	p.set_xlim([xmin, xmax])
	p.set_ylim([ymin, ymax])
	p.spines['right'].set_visible(False)
	p.spines['top'].set_visible(False)
	p.spines['left'].set_position(('axes', -0.05))
	p.spines['bottom'].set_position(('axes', -0.05))
	p.yaxis.set_ticks(np.arange(len(all_sub)))
	p.yaxis.set_ticks_position('left')
	p.xaxis.set_ticks_position('bottom')
	p.set_yticklabels(all_sub)

	plt.title("SNR of diffusion signal")
	for s in range(len(all_stat)):
	    stat = all_stat[s]
	    color = colors[s]

	    p.errorbar(stat[1:].mean(), s+1, xerr=stat[1:].std(), marker='o', linestyle='None', color=color)
	    p.plot(stat[0], s+1, marker='x', color=color)
	
	# save or show plot
	if dir_out:
		plt.savefig(os.path.join(dir_out, img_out))
		plt.savefig(os.path.join(dir_out, img_out_png))       
	else:
		plt.show()

	plt.close(fig)

### Difference and bootstrapping histograms
def plotDifferenceHistograms(groups,subjects,stat,diffusion_measures,colors,dir_out):
	import matplotlib.pyplot as plt
	import os,sys
	import seaborn as sns
	from itertools import combinations
	import pandas as pd


	img_out = "track_difference_histograms.eps"
	img_out_png = "track_difference_histograms.png"

	f, axes = plt.subplots(2, 4, figsize=(15, 15), sharex=True, sharey=True)
	f.suptitle("Average Difference - Tracts")

	comparison_array = list(combinations(groups,2))

	for dm in range(len(diffusion_measures)):
		if diffusion_measures[dm] in ['ad','fa','md','rd']:
			row = 1
			column = dm
		else:
			row = 0
			column = dm - 4

		#plt.xlim([-0.1,0.1])
		# set spines and ticks
		axes[row,column].spines['right'].set_visible(False)
		axes[row,column].spines['top'].set_visible(False)
		axes[row,column].yaxis.set_ticks_position('left')
		axes[row,column].xaxis.set_ticks_position('bottom')

		axes[row,column].patch.set_visible(False)

		axes[row,column].yaxis.set_ticks_position('left')
		axes[row,column].xaxis.set_ticks_position('bottom')
		
		comparison = {}
		g=0
		for compar in comparison_array:
			comparison[compar[0]+"_"+compar[1]] = pd.DataFrame([])
			comparison[compar[0]+"_"+compar[1]] = comparison[compar[0]+"_"+compar[1]].append(stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[0]])].groupby('structureID').mean() - stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[1]])].groupby('structureID').mean(),ignore_index=True)
			if g == 1:
				Colors = colors[compar[1]]
			else:
				Colors = colors[compar[0]]
			
			sns.distplot(comparison[compar[0]+"_"+compar[1]],kde=False,hist=True,color=Colors,bins=20,ax=axes[row,column],axlabel=diffusion_measures[dm],label="mean: %.3f" %np.mean(comparison[compar[0]+"_"+compar[1]]))
			g=g+1
		
		axes[row,column].axvline(x=0, color='black', linestyle='--', linewidth=3)
		axes[row,column].legend()
	
	# save or show plot
	if dir_out:
		if not os.path.exists(dir_out):
			os.mkdir(dir_out)

		plt.savefig(os.path.join(dir_out, img_out))
		plt.savefig(os.path.join(dir_out, img_out_png))       
	else:
		plt.show()

def plotBootstrappedDifference(groups,subjects,stat,diffusion_measures,colors,repetitions,alpha,dir_out,data_dir):
	import matplotlib.pyplot as plt
	import os,sys
	import seaborn as sns
	import pandas as pd
	import numpy as np
	from itertools import combinations

	# if not os.path.exists(data_dir):
	# 	os.mkdir(data_dir)
	
	img_out = "track_difference_bootstrap_histograms.eps"
	img_out_png = "track_difference_bootstrap_histograms.png"

	f, axes = plt.subplots(2, 4, figsize=(15, 15), sharex=True, sharey=True)
	f.suptitle("Average Bootrap Difference - Tracts")

	resample = {}
	for g in groups:
		resample[g] = {}
		for i in range(repetitions):
			resample[g][i] = list(pd.Series(subjects[g]).sample(len(subjects[g]),replace=True))

	comparison_array = list(combinations(groups,2))

	for dm in range(len(diffusion_measures)):
		if diffusion_measures[dm] in ['ad','fa','md','rd']:
			row = 1
			column = dm
		else:
			row = 0
			column = dm - 4

		# set spines and ticks
		axes[row,column].spines['right'].set_visible(False)
		axes[row,column].spines['top'].set_visible(False)
		axes[row,column].yaxis.set_ticks_position('left')
		axes[row,column].xaxis.set_ticks_position('bottom')

		axes[row,column].patch.set_visible(False)

		comparison = {}
		cli = {}
		g=0
		for compar in comparison_array:
			comparison[compar[0]+"_"+compar[1]] = pd.DataFrame([])
			cli[compar[0]+"_"+compar[1]] = {}
			for i in range(repetitions):
				comparison[compar[0]+"_"+compar[1]] = comparison[compar[0]+"_"+compar[1]].append(np.mean(stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(resample[compar[0]][i])].groupby('structureID').mean()) - np.mean(stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(resample[compar[1]][i])].groupby('structureID').mean()),ignore_index=True)
			comparison[compar[0]+"_"+compar[1]] = comparison[compar[0]+"_"+compar[1]].sort_values(by=diffusion_measures[dm])
			#comparison[compar[0]+"_"+compar[1]].to_csv(os.path.join(data_dir,'track_boostrap_difference_data_'+compar[0]+"_"+compar[1]+"_"+diffusion_measures[dm]+".csv"),index=False)
			cli[compar[0]+"_"+compar[1]] = [np.percentile(comparison[compar[0]+"_"+compar[1]],alpha/2*100),np.percentile(comparison[compar[0]+"_"+compar[1]],100-alpha/2*100),]
			if g == 1:
				Colors = colors[compar[1]]
			else:
				Colors = colors[compar[0]]
			
			sns.distplot(comparison[compar[0]+"_"+compar[1]],kde=False,hist=True,color=Colors,bins=20,ax=axes[row,column],axlabel=diffusion_measures[dm],label="mean: %.3f; cli: %.3f %.3f" %(np.mean(comparison[compar[0]+"_"+compar[1]]),cli[compar[0]+"_"+compar[1]][0],cli[compar[0]+"_"+compar[1]][1]))
			axes[row,column].axvline(cli[compar[0]+"_"+compar[1]][0],color=Colors,linestyle='--',linewidth=3)
			axes[row,column].axvline(cli[compar[0]+"_"+compar[1]][1],color=Colors,linestyle='--',linewidth=3)
			g=g+1

		axes[row,column].legend()


	# save or show plot
	if dir_out:
		if not os.path.exists(dir_out):
			os.mkdir(dir_out)

		plt.savefig(os.path.join(dir_out, img_out))
		plt.savefig(os.path.join(dir_out, img_out_png))       
	else:
		plt.show()

def plotBootstrappedH0TrackAverageDifference(groups,subjects,stat,diffusion_measures,colors,repetitions,dir_out):
	import matplotlib.pyplot as plt
	import os,sys
	import seaborn as sns
	import pandas as pd
	import numpy as np
	from itertools import combinations

	img_out = "track_h0_bootstrap_histograms.eps"
	img_out_png = "track_h0_bootstrap_histograms.png"

	f, axes = plt.subplots(2, 4, figsize=(15, 15), sharex=True, sharey=True)
	f.suptitle("Average Bootstrap (H0) Difference - Tracts")

	comparison_array = list(combinations(groups,2)) # 3 x 2 array; 3 different comparisons, with two pairs per comparison. comparison_array[0] = ("football","cross_country")

	for dm in range(len(diffusion_measures)): # loop through all diffusion measures
		if diffusion_measures[dm] in ['ad','fa','md','rd']:
			row = 1
			column = dm
		else:
			row = 0
			column = dm - 4

		# set spines and ticks for plot
		axes[row,column].spines['right'].set_visible(False)
		axes[row,column].spines['top'].set_visible(False)
		axes[row,column].yaxis.set_ticks_position('left')
		axes[row,column].xaxis.set_ticks_position('bottom')

		axes[row,column].patch.set_visible(False)

		# set up empty data structures
		comparison = {} # for pooled track averages (H0)
		g_diff = {} # H0 group differences array 
		p_value = {} # pvalue array
		g=0 # groups counter to help pick colors so i don't have to range(len()) the comparison array
		for compar in comparison_array:
			# data structure set up
			comparison[compar[0]+"_"+compar[1]] = pd.DataFrame([]) # set up dataframe for each comparison
			comparison[compar[0]+"_"+compar[1]] = pd.concat([stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[0]])].groupby('structureID').mean(),stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[1]])].groupby('structureID').mean()],ignore_index=True) # pooled group average track data
			g_diff[compar[0]+"_"+compar[1]] = [] # set up dataframe for each comparison
			p_value[compar[0]+"_"+compar[1]] = [] # set up dataframe for each comparison
			
			# bootstrapping
			for i in range(repetitions): # loop through repetitions
				g_diff[compar[0]+"_"+compar[1]].append(np.mean(np.random.choice(list(comparison[compar[0]+"_"+compar[1]][diffusion_measures[dm]]),int(len(comparison[compar[0]+"_"+compar[1]][diffusion_measures[dm]])/2),replace=True)) \
					- np.mean(np.random.choice(list(comparison[compar[0]+"_"+compar[1]][diffusion_measures[dm]]),int(len(comparison[compar[0]+"_"+compar[1]][diffusion_measures[dm]])/2),replace=True))) # randomly select from pooled dataframe, and compute difference
			actual_difference = np.mean(stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[0]])].groupby('structureID').mean()[diffusion_measures[dm]]) - np.mean(stat[['structureID',diffusion_measures[dm]]][stat['subjectID'].isin(subjects[compar[1]])].groupby('structureID').mean()[diffusion_measures[dm]]) # calculate actual difference between groups
			
			# calculate p-value
			p_value[compar[0]+"_"+compar[1]] = sum(np.abs(g_diff[compar[0]+"_"+compar[1]]) >= np.abs(actual_difference)) / repetitions # compute p-value
			
			# finish plotting data
			if g == 1:
				Colors = colors[compar[1]]
			else:
				Colors = colors[compar[0]]
			
			sns.distplot(g_diff[compar[0]+"_"+compar[1]],kde=False,hist=True,color=Colors,bins=20,ax=axes[row,column],axlabel=diffusion_measures[dm],label="p_value: %.6f" %p_value[compar[0]+"_"+compar[1]])
			axes[row,column].axvline(actual_difference,color=Colors,linestyle='--',linewidth=3)
			g=g+1

		# print out legend to finish plot for diffusion measures dm
		axes[row,column].legend()

	# save or show plot
	if dir_out:
		if not os.path.exists(dir_out):
			os.mkdir(dir_out)

		plt.savefig(os.path.join(dir_out, img_out))
		plt.savefig(os.path.join(dir_out, img_out_png))       
	else:
		plt.show()
