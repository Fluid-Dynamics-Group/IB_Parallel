#! /bin/bash

# exit out of the script if a command fails
set -e

# building base container with all dependencies included
#
function compile_base() {
	base_output="base.sif"
	base_input="base.apptainer"

	rm -f $base_output
	
	sudo -E apptainer build $base_output $base_input
}

#
# building main container
#
function build_ib_parallel() {
	output="ib_parallel.sif"
	input="ib_parallel.apptainer"

	rm -f $output

	sudo -E apptainer build $output $input
}

# if the argument was 'full'
if [[ $1 == "full" ]]
then
	echo "compiling base image"
	compile_base
# if there /was/ an argument, but it was not 'full'
elif [[ $1 != "full" ]] && [[ $# != 0 ]];then
	echo "argument was not 'full', run ./build-apptainer.sh if you only wish to build an image with changes to local code"
	exit
fi


# always bulid the new version of the ib_parallel image
echo "compiling ib_parallel image"
build_ib_parallel
