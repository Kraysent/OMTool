import time
from typing import Callable

from amuse.lab import ScalarQuantity, units
from zlog import logger

from omtool import visualizer
from omtool.actions_after import initialize_actions_after
from omtool.actions_before import initialize_actions_before
from omtool.core.configs import AnalysisConfig
from omtool.core.datamodel import Snapshot, profiler
from omtool.core.tasks import DataType, initialize_tasks
from omtool.core.utils import initialize_logger
from omtool.misc import initialize_input_snapshot


def analize(config: AnalysisConfig, close_funcs: list[Callable[[], None]]):
    """
    Analysis mode for the OMTool. It is used for the data
    analysis of existing models and the export of their parameters.
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

    @profiler("Analysis stage")
    def loop_analysis_stage(snapshot: Snapshot):
        outputs: dict[str, DataType] = {}

        for id, task in tasks.items():
            outputs[id] = task.run(snapshot, outputs)

    @profiler("Saving stage")
    def loop_saving_stage(iteration: int, timestamp: ScalarQuantity):
        if visualizer_service is not None:
            visualizer_service.save({"i": iteration, "time": timestamp.value_in(units.Myr)})

    logger.info().msg("Analysis started")

    snapshots = initialize_input_snapshot(config.input_file)

    for (i, snapshot) in enumerate(snapshots):
        start_comp = time.time()
        loop_analysis_stage(snapshot)
        start_save = time.time()
        loop_saving_stage(i, snapshot.timestamp)
        end = time.time()

        (
            logger.info()
            .string("id", "time_data")
            .int("i", i)
            .measured_float("timestamp", snapshot.timestamp.value_in(units.Myr), "Myr", decimals=3)
            .measured_float("computation_time", start_save - start_comp, "s", decimals=2)
            .measured_float("saving_time", end - start_save, "s", decimals=2)
            .send()
        )
