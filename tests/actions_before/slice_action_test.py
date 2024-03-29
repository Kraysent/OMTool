from amuse.lab import Particles

from omtool.actions_before import slice_action
from omtool.core.datamodel import Snapshot
from omtool.core.utils import BaseTestCase


class TestSliceAction(BaseTestCase):
    def test_parts_one_slice(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, parts=[(0, 0.1)])
        expected = snapshot[:10]

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_parts_two_slice_without_overlap(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, parts=[(0, 0.1), (0.2, 0.3)])
        expected = snapshot[:10] + snapshot[20:30]

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_parts_two_slices_with_overlap(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, parts=[(0, 0.2), (0.1, 0.3)])
        expected = snapshot[:20] + snapshot[10:30]

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_parts_outside_unit_interval(self):
        snapshot = self._generate_snapshot()

        self.assertRaises(ValueError, slice_action, snapshot, parts=[(0, 10)])

    def test_part_valid(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, part=[0, 20])
        expected = snapshot[:20]

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_part_wrong_number_of_arguments(self):
        snapshot = self._generate_snapshot()

        self.assertRaises(ValueError, slice_action, snapshot, part=[0, 1, 2, 3])

    def test_part_outside_of_boundaries(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, part=[1000, 2000])
        expected = Snapshot(Particles(), snapshot.timestamp)

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_id_valid(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, id=10)
        expected = snapshot[10:11]

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_id_outside_of_boundaries(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, id=150)
        expected = Snapshot(Particles(), snapshot.timestamp)

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_ids_valid(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, ids=[5, 10, 15])
        expected = Snapshot(Particles(), snapshot.timestamp)
        expected.particles.add_particle(snapshot.particles[5])
        expected.particles.add_particle(snapshot.particles[10])
        expected.particles.add_particle(snapshot.particles[15])

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)

    def test_ids_empty_list(self):
        snapshot = self._generate_snapshot()
        actual = slice_action(snapshot, ids=[])
        expected = Snapshot(Particles(), snapshot.timestamp)

        self.assertSnapshotsEqual(actual, expected, test_kinematics=False)
