#!/bin/bash

topPath=$1
subjectID=$2
runs="run_1 run_2"
resliced_dirs="dwi dti dki csd noddi-wm noddi-cortex"

module load hpss nodejs

if [ ! -d $topPath/${subjectID} ]; then
	echo "restoring data directory"
	mkdir -p ${topPath}/${subjectID}
	restore $topPath/${subjectID}
	echo "restoring data directory complete"
else
	echo "data already there"
fi

# prune cortexmap directory
for RUNS in ${runs}
do
	echo "cortexmap data"
	echo "${subjectID} ${RUNS}"
	# path to run data
	datapath=${topPath}/${subjectID}/diffusion/${RUNS}/
	
	# make cortexmap directory if not already there
	if [ ! -d ${datapath}/cortexmap/ ]; then
		mkdir -p ${datapath}/cortexmap
	fi
	
	# set path to newly made cortexmap directory
	cortexpath=${datapath}/cortexmap

	# copy data from dki to cortexpath
	rsync -r -c --info=progress2 ${cortexpath}-dki/cortexmap/* ${cortexpath}/

	# make subdirectories in func directory for dti and dki files
	mkdir -p ${cortexpath}/func/dti ${cortexpath}/func/dki

	# move the mapped files from dki currently in cortexpath to func/dki
	mv ${cortexpath}/func/*.func.gii ${cortexpath}/func/dki/

	# copy data from dti to func/dti
	rsync -r -c --info=progress2 ${cortexpath}-dti/cortexmap/func/* ${cortexpath}/func/dti/

	# remove unneccessary ribbon and separated folders
	rm -rf ${cortexpath}/surf/ribbon.nii.gz ${cortexpath}-dki ${cortexpath}-dti
	echo "cortexmap data complete"

	# work on statistics files for cortex map
	echo "cortexmap statistics"
	if [ ! -d ${cortexpath}-statistics/ ]; then
		mkdir -p ${cortexpath}-statistics
	fi
	
	cortexstatspath=${cortexpath}-statistics

	# make directories for dki and dti
	mkdir -p ${cortexstatspath}/dti ${cortexstatspath}/dki

	# copy data
	rsync -r -c --info=progress2 ${cortexstatspath}-dki/* ${cortexstatspath}/dki/
	rsync -r -c --info=progress2 ${cortexstatspath}-dti/* ${cortexstatspath}/dti/

	# remove directories
	rm -rf ${cortexstatspath}-dki ${cortexstatspath}-dti
	echo "cortexmap statistics complete"

	# tract statistics
	echo "tract statistics"
	if [ ! -d ${datapath}/tract-statistics/ ]; then
		mkdir -p ${datapath}/tract-statistics
	fi
	
	tractstatspath=${datapath}/tract-statistics

	# make directories for dti and dki
	mkdir -p ${tractstatspath}/dti ${tractstatspath}/dki

	# copy data
	rsync -r -c --info=progress2 ${tractstatspath}-dki/* ${tractstatspath}/dki/
	rsync -r -c --info=progress2 ${tractstatspath}-dti/* ${tractstatspath}/dti/

	# remove directories
	rm -rf ${tractstatspath}-dki ${tractstatspath}-dti
done

# clean up resliced issues
for RSDIRS in ${resliced_dirs}
do
	echo ${RSDIRS}
	for RUNS in ${runs}
	do
		echo ${RUNS}
		datapath=${topPath}/${subjectID}/diffusion/${RUNS}/${RSDIRS}
		
		# move current directory elsewhere
		mkdir -p ${topPath}/${subjectID}/${RUNS}
		mv ${datapath} ${topPath}/${subjectID}/${RUNS}/${RSDIRS}
		
		rm -rf ${datapath}

		# move resliced data to data path
		mv ${datapath}_resliced ${datapath}
		echo "run complete"
	done
	echo "${RSDIRS} complete"
done

echo "archiving data"
archive $topPath/${subjectID}
echo "archive complete"
