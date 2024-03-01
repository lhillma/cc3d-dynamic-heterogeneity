# cc3d-dynamic-heterogeneity

## Installation
The following steps assume that you have already installed
[Miniconda](https://docs.anaconda.com/free/miniconda/index.html#quick-command-line-install)
and [CompuCell3D](http://www.compucell3d.org/SrcBin) in a conda environment
called `cc3d`.

Clone the repository:
```bash
git clone --recursive https://github.com/lhillma/cc3d-dynamic-heterogeneity.git
```

Install the requirements
```bash
conda activate cc3d

pip install -r requirements.txt
```

## Running the example

Invoke the example run script:
```bash
./example_run.sh
```

If you'd like to change the parameters of the simulation, you can do so by
editing the options in the `config.toml` file at the root of the repository.
