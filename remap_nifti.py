#/usr/bin/env python3

import numpy as np
import nibabel as nib
from sys import argv
import json

def remap_nifti():
	i_file = str(argv[1])
	o_file = str(argv[2])
	labs_file = str(argv[3])

	i_img = nib.load(i_file)
	i_data = i_img.get_data()

	# load label.json
	with open(labs_file,'r') as labels_json:
		labels = json.load(labels_json)	

	# get labs from first colum of LUT table
	labs = [ f['label'] for f in labels ]  

	# init o_data
	o_data = np.zeros(i_data.shape,dtype=np.int32)
		
	for x in range(0,len(labs)):
		w = np.where(i_data == int(labs[x]))
		o_data[w[0],w[1],w[2]] = (x + 1)

	# save output
	o_img = nib.Nifti1Image(o_data, i_img.get_affine())
	nib.save(o_img, o_file)

if __name__ == '__main__':
	remap_nifti()
