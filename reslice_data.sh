#!/bin/bash

topPath=$1
subjectID=$2
projectID="5e2b98fbe51f7a9aeb88c43c"
runs="run_1 run_2"
convertFolders="dwi dti dki csd noddi-cortex noddi-wm"

# unload and load appropriate modules
module unload perl
module load hpss freesurfer
module load nodejs

if [ ! -d $topPath/${subjectID} ]; then
	echo "restoring data directory"
	mkdir -p ${topPath}/${subjectID}
	restore $topPath/${subjectID}
	echo "restoring data directory complete"
else
	echo "data already there"
fi

if [ ! -f ${topPath}/${subjectID}/t1.nii.gz ]; then
	module unload nodejs
	echo "downloading t1: ${subjectID}"
	
	bl dataset query --project ${projectID} --datatype neuro/anat/t1w --datatype_tag "acpc_aligned" --tag "acpc_aligned" --json > ${topPath}/${subjectID}/${subjectID}_t1.json

	id=$(jq -r '.[] | select(.meta.subject == '\"${subjectID}\"') | ._id' $topPath/${subjectID}/${subjectID}_t1.json)
	echo ${id}

	bl dataset download -i ${id} -d $topPath/${subjectID}/
	module load nodejs
else
	echo "t1 already there. skipping"
fi

for cvfs in ${convertFolders}
do
	echo "reslicing data found in ${cvfs}"
	for RUNS in ${runs}
	do
		echo ${RUNS}
		
		# set paths
		data_path=$topPath/${subjectID}/diffusion/${RUNS}/${cvfs}
		out_path=$topPath/${subjectID}/diffusion/${RUNS}/${cvfs}_resliced
		echo "original data found in ${data_path}"
		echo "outpath for data ${out_path}"

		# make dirs
		if [ -d ${out_path} ]; then
			echo "outpath found. assumed stopped in middle. removing"
			rm -rf ${out_path}
		fi
		
		mkdir -p ${out_path}

		# copy data over
		echo "copying data"
		cp -R -v ${data_path}/* ${out_path}/		
		
		# grab file list to convert
		files=(`find ${out_path}/*.nii.gz`)

		# reslice data		
		for FLS in ${files[*]}
		do
			echo "reslicing ${FLS}"
			mri_vol2vol --mov ${FLS} --targ ${topPath}/${subjectID}/t1.nii.gz --regheader --interp nearest --o ${FLS}
			echo "reslicing ${FLS} complete"
		done
	done
done

echo "archiving data"
archive $topPath/${subjectID}
echo "archive complete"
