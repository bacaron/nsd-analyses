#!/bin/bash

topDir=$1
projectID="5e2b98fbe51f7a9aeb88c43c"
datatypes="dwi mask tractmeasures networks snr parc_stats_cortex parc_stats_hcp vm-networks"
tags="run_1 run_2"

for DTYPES in ${datatypes}
do
	for TAGS in ${tags}
	do
		echo "${DTYPES} ${TAGS}"
		if [ ! -f data_${DTYPES}_${TAGS}.json ]; then
			if [[ ${DTYPES} == 'mask' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/${DTYPES} --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'dwi' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/${DTYPES} --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tractmeasures' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/${DTYPES} --datatype_tag "macro_micro" --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'networks' ]]; then
				bl dataset query --project ${projectID} --datatype raw --datatype_tag "networkmatrices" --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'snr' ]]; then
				bl dataset query --project ${projectID} --datatype raw --datatype_tag "snr-cc" --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'parc_stats_cortex' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/parc-stats --datatype_tag "cortex_mapping_stats" --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'parc_stats_hcp' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/parc-stats --datatype_tag "SupraTentorial" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'vm-networks' ]]; then
				bl dataset query --project ${projectID} --datatype raw --datatype_tag "networkmatrices" --tag ${TAGS} --tag "visual_wm" --json > data_${DTYPES}_${TAGS}.json
			fi
		fi
	
		for subject in $(jq -r '.[].meta.subject' data_${DTYPES}_${TAGS}.json | sort -u)
		do
			# make subject directory if not made
			if [ ! -d $topDir/$subject ]; then
				mkdir -p $topDir/$subject
			fi
	
			# make datatype directory if not made
		    if [ ! -d $topDir/$subject/${TAGS}/${DTYPES} ];
		    then
				echo "downloading subject:$subject ---------------"
				mkdir -p $topDir/$subject/${TAGS}/${DTYPES}
				ids=$(jq -r '.[] | select(.meta.subject == '\"$subject\"') | ._id' data_${DTYPES}_${TAGS}.json)
				for id in $ids
				do
				        echo $id
				        outdir=$topDir/$subject/${TAGS}/${DTYPES}
				        bl dataset download -i $id --directory $outdir
				done
		    fi
		done
	done
done
