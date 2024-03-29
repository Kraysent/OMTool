from dataclasses import dataclass
from typing import Callable

from zlog import logger

from omtool.core.tasks.abstract_task import AbstractTask
from omtool.core.tasks.handler_task import HandlerTask
from omtool.core.tasks.plugin import TASKS
from omtool.core.utils import import_modules


@dataclass
class TasksConfig:
    name: str
    args: dict
    id: str
    inputs: dict[str, str]
    actions_before: list[dict]
    actions_after: list[dict]


def get_task(task_name: str, args: dict) -> AbstractTask | None:
    return TASKS[task_name](**args) if task_name in TASKS else None


def initialize_tasks(
    imports: list[str],
    configs: list[TasksConfig],
    actions_before: dict[str, Callable],
    actions_after: dict[str, Callable],
) -> dict[str, HandlerTask]:
    import_modules(imports)
    tasks: dict[str, HandlerTask] = {}

    for i, config in enumerate(configs):
        task = get_task(config.name, config.args)

        if task is None:
            (
                logger.warn()
                .string("error", "task not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        curr_task = HandlerTask(task)
        curr_task.inputs = config.inputs

        for action_params in config.actions_before:
            action_name = action_params.pop("type", None)

            if action_name is None:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is not specified, skipping."
                )
                continue

            if action_name not in actions_before:
                logger.error().msg(
                    f"action_before type {action_name} of the task "
                    f"{type(curr_task.task)} is unknown, skipping."
                )
                continue

            def action(snapshot, name=action_name, params=action_params):
                return actions_before[name](snapshot, **params)

            curr_task.actions_before.append(action)

        for handler_params in config.actions_after:
            handler_name = handler_params.pop("type", None)

            if handler_name is None:
                (
                    logger.error().msg(
                        f"Handler type {handler_name} of the task "
                        f"{type(curr_task.task)} is not specified, skipping."
                    )
                )
                continue

            if handler_name not in actions_after:
                (
                    logger.error().msg(
                        f"Handler type {handler_name} of the task "
                        f"{type(curr_task.task)} is unknown, skipping."
                    )
                )
                continue

            def handler(data, name=handler_name, params=handler_params):
                return actions_after[name](data, **params)

            curr_task.actions_after.append(handler)

        if config.id == "":
            config.id = f"task_{i}"

        tasks[config.id] = curr_task
        logger.debug().string("name", config.name).msg("initialized task")

    return tasks
