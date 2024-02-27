from cc3dslib.nucleus import NucleusCompartmentCell, NucleusCompartmentCellParams
from cc3dslib.filter import CompartmentFilter, RandomFractionFilter
from cc3dslib import ActiveSwimmer, ActiveSwimmerParams
from cc3dslib.simulation import ConfigBuilder, PottsParams

mode = "multi"
contact_internal = 0.5

sim_params = PottsParams(
    dimensions=(200, 200, 1),
    steps=10_000,
    neighborOrder=1,
)

# nucleus
nuc_params = NucleusCompartmentCellParams(
    diameter=40,
    box=(80, 80, 120, 120) if mode == "single" else (0, 0, *sim_params.dimensions[:2]),
    nucleus_size_ratio=0.56,
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
nuc_params.contact_internal[("Cytoplasm", "Nucleus")] = contact_internal
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

    def on_stop(self):
        import numpy as np

        np.savetxt(self.path, self.indices, fmt="%d")


active_filter = RandomFilter(cell_filter, 1.0, path="example/output/ids_motile.txt")

active_params = ActiveSwimmerParams(
    filter=active_filter,
    d_theta=0.1,
    force_magnitude=200.0,
)
active_steppable = ActiveSwimmer(params=active_params)

(
    ConfigBuilder()
    .base(n_processors=1, dbg_frequency=1000)
    .potts(sim_params)
    .add(nuc_steppable)
    .add(cell_filter)
    .add(active_filter)
    .add(active_steppable)
    .setup()
    .run()
)
