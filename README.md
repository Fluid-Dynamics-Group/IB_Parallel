# IB_Parallel

This code is used to simulate strongly-coupled fluid-structure interaction problems. It has parallel computing functionality in addition to an efficient fluid-structure coupling strategy. Refer to Nair and Goza JCP 2022 for more details.

## Building

The following dependencies are required:

* mpich
* fftw
* PETSC with
	* fftw 
	* elemental
	* mpich

then, configure `PETSC_ARCH` and `PETSC_DIR` in the makefile. Then:

```
make clean && make ib
```

## Running

The compiled binary is located in `./bin/ib`. Running with 16 mpi processes:

```
mpirun -np 16 ./bin/ib
```

output is stored in `./output`

## Apptainer

If you wish to get up and running quickly, a container solution is available with 
[`apptainer`](https://apptainer.org/) (previously singularity).

First, you will need to perform a full build. The full build compiles a base image `./base.sif` that
contains dependencies that will not change between compilations of `IB_Parallel`. Then, the actual 
compilation of `./ib_parallel.sif` will happen with `./base.sif` as the base image. 

The first time you are building:

```
./build-apptainer.sh full
```

all subsequent compilations can be executed with:

```
./build-apptainer.sh full
```


### Running Apptainer Containers

To run a default case of

```
mpirun -np 2 ./bin/ib -malloc_dump -ksp_monitor_true_residual -ksp_converged_reason
```

simply run:

```
./run-apptainer.sh default
```

If you wish to change this command, you can edit `./ib_parallel.apptainer` and recompile the image. To avoid recompiling the entire
`IB_Parallel` project, you can instead pass a user-defined command. For example, we can print "1234" from inside the container
with:

```
./run-apptainer.sh "echo 1234"
```

which outputs:

```
running user-defined string: 'echo 1234'
1234
```

The enclosing "" quotes around `1234` are important. Applying this methodology to the solver, you can adjust the number of processes
for the default case with:

```
./run-apptainer.sh \
	"mpirun -np 16 ./bin/ib -malloc_dump -ksp_monitor_true_residual -ksp_converged_reason"
```
