#!/bin/bash

topPath=$1
subjectID=$2
projectID="5e2b98fbe51f7a9aeb88c43c"
hemispheres="lh rh"

module unload perl nodejs
module load freesurfer hpss

function bl {
	singularity run docker://brainlife/cli $@
}

outpath=${topPath}/${subjectID}/"parcellation-glasser-nsd-provided"
if [ ! -d ${outpath} ]; then
	mkdir -p ${outpath} ${outpath}/tmp
fi

# download freesurfer
if [ ! -d ${topPath}/${subjectID}/freesurfer ]; then
        module unload nodejs
        echo "downloading freesurfer: ${subjectID}"

        bl dataset query --project ${projectID} --datatype neuro/freesurfer --tag "nsd_provided" --json > ${topPath}/${subjectID}/${subjectID}_freesurfer.json

        id=$(jq -r '.[] | select(.meta.subject == '\"${subjectID}\"') | ._id' $topPath/${subjectID}/${subjectID}_freesurfer.json)
        echo ${id}
	
	mkdir -p ${topPath}/${subjectID}/freesurfer/
        bl dataset download -i ${id} -d $topPath/${subjectID}/freesurfer/
        module load nodejs
else
        echo "freesurfer already there. skipping"
fi

# loop through hemispheres
for hemi in ${hemispheres}
do
	echo "${hemi}"

	# convert glasser parc.mgz to .func.gii
	if [ -f ${outpath}/tmp/${hemi}.parc.func.gii ]; then
		echo "file exists. assuming stopped in middle. deleting and remaking"
		rm -rf ${outpath}/tmp/${hemi}.parc.func.gii
	fi

	echo "converting .mgz to .func.gii"
	mris_convert -f ${topPath}/${subjectID}/freesurfer/output/label/${hemi}.HCP_MMP1.mgz \
		${topPath}/${subjectID}/freesurfer/output/surf/${hemi}.white \
		${outpath}/tmp/${hemi}.parc.func.gii
	echo "converting .mgz to .func.gii complete"


	# add 1 in order to set up labels.json properly. convert to label
	wb_command -metric-math 'x+1' \
		${outpath}/tmp/${hemi}.parc.func.gii \
		-var x ${outpath}/tmp/${hemi}.parc.func.gii

	# convert to label.gii
	wb_command -metric-label-import ${outpath}/tmp/${hemi}.parc.func.gii \
		${topPath}/${hemi}_hcp_lut.txt ${outpath}/${hemi}.parc.label.gii \
		-unlabeled-value 1

	# copy to dumb brainlife standard
	cp ${outpath}/${hemi}.parc.label.gii ${outpath}/${hemi}.parc.annot.gii

	# convert surfaces to dumb brainlife standard
	mris_convert ${topPath}/${subjectID}/freesurfer/output/surf/${hemi}.inflated ${outpath}/${hemi}.parc.inflated.gii 
	mris_convert ${topPath}/${subjectID}/freesurfer/output/surf/${hemi}.white ${outpath}/${hemi}.parc.white.gii 
	mris_convert ${topPath}/${subjectID}/freesurfer/output/surf/${hemi}.pial ${outpath}/${hemi}.parc.pial.gii 

	echo "${run} complete"
done

# copy over label.json file needed for bl datatype
if [ ! -f ${outpath}/label.json ]; then
	cp ${topPath}/label.json ${outpath}/label.json
fi

# upload data to brainlife
module unload nodejs
echo "uploading parcellation surface to brainlife"
bl dataset upload --project ${projectID} \
	--subject ${subjectID} \
	--datatype neuro/parcellation/surface-deprecated \
	--lh_annot ${outpath}/lh.parc.annot.gii \
	--rh_annot ${outpath}/rh.parc.annot.gii \
	--lh_inflated_surf ${outpath}/lh.parc.inflated.gii \
	--rh_inflated_surf ${outpath}/rh.parc.inflated.gii \
	--lh_pial_surf ${outpath}/lh.parc.pial.gii \
	--rh_pial_surf ${outpath}/rh.parc.pial.gii \
	--lh_white_surf ${outpath}/lh.parc.white.gii \
	--rh_white_surf ${outpath}/rh.parc.white.gii \
	--label ${outpath}/label.json \
	--tag "hcp-mmp" \
	--tag "hcp-mmp-b" \
	--tag "nsd-provided"
module load nodejs
######### volume parcellation
if [ ! -f ${outpath}/volume ]; then
	mkdir -p ${outpath}/volume
fi

# convert parcellation to .annot
for hemi in ${hemispheres}
do
	echo "converting to .annot for ${hemi}"
	mris_convert --annot ${outpath}/${hemi}.parc.label.gii ${topPath}/${subjectID}/freesurfer/output/surf/${hemi}.white ${outpath}/volume/${hemi}.hcp_parc.annot
	ln -s ${outpath}/volume/${hemi}.hcp_parc.annot ${topPath}/${subjectID}/freesurfer/output/label/${hemi}.hcp_parc.annot
	echo "converting to .annot for ${hemi} complete"
done

# convert to aparc+aseg
export SUBJECTS_DIR=${topPath}
mri_aparc2aseg --s ${subjectID}/freesurfer/output \
	--annot hcp_parc \
	--volmask \
	--o ${outpath}/volume/hcp_parc.mgz

# convert to nifti
mri_label2vol --seg ${outpath}/volume/hcp_parc.mgz \
	--temp ${topPath}/${subjectID}/freesurfer/output/mri/rawavg.mgz \
	--o ${outpath}/volume/parc_tmp.nii.gz \
	--regheader ${outpath}/volume/hcp_parc.mgz

# extract only cortex
mri_binarize --i ${outpath}/volume/parc_tmp.nii.gz \
	--min 1001 \
	--o ${outpath}/volume/tmp_mask1.nii.gz

mri_binarize --i ${outpath}/volume/parc_tmp.nii.gz \
	--min 2182 --inv \
	--o ${outpath}/volume/tmp_mask2.nii.gz

# create mask of overlap
mri_mask ${outpath}/volume/tmp_mask1.nii.gz \
	${outpath}/volume/tmp_mask2.nii.gz \
	${outpath}/volume/tmp_mask3.nii.gz

# mask out cortex
mri_mask ${outpath}/volume/parc_tmp.nii.gz \
	${outpath}/volume/tmp_mask3.nii.gz \
	${outpath}/volume/parc_tmp_cortex.nii.gz

# remap labels to start 1-(n-labels)
python3_conda ${topPath}/remap_nifti.py \
	${outpath}/volume/parc_tmp_cortex.nii.gz \
	${outpath}/volume/parc.nii.gz \
	${outpath}/label.json

# copy key.txt
cp ${topPath}/key.txt ${outpath}/volume/

# upload to brainlife
module unload nodejs
echo "uploading parcellation surface to brainlife"
bl dataset upload --project ${projectID} \
	--subject ${subjectID} \
	--datatype neuro/parcellation/volume \
	--datatype neuro/parcellation/volume \
	--parc ${outpath}/volume/parc.nii.gz \
	--key ${outpath}/volume/key.txt \
	--label ${outpath}/label.json \
	--tag "hcp-mmp" \
	--tag "hcp-mmp-b" \
	--tag "nsd-provided"
module load nodejs

## archive updated data
#module load nodejs
#archive ${topPath}/${subjectID}
