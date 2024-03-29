from typing import Callable

from omtool import visualizer
from omtool.actions_after.extract_params_action import extract_action
from omtool.actions_after.fit_action import fit_2d_action
from omtool.actions_after.logger_action import logger_action
from omtool.actions_after.visualizer_action import VisualizerAction


def initialize_actions_after(
    vis_service: visualizer.VisualizerService | None = None,
) -> dict[str, Callable]:
    actions_after: dict[str, Callable] = {
        "logging": logger_action,
        "fit": fit_2d_action,
        "fit2d": fit_2d_action,
        "extract": extract_action,
    }

    if vis_service is not None:
        actions_after["visualizer"] = VisualizerAction(vis_service)

    return actions_after
