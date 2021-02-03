#!/bin/bash

topPath=$1
subjects=$2
runs="run_1 run_2"
dki_measures="ad ak fa ga goodvertex isovf md mk ndi odi rd rk snr"
dti_measures="ad fa goodvertex isovf md ndi odi rd snr"
hemi="lh rh"

module unload perl
module load freesurfer

for su in ${subjects}
do
	for ru in ${runs}
	do
		echo ${su} ${ru}
		cortexmap_dki_path="${topPath}/${su}/diffusion/${ru}/cortexmap-dki/cortexmap"
		cortexmap_dti_path="${topPath}/${su}/diffusion/${ru}/cortexmap-dti/cortexmap"

		if [ ! -d ${cortexmap_dki_path}/freesurfer ]; then
			mkdir ${cortexmap_dki_path}/func/freesurfer 
		fi
		if [ ! -d ${cortexmap_dti_path}/freesurfer ] ;then
			mkdir ${cortexmap_dti_path}/func/freesurfer
		fi

		for HEMI in ${hemi}
		do
			echo ${HEMI}
			for dkm in ${dki_measures}
			do
				echo ${dkm}
				mris_convert -f ${cortexmap_dki_path}/func/${HEMI}.${dkm}.func.gii ${cortexmap_dki_path}/surf/${HEMI}.midthickness.native.surf.gii ${cortexmap_dki_path}/func/freesurfer/${HEMI}.${dkm}.mgh
			done

			for dtm in ${dti_measures}
			do
				echo ${dtm}
				mris_convert -f ${cortexmap_dti_path}/func/${HEMI}.${dtm}.func.gii ${cortexmap_dti_path}/surf/${HEMI}.midthickness.native.surf.gii ${cortexmap_dti_path}/func/freesurfer/${HEMI}.${dtm}.mgh
			done
		done
	done
done
