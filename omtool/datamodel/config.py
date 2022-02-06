from typing import Union

import numpy as np
import yaml
from amuse.lab import ScalarQuantity, VectorQuantity, units
from amuse.units.core import named_unit


def str_to_unit(s: str) -> named_unit:
    unit_names = ['Myr', 'kpc', 'kms', 'MSun', 'J']
    actual_units = [units.Myr, units.kpc, units.kms, units.MSun, units.J]

    index = unit_names.index(s) if s in unit_names else None

    if index is not None:
        return actual_units[index]
    else:
        raise RuntimeError(f'{str} is unsupported unit name.')

def unit_constructor(
    loader: yaml.SafeLoader, node: yaml.nodes.Node
) -> Union[ScalarQuantity, VectorQuantity]:
    data = loader.construct_sequence(node, deep = True)

    if len(data) != 2:
        raise RuntimeError(f'Tried to cast {data} to quantity.')

    if isinstance(data[0], list):
        return np.array(data[0]) | str_to_unit(data[1])
    else:
        return data[0] | str_to_unit(data[1])

def yaml_loader() -> yaml.Loader:
    loader = yaml.SafeLoader
    loader.add_constructor('!q', unit_constructor)

    return loader
