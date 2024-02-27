#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=phys.default.q
#SBATCH --error=~/jobs/slurm-%j.err
#SBATCH --output=~/jobs/slurm-%j.out
#SBATCH --time=54:00:00

# This script is used to set up a simulation directory. It copies the simulation scripts
# to the simulation directory specified as the first argument. It furthermore generates
# a new configuration file for the simulation and copies it to the simulation directory.

conda activate dynhet

DIR=$1
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

setup () {
    mkdir -p $DIR/simulation
    
    # Copy the simulation scripts to the simulation directory
    cp -r $parent_path/../simulation/* $DIR/simulation
    cp $parent_path/run.sh $DIR
    
    # Generate a new configuration file for the simulation, forwards the arguments to the
    # generate_config.py script
    shift 1
    python $parent_path/gen_config.py $@ > $DIR/config.toml
}

run () {
    pushd $DIR
    ./run.sh
    popd
}

setup $@
run
