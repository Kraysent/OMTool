"""
Task that computes radial distribution of the potential.
"""
from amuse.lab import ScalarQuantity, VectorQuantity, units

from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import AbstractTask, DataType, register_task
from omtool.core.utils import math, particle_centers, pyfalcon_analizer


@register_task(name="PotentialTask")
class PotentialTask(AbstractTask):
    """
    Task that computes radial distribution of the potential. Algorithm: take the center and then
    draw a bunch of concentric sphere slices (number depends on `resolution`). Compute potential
    for each particle of the snapshot. For each slice compute average potential of the particles
    inside.

    Args:
    * `r_unit` (`ScalarQuantity`): unit of the radius for the output.
    * `pot_unit` (`ScalarQuantity`): unit of the potential for the output.
    * `resolution` (`int`): number of slices between nearest and farthest particle to the center.

    Dynamic args:
    * `center` (`VectorQuantity`): position of the center of profile. Center of mass by default.

    Returns:
    * `radii`: list of radii of the sphere slices.
    * `potential`: list of potentials for each slice.
    """

    def __init__(
        self,
        resolution: int = 1000,
        r_unit: ScalarQuantity = 1 | units.kpc,
        pot_unit: ScalarQuantity = None,
    ) -> None:
        super().__init__()
        self.resolution = resolution
        self.r_unit = r_unit
        self.pot_unit = pot_unit

    @profiler("Potential profile task")
    def run(
        self,
        snapshot: Snapshot,
        center: VectorQuantity | None = None,
    ) -> DataType:
        particles = snapshot.particles

        if center is None:
            center = particle_centers.center_of_mass(particles)

        radii = math.get_lengths(particles.position - center)
        potentials = pyfalcon_analizer.get_potentials(snapshot.particles, 0.2 | units.kpc)
        radii, potentials = math.sort_with(radii, potentials)

        number_of_chunks = (len(radii) // self.resolution) * self.resolution

        radii = radii[0 : number_of_chunks : self.resolution]
        potentials = potentials[:number_of_chunks].reshape((-1, self.resolution)).mean(axis=1)

        if self.pot_unit is None:
            self.pot_unit = potentials.mean()

        return {"radii": radii / self.r_unit, "potential": potentials / self.pot_unit}


task = PotentialTask
