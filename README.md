# Natural Scenes Dataset - Diffusion study

This is the code repository for the paper entitled _XX (link). This repository contains the code responsible for all figures and analyses generated in the paper. Specifically, this repository contains code for downloading the relevant data from brainlife.io, collating the data into relevant .csv files, analyzing the data, and producing figure plots. The code here has been implemented in python3.6.
<!--
#![fig1](./reports/figures/fig1.png)

#![fig2](./reports/figures/fig2.png)
-->

### Authors 

- Brad Caron (bacaron@iu.edu)

### Acknowledgements  

This research was supported by NSF OAC-1916518, NSF IIS-1912270, NSF, IIS-1636893, NSF BCS-1734853, NIH NIDCD 5R21DC013974-02, NIH 1R01EB029272-01, NIH NIMH 5T32MH103213, the Indiana Spinal Cord and Brain Injury Research Fund, Microsoft Faculty Fellowship, the Indiana University Areas of Emergent Research initiative “Learning: Brains, Machines, Children.” We thank Soichi Hayashi, and David Hunt for contributing to the development of brainlife.io, Craig Stewart, Robert Henschel, David Hancock and Jeremy Fischer for support with jetstream-cloud.org (NSF ACI-1445604). We also thank The Indiana University Lawrence D. Rink Center for Sports Medicine and Technology and Center for Elite Athlete Development for contributing funding to athletic scientific research and for the development of a new research facility.

### Data availability

Data used in this project can be found at the accompanying [brainlife.io project](https://brainlife.io/project/5cb8973c71a8630036207a6a).

### Project Directory Organization

For a better understanding of how this code was run locally, here is the local directory structure:

	.
	├── analyzeWmGmData.py
	├── bl_download.sh
	├── configs
	│   ├── config.json
	│   ├── distinct_colors.txt
	│   └── labels.txt
	├── main
	├── README.md
	└── utils
	    ├── analyses.py
	    ├── compile_data.py
	    └── plotting.py
	
	2 directories, 10 files

<!--
<sub> This material is based upon work supported by the National Science Foundation Graduate Research Fellowship under Grant No. 1342962. Any opinion, findings, and conclusions or recommendations expressed in this material are those of the authors(s) and do not necessarily reflect the views of the National Science Foundation. </sub>
-->

### Config.json

Here is a snapshot of the config.json structure:

	{
	    "topPath":  "/path/to/data/nsd",
	    "scriptsPath":  "nsd-analyses",
	    "utilsPath":    "utils",
	    "configsPath":  "configs",
	    "groups":   "run_1 run_2",
	    "colors":   "orange blue",
	    "diffusion_measures":   "ad fa md rd ndi ga ak mk rk isovf odi",
	    "network_measures": "density fa",
	    "number_of_nodes":  180
	}


### Dependencies

This repository requires the following libraries when run locally. 

- npm: https://www.npmjs.com/get-npm
- brainlife CLI: https://brainlife.io/docs/cli/install/
- jsonlab: https://github.com/fangq/jsonlab.git
- python3.6: https://www.python.org/downloads/
- numpy: https://numpy.org/doc/stable/user/install.html
- pandas: https://pandas.pydata.org/
- seaborn: https://seaborn.pydata.org/installing.html
- matplotlib: https://matplotlib.org/faq/installing_faq.html
- scipy: https://www.scipy.org/install.html
- scikit-learn: https://scikit-learn.org/stable/install.html
- statsmodels: https://www.statsmodels.org/stable/install.html
- pinguoin: https://pingouin-stats.org/

### Docker container

A docker container exists containing all of the dependencies necessary for running the analyses in this paper (https://hub.docker.com/r/bacaron/athlete-brain-container). This container can be executed or downloaded via singularity. See the "main" script for examples of how to execute the analyses via singularity.

### To run locally

Before any of the scripts provided are ran, the user must set up two specific paths in the config.json file. 'topPath' is the filepath to the directory in where you want the data to be downloaded and analyses to be ran. This directory will be created by the bl_download.sh script if it does not already exist. 'scriptsPath' is the path to this repository on your local machine. 'configsPath' is the path to the configs directory containing the config.json file. 'utilsPath' is the path to the python utility scripts. The other variables range in necessity. "groups" is necessary, but can be altered to look at only a subset of the group comparisons (run_1, run_2). "colors" is also necessary, but can be altered to be any color name in the matplotlib suite of colors. "diffusion_measures" is also necessary, but can be altered to only include a subset of diffusion measures (DTI: ad, fa, md, rd; NODDI: ndi, isovf, odi). "network_measures" is necessary but can be modified to use any of the network matrices outputs. "number_of_nodes" is the number of nodes desired for the tract profiles. 

To run locally, the user first needs to download the appropriate data using the bl_download.sh shell script. Once the data is downloaded, the user can run via python3 the analyzeGmWmData.py script to generate the summary data structures and figures. This route requires all of the dependencies to be installed on your machine.

If the user has singularity installed, they can run the entire analysis pipeline by running via shell/bash the main script. This will run the scripts for downloading and analyzing the data via singularity using the docker container described above. This route does not require all of the dependencies to be installed on your machine, and will reproduce the analyses exactly as they were ran for the paper.
