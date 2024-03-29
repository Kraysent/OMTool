import os
from pathlib import Path
from typing import Callable

from amuse.lab import units
from zlog import logger

from omtool import visualizer
from omtool.actions_after import initialize_actions_after
from omtool.actions_before import initialize_actions_before
from omtool.core.configs import IntegrationConfig
from omtool.core.datamodel import Snapshot, profiler
from omtool.core.integrators import initialize_integrator
from omtool.core.tasks import DataType, initialize_tasks
from omtool.core.utils import initialize_logger
from omtool.misc import initialize_input_snapshot


def integrate(config: IntegrationConfig, close_funcs: list[Callable[[], None]]):
    """
    Integration mode for the OMTool. Used to integrate existing model
    from the file and write it to another file.
    """
    initialize_logger(**config.logging)
    visualizer_service = (
        visualizer.VisualizerService(config.visualizer) if config.visualizer is not None else None
    )

    if visualizer_service is not None:
        close_funcs.append(visualizer_service.close)

    actions_after: dict[str, Callable] = initialize_actions_after(visualizer_service)
    actions_before = initialize_actions_before()
    tasks = initialize_tasks(config.imports.tasks, config.tasks, actions_before, actions_after)
    integrator = initialize_integrator(config.imports.integrators, config.integrator)

    if config.output_file != "" and Path(config.output_file).is_file():
        os.remove(config.output_file)

    @profiler("Integration stage")
    def loop_integration_stage(snapshot: Snapshot) -> Snapshot:
        return integrator.leapfrog(snapshot)

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot):
        outputs: dict[str, DataType] = {}

        for id, task in tasks.items():
            outputs[id] = task.run(snapshot, outputs)

    @profiler("Saving to file stage")
    def loop_saving_stage(iteration: int, snapshot: Snapshot):
        if config.output_file != "" and iteration % config.snapshot_interval == 0:
            snapshot.to_fits(config.output_file, append=True)

        (
            logger.info()
            .string("id", "integration_timing")
            .measured_float("timestamp", snapshot.timestamp.value_in(units.Myr), "Myr", decimals=3)
            .send()
        )

        if visualizer_service is not None:
            visualizer_service.save(
                {"i": iteration, "time": snapshot.timestamp.value_in(units.Myr)}
            )

    generator = initialize_input_snapshot(config.input_file)
    snapshot = next(generator)
    logger.info().msg("Integration started")
    i = 0

    while snapshot.timestamp < config.model_time:
        snapshot = loop_integration_stage(snapshot)
        loop_analysis_stage(snapshot)
        loop_saving_stage(i, snapshot)

        i += 1
