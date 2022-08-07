import glob
import importlib
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Optional

from amuse.lab import VectorQuantity, units
from zlog import logger

from omtool.core.datamodel import AbstractModel, Snapshot
from omtool.core.models.plugin import MODELS


@dataclass
class ModelConfig:
    name: str
    args: dict[str, Any]
    position: VectorQuantity
    velocity: VectorQuantity
    downsample_to: Optional[int]


def get_model(model_name: str, args: dict) -> AbstractModel | None:
    return MODELS[model_name](**args) if model_name in MODELS else None


def import_models(imports: list[str]):
    filenames = []

    for imp in imports:
        filenames.extend(glob.glob(imp))

    for filename in filenames:
        path = pathlib.Path(filename)
        sys.path.append(str(path.parent))
        importlib.import_module(path.stem)


def initialize_models(imports: list[str], configs: list[ModelConfig]) -> list[Snapshot]:
    import_models(imports)
    models: list[Snapshot] = []

    for config in configs:
        model = get_model(config.name, config.args)

        if model is None:
            (
                logger.warn()
                .string("error", "model not found")
                .string("name", config.name)
                .msg("skipping")
            )
            continue

        snapshot = model.run()
        snapshot.particles.position += config.position
        snapshot.particles.velocity += config.velocity

        if config.downsample_to is not None:
            c = len(snapshot.particles) / config.downsample_to
            snapshot.particles = snapshot.particles[:: int(c)]
            snapshot.particles.mass *= c

        models.append(snapshot)
        (
            logger.info()
            .int("n", len(snapshot.particles))
            .measured_float(
                "total_mass", snapshot.particles.total_mass().value_in(units.MSun), "MSun"
            )
            .msg("added snapshot")
        )

    return models
