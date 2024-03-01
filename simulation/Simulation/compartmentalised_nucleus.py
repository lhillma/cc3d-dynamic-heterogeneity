import toml
from typing import TypedDict, cast

from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.filter import CompartmentFilter, RandomFractionFilter
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams
from cc3dslib.simulation import ConfigBuilder, PottsParams
from cc3dslib.analysis import COMTracker


config = toml.load("config.toml")


sim_params = PottsParams(
    dimensions=(config["sim"]["box_size"], config["sim"]["box_size"], 1),
    steps=config["sim"]["steps"],
    neighborOrder=1,
)

# nucleus
nuc_params = NucleusCompartmentCellParams(
    diameter=config["cell"]["diameter"],
    box=(0, 0, *sim_params.dimensions[:2]),
    nucleus_size_ratio=config["cell"]["nucleus_size_ratio"],
    nuc_lambda_volume=6,
    cyto_lambda_volume=3,
    neighbour_order_volume=16,
    neighbour_order_contact=16,
    neighbour_order_internal=16,
)
nuc_params.contact_energy[("Cytoplasm", "Medium")] = 1.0
nuc_params.contact_energy[("Cytoplasm", "Cytoplasm")] = 1.0
nuc_params.contact_energy[("Nucleus", "Medium")] = 10.0
nuc_params.contact_energy[("Nucleus", "Cytoplasm")] = 10.0
nuc_params.contact_energy[("Nucleus", "Nucleus")] = 100.0
nuc_params.contact_internal[("Cytoplasm", "Nucleus")] = 0.5
nuc_steppable = NucleusCompartmentCell(params=nuc_params)

# active force
cell_filter = CompartmentFilter()


class RandomFilter(RandomFractionFilter):
    """Random filter that saves the indices of the cell clusters to a file.

    The indices are saved to a file when the simulation stops. The file is saved in the
    same directory as the simulation script and is named "indices.txt" by default.
    """

    def __init__(self, *args, path: str = "indices.txt", **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

    def finish(self):
        self.on_stop()

    def on_stop(self):
        import numpy as np

        np.savetxt(self.path, self.indices, fmt="%d")


active_filter = RandomFilter(cell_filter, fraction=config["sim"]["active_fraction"])

active_params = ActiveSwimmerParams(
    filter=active_filter,
    d_theta=0.1,
    force_magnitude=config["cell"]["propensity"],
)
active_steppable = ActiveSwimmer(params=active_params)


def com_filter_fn(cells):
    """This function is used to filter cells for COMTracker.

    It returns a list of lists of cells. For each compartment, the outer list contains a
    list of all the cells within a compartment (cytoplasm and nucleus). Following this,
    there are then two lists, one for the cytoplasm and one for the nucleus, each
    containing a single cell. Thus, for each cell, the result of this function looks as
    follows:

    [[CYTOPLASM, NUCLEUS], [CYTOPLASM], [NUCLEUS]]

    The resulting h5 py tables file will have the following structure:

    (t, 0) -> COM_COMPARTMENT
    (t, 1) -> COM_CYTOPLASM
    (t, 2) -> COM_NUCLEUS
    """
    import itertools

    return itertools.chain(
        *[[cell] + [[c] for c in sorted(cell, key=lambda c: c.type)] for cell in cells]
    )


com_tracker = COMTracker(
    "com.h5",
    cell_filter.transform(com_filter_fn),
    frequency=100,
)


(
    ConfigBuilder()
    .base(n_processors=1, dbg_frequency=1000)
    .potts(sim_params)
    .add(nuc_steppable)
    .add(cell_filter)
    .add(active_filter)
    .add(active_steppable)
    .add(com_tracker)
    .setup()
    .run()
)
