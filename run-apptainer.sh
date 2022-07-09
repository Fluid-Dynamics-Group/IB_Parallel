#! /bin/bash

# exit out of the script if a command fails
set -e

image="ib_parallel.sif"

# if there was an argument to this script:
if [[ $# == 1 ]]; then
	# run the container and bind the current directory's 
	# ./output to the image's ./output
	# so that we can output some results
	apptainer run --bind $PWD/output/:/IB_Parallel/output $image "$1"
else
	echo "./run-apptainer.sh only expects one argument: \`default\` or a string to execute in the container"
	exit
fi
