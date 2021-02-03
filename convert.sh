#!/bin/bash

topPath=$1
movePath=${topPath}/bids-data/
subjects=`ls -d ${topPath}/*subj0*`
tags="run_1 run_2"

#for subj in ${subjects}
#do
#	# for TAGS in ${tags}
#	# do
#		echo ${subj}/run_1
#		# mv ${subj}/${TAGS}/dwi ${movePath}/${subj#${topPath}/}/diffusion/${TAGS}/
#		# mkdir ${movePath}/${subj#${topPath}/}/diffusion/${TAGS}/brainmask/
#		# cp ${subj}/mask_final.nii.gz ${movePath}/${subj#${topPath}/}/diffusion/${TAGS}/brainmask/
#		mv ${movePath}/${subj#${topPath}/}/diffusion/run_1/brainmask ${movePath}/${subj#${topPath}/}/diffusion/ && rm -rf ${movePath}/${subj#${topPath}/}/diffusion/run_2/brainmask/	# done
#done



for subj in ${subjects}
do
	diff_path=${subj}"/diffusion"
	if [ ! -d ${diff_path} ]; then
		mkdir ${diff_path}
	fi
	for TAGS in ${tags}
	do
		mv ${subj}"/"${TAGS} ${diff_path}
		tag_path=${diff_path}"/"${TAGS}
		echo ${tag_path}

		# snr
		mkdir ${tag_path}"/snr"
		mv ${tag_path}"/snr-cc/output/snr.json" ${tag_path}"/snr/"
		rm -rf ${tag_path}"/snr-cc"

		# visual area parcellation
		mv ${tag_path}"/parcellation" ${tag_path}"/visual-area-parcellation"
		rm -rf ${tag_path}"/visual-area-parcellation/*info.json"

		# dti
		mv ${tag_path}"/tensor-lmax8" ${tag_path}"/dti"

		# dki
		mv ${tag_path}"/tensor-dki" ${tag_path}"/dki"

		# tractography
		mkdir ${tag_path}"/track"
		mv ${tag_path}"/track-lmax6/track.tck" ${tag_path}"/track/track-lmax6.tck"
		mv ${tag_path}"/track-lmax8/track.tck" ${tag_path}"/track/track-lmax8.tck"
		mv ${tag_path}"/track-merged/track.tck" ${tag_path}"/track/track-merged.tck"
		mv ${tag_path}"/track-optic-radiation/track.tck" ${tag_path}"/track/track-optic-radiation.tck"
		rm -rf ${tag_path}"/track-lmax6" ${tag_path}"/track-lmax8" ${tag_path}"/track-merged" ${tag_path}"/track-optic-radiation"

		# tract segmentation
		mkdir ${tag_path}"/tract-segmentation"
		mv ${tag_path}"/wmc-wholebrain/classification.mat" ${tag_path}"/tract-segmentation/classification-wholebrain.mat"
		mv ${tag_path}"/wmc-wholebrain-clean/classification.mat" ${tag_path}"/tract-segmentation/classification-wholebrain-clean.mat"
		mv ${tag_path}"/wmc-optic-radiation/classification.mat" ${tag_path}"/tract-segmentation/classification-optic-radiation.mat"
		mv ${tag_path}"/wmc-optic-radiation-clean/classification.mat" ${tag_path}"/tract-segmentation/classification-optic-radiation-clean.mat"
		rm -rf ${tag_path}"/wmc-wholebrain" ${tag_path}"/wmc-wholebrain-clean" ${tag_path}"/wmc-optic-radiation" ${tag_path}"/wmc-optic-radiation-clean"

		# visual area networks
		mv ${tag_path}"/networks-vwm" ${tag_path}"/visual-area-network"

		# cortexmap
		mv ${tag_path}"/cortexmap-non-dki" ${tag_path}"/cortexmap-dti"

		# profiles
		mkdir ${tag_path}"/tract-statistics-dki" ${tag_path}"/tract-statistics-dti"
		mv ${tag_path}"/tractmeasures-dki/output_FiberStats.csv" ${tag_path}"/tract-statistics-dki/output_FiberStats_wholebrain.csv"
		mv ${tag_path}"/tractmeasures-non-dki/output_FiberStats.csv" ${tag_path}"/tract-statistics-dti/output_FiberStats_wholebrain.csv"
		mv ${tag_path}"/tractmeasures-or-dki/output_FiberStats.csv" ${tag_path}"/tract-statistics-dki/output_FiberStats_optic-radiation.csv"
		mv ${tag_path}"/tractmeasures-or-non-dki/output_FiberStats.csv" ${tag_path}"/tract-statistics-dti/output_FiberStats_optic-radiation.csv"
		rm -rf ${tag_path}"/tractmeasures-dki" ${tag_path}"/tractmeasures-non-dki" ${tag_path}"/tractmeasures-or-dki" ${tag_path}"/tractmeasures-or-non-dki"
		# cortexmap stats
		mv ${tag_path}"/parc-stats-dki" ${tag_path}"/cortexmap-statistics-dki"
		mv ${tag_path}"/parc-stats-non-dki" ${tag_path}"/cortexmap-statistics-dti"
	done
done
