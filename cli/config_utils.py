import os
from typing import Type

import numpy as np
import yaml
from amuse.lab import ScalarQuantity, VectorQuantity, units
from amuse.units.core import named_unit


def str_to_unit(name: str) -> named_unit:
    return getattr(units, name)


def unit_cartesian_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.SequenceNode
) -> ScalarQuantity | VectorQuantity:
    """
    Processes the !q tag
    """
    data = loader.construct_sequence(node, deep=True)

    if len(data) != 2:
        raise ValueError(f"Tried to cast {data} to quantity.")

    if isinstance(data[0], list):
        return np.array(data[0]) | str_to_unit(data[1])

    return data[0] | str_to_unit(data[1])


def unit_spherical_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.SequenceNode
) -> ScalarQuantity | VectorQuantity:
    """
    Processes the !qs tag
    """
    data = loader.construct_sequence(node, deep=True)

    if len(data) != 2:
        raise ValueError(f"Tried to cast {data} to quantity.")

    if isinstance(data[0], list):
        if len(data[0]) != 3:
            raise ValueError(
                f"{data} should have 3 components; don't know how to convert {len(data[0])} "
                "components from spherical coordinates."
            )

        x = data[0][0] * np.cos(data[0][1]) * np.sin(data[0][2])
        y = data[0][0] * np.sin(data[0][1]) * np.sin(data[0][2])
        z = data[0][0] * np.sin(data[0][2])
        return np.array([x, y, z]) | str_to_unit(data[1])

    return data[0] | str_to_unit(data[1])


def env_constructor(loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode) -> str:
    """
    Processes the !env tag
    """
    data = loader.construct_scalar(node)

    if not isinstance(data, str):
        raise ValueError(f"Tried to paste environment variable into not-string: {data}")

    return data.format(**os.environ)


def slice_constructor(loader: yaml.SafeLoader, node: yaml.nodes.SequenceNode) -> slice:
    """
    Processes the !slice tag
    """
    data = loader.construct_sequence(node)

    if len(data) in {1, 2, 3}:
        return slice(*data)
    else:
        raise ValueError(
            f"{data} has len {len(data)} while 1, 2 or 3 is possible to construct a slice."
        )


def yaml_loader() -> Type[yaml.SafeLoader]:
    """
    Loader that processes all the tags.
    """
    loader = yaml.SafeLoader
    loader.add_constructor("!q", unit_cartesian_constructor)
    loader.add_constructor("!qs", unit_spherical_constructor)
    loader.add_constructor("!env", env_constructor)
    loader.add_constructor("!slice", slice_constructor)

    return loader
