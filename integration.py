import logging
import os
from pathlib import Path

from amuse.lab import units

from omtool.datamodel import Snapshot, profiler
from omtool.integration import PyfalconIntegrator
from omtool.integration.config import IntegrationConfig


@profiler('Integration stage')
def loop_integration_stage(integrator):
    integrator.leapfrog()

@profiler('Saving to file stage')
def loop_saving_stage(integrator, config: IntegrationConfig, iteration: int, points_to_track: dict):
    if iteration % config.snapshot_interval == 0:
        snapshot = integrator.get_snapshot()
        snapshot.to_fits(config.output_file, append = True)

    for (point_id, name) in points_to_track.items():
        with open(name, 'a') as stream:
            particle = integrator.get_particle(point_id)
            x, y, z = particle.position.value_in(units.kpc)
            vx, vy, vz = particle.velocity.value_in(units.kms)
            m = particle.mass.value_in(units.MSun)
            T = integrator.timestamp.value_in(units.Myr)
            stream.write(f'{T} {x} {y} {z} {vx} {vy} {vz} {m}\n')

    logging.info(f'{integrator.timestamp.value_in(units.Myr):.01f}')

def integrate(config: IntegrationConfig):
    snapshot = next(Snapshot.from_fits(config.input_file))
    integrator = PyfalconIntegrator(snapshot, config.eps, config.timestep)

    if not config.overwrite:
        if Path(config.output_file).is_file():
            raise Exception(f'Output file ({config.output_file}) exists and "overwrite" option in integration config file is false (default)')
        
        for x in config.logs:
            if Path(x.filename).is_file():
                raise Exception(f'Log output file ({x.filename}) exists and "overwrite" option in integration config file is false (default)')

    if Path(config.output_file).is_file():
        os.remove(config.output_file)

    logging.info('T, Myr')
    i = 0

    points_to_track = { x.point_id: x.filename for x in config.logs }
    
    for (_, name) in points_to_track.items():
        with open(name, 'w') as stream:
            stream.write('T x y z vx vy vz m\n')

    while integrator.timestamp < config.model_time:
        loop_integration_stage(integrator)
        loop_saving_stage(integrator, config, i, points_to_track)
        
        i += 1
