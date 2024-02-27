#!/usr/bin/env bash

conda activate dynhet

python -m cc3d.run_script -i simulation/simulation.cc3d -o cc3d_output -f 1000
