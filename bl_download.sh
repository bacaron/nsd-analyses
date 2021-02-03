#!/bin/bash

topDir=$1
projectID="5e2b98fbe51f7a9aeb88c43c"
datatypes="snr-cc noddi-wm noddi-cortex csd tractmeasures-dki tractmeasures-non-dki tractmeasures-or-dki tractmeasures-or-non-dki cortexmap-dki cortexmap-non-dki parc-stats-dki parc-stats-non-dki wmc-wholebrain wmc-wholebrain-clean wmc-optic-radiation wmc-optic-radiation-clean track-lmax6 track-lmax8 track-merged track-optic-radiation tensor-lmax8 tensor-dki parcellation networks-vwm"
tags="run_1 run_2"

for DTYPES in ${datatypes}
do
	for TAGS in ${tags}
	do
		echo "${DTYPES} ${TAGS}"
		if [ ! -f data_${DTYPES}_${TAGS}.json ]; then
			if [[ ${DTYPES} == 'snr-cc' ]]; then
				bl dataset query --project ${projectID} --datatype raw --datatype_tag "snr-cc" --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'noddi-wm' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/noddi --tag ${TAGS} --tag "wm" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'noddi-cortex' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/noddi --tag ${TAGS} --tag "0.0011" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'csd' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/${DTYPES} --tag ${TAGS} --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tractmeasures-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tractmeasures --datatype_tag "macro_micro" --tag ${TAGS} --tag "dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tractmeasures-non-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tractmeasures --datatype_tag "macro_micro" --tag ${TAGS} --tag "non_dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tractmeasures-or-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tractmeasures --datatype_tag "macro_micro" --tag ${TAGS} --tag "optic_radiation" --tag "dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tractmeasures-or-non-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tractmeasures --datatype_tag "macro_micro" --tag ${TAGS} --tag "optic_radiation" --tag "non_dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'cortexmap-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/cortexmap --tag ${TAGS} --tag "dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'cortexmap-non-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/cortexmap --tag ${TAGS} --tag "non_dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'parc-stats-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/parc-stats --tag ${TAGS} --tag "dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'parc-stats-non-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/parc-stats --tag ${TAGS} --tag "non_dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'wmc-wholebrain' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/wmc --tag ${TAGS} --tag "wholebrain" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'wmc-wholebrain-clean' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/wmc --tag ${TAGS} --tag "wholebrain" --datatype_tag "cleaned" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'wmc-optic-radiation' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/wmc --tag ${TAGS} --tag "optic_radiation" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'wmc-optic-radiation-clean' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/wmc --tag ${TAGS} --tag "optic_radiation" --datatype_tag "cleaned" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'track-lmax6' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/track/tck --tag ${TAGS} --tag "lmax6" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'track-lmax8' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/track/tck --tag ${TAGS} --tag "lmax8" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'track-merged' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/track/tck --tag ${TAGS} --datatype_tag "merged" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'track-optic-radiation' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/track/tck --tag ${TAGS} --tag "optic_radiation" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tensor-lmax8' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tensor --tag ${TAGS} --tag "lmax8" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'tensor-dki' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/tensor --tag ${TAGS} --datatype_tag "dki" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'parcellation' ]]; then
				bl dataset query --project ${projectID} --datatype neuro/parcellation/volume --tag ${TAGS} --datatype_tag "visual_areas" --json > data_${DTYPES}_${TAGS}.json
			fi
			if [[ ${DTYPES} == 'networks-vwm' ]]; then
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
				        bl dataset download -i $id -d $outdir
				done
		    fi
		done
	done
done
