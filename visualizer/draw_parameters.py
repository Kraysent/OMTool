from dataclasses import dataclass
from typing import Any, Tuple

import matplotlib as mpl


@dataclass
class DrawParameters:  
    id: str
    markersize: float = 0.1
    linestyle: str = 'None'
    color: str = 'b'
    marker: str = 'o'
    is_density_plot: bool = False
    resolution: int = 100
    extent: Tuple[int, int, int, int] = (0, 100, 0, 100)
    cmap: str = 'ocean_r'
    cmapnorm: Any = mpl.colors.LogNorm()
    label: str = None
    channel: str = 'b'
