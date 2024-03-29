"""
Model sole purpose of which is to read the output of TSF program
from NEMO package.

example of the file:

    tsf galaxy.nemo allline=t xml=t > res.txt
"""

import numpy as np
from amuse.lab import Particles, ScalarQuantity, units
from lxml import etree

from omtool.core.datamodel import Snapshot
from omtool.core.models import AbstractModel, register_model


@register_model(name="tsf")
class TSFModel(AbstractModel):
    def __init__(
        self,
        filename: str,
        dist_unit: ScalarQuantity = 1 | units.kpc,
        vel_unit: ScalarQuantity = 1 | units.kms,
        mass_unit: ScalarQuantity = 232500 | units.MSun,
        barion_fraction: float | None = None,
    ) -> None:
        self.filename = filename
        self.dist_unit = dist_unit
        self.vel_unit = vel_unit
        self.mass_unit = mass_unit
        self.barion_fraction = barion_fraction

    def run(self) -> Snapshot:
        with open(self.filename, "r") as f:
            xml_text = f.read()

        data = bytes(bytearray(xml_text, encoding="utf-8"))
        tree = etree.XML(data)
        snapshot_node = tree.find("SnapShot")
        params_node = snapshot_node.find("Parameters")
        n_obj = int(params_node.find("Nobj").text)

        particles_node = snapshot_node.find("Particles")
        positions = particles_node.find("Position").text
        positions = np.fromstring(positions, dtype=float, sep=" ")
        if len(positions) % 3 != 0:
            positions = np.array([])
        positions = positions.reshape((-1, 3))

        velocities = particles_node.find("Velocity").text
        velocities = np.fromstring(velocities, dtype=float, sep=" ")
        if len(velocities) % 3 != 0:
            velocities = np.array([])
        velocities = velocities.reshape((-1, 3))

        masses = particles_node.find("Mass").text
        masses = np.fromstring(masses, dtype=float, sep=" ")
        if len(positions) == 0:
            masses = np.array([])

        particles = Particles(n_obj)
        particles.position = positions * self.dist_unit
        particles.velocity = velocities * self.vel_unit
        particles.mass = masses * self.mass_unit

        if self.barion_fraction is not None:
            is_barion: np.ndarray = np.ndarray((len(particles),))
            is_barion[: int(len(particles) * self.barion_fraction)] = True
            is_barion[int(len(particles) * self.barion_fraction) :] = False
            particles.is_barion = is_barion

        return Snapshot(particles)
