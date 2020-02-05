import pytest

import cirq

from cirq.pasqal import PasqalDevice, ThreeDGridQubit


def cubic_device(width: int,
                 height: int,
                 depth: int,
                 holes=()
                 ) -> PasqalDevice:

    return PasqalDevice(  # type: ignore
        control_radius=1.5,
        qubits=[
            ThreeDGridQubit(row, col, lay)
            for row in range(width)
            for col in range(height)
            for lay in range(depth)
            if ThreeDGridQubit(row, col, lay) not in holes
        ])


def test_init():
    d = cubic_device(2, 2, 2, holes=[ThreeDGridQubit(1, 1, 1)])
    us = cirq.Duration(nanos=10 ** 3)
    ms = cirq.Duration(nanos=10 ** 6)
    q000 = ThreeDGridQubit(0, 0, 0)
    q001 = ThreeDGridQubit(0, 0, 1)
    q010 = ThreeDGridQubit(0, 1, 0)
    q011 = ThreeDGridQubit(0, 1, 1)
    q100 = ThreeDGridQubit(1, 0, 0)
    q101 = ThreeDGridQubit(1, 0, 1)
    q110 = ThreeDGridQubit(1, 1, 0)

    assert d.qubit_set() == {q000, q001, q010, q011, q100, q101, q110}
    assert set(d.qubit_list()) == {q000, q001, q010, q011, q100, q101, q110}
    assert d.duration_of(cirq.ops.GateOperation(cirq.ops.IdentityGate(1),
                                       [q000])) == 2 * us
    assert d.duration_of(cirq.ops.measure(q000)) == 5 * ms
    with pytest.raises(ValueError):
        _ = d.duration_of(cirq.ops.SingleQubitGate().on(q000))


def test_init_errors():
    line = cirq.devices.LineQubit.range(3)
    with pytest.raises(TypeError, match="Unsupported qubit type"):
        _ = PasqalDevice(control_radius=1.5, qubits=line)

    with pytest.raises(ValueError):
        _ = PasqalDevice(control_radius=-1, qubits=[ThreeDGridQubit(0, 0, 0)])


def test_decompose_error():
    d = cubic_device(2, 2, 1, holes=[ThreeDGridQubit(1, 1, 0)])
    for op in d.decompose_operation((cirq.ops.CCZ**1.5).on(*(d.qubit_list()))):
        d.validate_operation(op)

    class bad_op(cirq.Operation):

        def bad_op(self):
            pass

        def qubits(self):
            pass

        def with_qubits(self, new_qubits):
            pass

    with pytest.raises(TypeError):
        d.decompose_operation(bad_op())

    #MeasurementGate is not a GateOperation
    with pytest.raises(TypeError):
        d.decompose_operation(cirq.ops.MeasurementGate(num_qubits=1))
    #It has to be made into one
    assert PasqalDevice.is_pasqal_device_op(
        cirq.ops.GateOperation(cirq.ops.MeasurementGate(1), [ThreeDGridQubit(0, 0, 0)]))

    assert PasqalDevice.is_pasqal_device_op(cirq.ops.X(ThreeDGridQubit(0, 0, 0)))
        #cirq.ops.GateOperation(cirq.ops.X, [ThreeDGridQubit(0, 0, 0)]))


def test_validate_operation_errors():
    d = cubic_device(3, 3, 3)

    class bad_op(cirq.Operation):

        def bad_op(self):
            pass

        def qubits(self):
            pass

        def with_qubits(self, new_qubits):
            pass

    with pytest.raises(ValueError, match="Unsupported operation"):
        d.validate_operation(bad_op())

    #with pytest.raises(ValueError, match="Qubit not on device"):
    #    d.validate_operation(not_on_device_op)
    with pytest.raises(ValueError):
        d.validate_operation(cirq.CCX.on(cirq.LineQubit(0)))
    with pytest.raises(ValueError, match="are too far away"):
        d.validate_operation(cirq.CZ.on(ThreeDGridQubit(0, 0, 0),
                                        ThreeDGridQubit(3, 3, 3)))
    with pytest.raises(ValueError, match="Too many Z gates in parallel"):
        d.validate_operation(cirq.ParallelGateOperation(cirq.ops.Z, d.qubits))
    with pytest.raises(ValueError, match="Bad number of X/Y gates in parallel"):
        d.validate_operation(cirq.ParallelGateOperation(cirq.ops.X,
                                                        d.qubit_list()[1:]))


def test_qubit_set():
    assert cubic_device(2, 2, 2).qubit_set() == set(
        ThreeDGridQubit.cube(2, 0, 0, 0))

def test_distance():
    d = cubic_device(2, 2, 1)
    assert d.distance(ThreeDGridQubit(0,0,0),ThreeDGridQubit(1,0,0)) == 1

    with pytest.raises(ValueError):
        _ = d.distance(ThreeDGridQubit(0,0,0), cirq.devices.LineQubit(1))

    with pytest.raises(ValueError):
        _ = d.distance(cirq.devices.LineQubit(1), ThreeDGridQubit(0,0,0))


def test_repr():
    print(repr(cubic_device(1, 1, 1)))
    assert repr(cubic_device(1, 1, 1)) == ("pasqal.PasqalDevice("
            "control_radius=1.5, qubits=[pasqal.ThreeDGridQubit(0, 0, 0)])")


def test_to_json():
    dev = cirq.pasqal.PasqalDevice(
        control_radius=5,
        qubits=[cirq.pasqal.ThreeDGridQubit(1, 1, 1)]
    )
    d = dev._json_dict_()
    assert d == {
        "cirq_type": "PasqalDevice",
        "control_radius": 5,
        "qubits": [cirq.pasqal.ThreeDGridQubit(1, 1, 1)]
    }
