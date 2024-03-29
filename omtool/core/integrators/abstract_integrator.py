from abc import ABC, abstractmethod

from omtool.core.datamodel.snapshot import Snapshot


class AbstractIntegrator(ABC):
    """
    Run one step of integration.
    """

    @abstractmethod
    def leapfrog(self, snapshot: Snapshot) -> Snapshot:
        raise NotImplementedError
