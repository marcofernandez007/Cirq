# Copyright 2020 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Iterable, List, Optional, Set, Tuple
from numpy import sqrt, isclose
import numpy as np

import cirq


class ThreeDGridQubit(cirq.ops.Qid):
    """A qubit in 3d.

    ThreeDGridQubits use x-y-z ordering:

        ThreeDGridQubit(0, 0, 0) < ThreeDGridQubit(0, 0, 1)
        < ThreeDGridQubit(0, 1, 0)< ThreeDGridQubit(1, 0, 0)
        < ThreeDGridQubit(0, 1, 1)< ThreeDGridQubit(1, 0, 1)
        < ThreeDGridQubit(1, 1, 0)< ThreeDGridQubit(1, 1, 1)

    New ThreeDGridQubit can be constructed by adding or subtracting tuples

        >>> cirq.pasqal.ThreeDGridQubit(2.5, 3, 4.7) + (3, 1.2, 6)
        pasqal.ThreeDGridQubit(5.5, 4.2, 10.7)

        >>> cirq.pasqal.ThreeDGridQubit(2.4, 3.1, 4.8) - (1, 2, 2.1)
        pasqal.ThreeDGridQubit(1.4, 1.1, 2.7)
    """

    def __init__(self, row: float, col: float, lay: float):
        self.x = row
        self.y = col
        self.z = lay

    def _comparison_key(self):
        return round(self.x, 9), round(self.y, 9), round(self.z, 9)

    @property
    def dimension(self) -> int:
        return 2


    def distance(self, other: cirq.ops.Qid) -> float:
        """Returns the distance between two qubits in 3D"""
        if not isinstance(other, ThreeDGridQubit):
            raise TypeError(
                "Can compute distance to another ThreeDGridQubit, but {}".
                format(other))
        return sqrt((self.x - other.row)**2 + (self.y - other.col)**2 +
                    (self.z - other.lay)**2)

    @staticmethod
    def cube(diameter: int, top: int = 0, left: int = 0,
             upper: int = 0) -> List['ThreeDGridQubit']:
        """Returns a cube of ThreeDGridQubits.

        Args:
            diameter: Length of a side of the square
            top: Row number of the topmost row
            top: x-coordinate of the topmost qubit
            left: y-coordinate of the leftmost qubit

        Returns:
            A list of ThreeDGridQubits filling in a square grid
        """
        return ThreeDGridQubit.parallelep(diameter,
                                          diameter,
                                          diameter,
                                          top=top,
                                          left=left,
                                          upper=upper)

    @staticmethod
    def parallelep(rows: int,
                   cols: int,
                   lays: int,
                   top: int = 0,
                   left: int = 0,
                   upper: int = 0) -> List['ThreeDGridQubit']:
        """Returns a parallelepiped of ThreeDGridQubits.

        Args:
            rows: Number of rows in the rectangle
            cols: Number of columns in the rectangle
            top: x-coordinate of the topmost qubit
            left: y-coordinate of the leftmost qubit

        Returns:
            A list of ThreeDGridQubits filling in a rectangular grid
        """
        return [
            ThreeDGridQubit(row, col, lay) for row in range(top, top + rows)
            for col in range(left, left + cols)
            for lay in range(upper, upper + lays)
        ]

    @staticmethod
    def square(diameter: int, top: int = 0,
               left: int = 0) -> List['ThreeDGridQubit']:
        """Returns a square of ThreeDGridQubits.

        Args:
            diameter: Length of a side of the square
            top: x-coordinate of the topmost qubit
            left: y-coordinate of the leftmost qubit

        Returns:
            A list of ThreeDGridQubits filling in a square grid
        """
        return ThreeDGridQubit.rect(diameter, diameter, top=top, left=left)

    @staticmethod
    def rect(rows: int, cols: int, top: int = 0,
             left: int = 0) -> List['ThreeDGridQubit']:
        """Returns a rectangle of ThreeDGridQubits.

        Args:
            rows: Number of rows in the rectangle
            cols: Number of columns in the rectangle
            top: x-coordinate of the topmost qubit
            left: y-coordinate of the leftmost qubit

        Returns:
            A list of ThreeDGridQubits filling in a rectangular grid
        """
        return [
            ThreeDGridQubit(row, col, 0)
            for row in range(top, top + rows)
            for col in range(left, left + cols)
        ]


    @staticmethod
    def triangular_lattice(l : int, top: float = 0., left: float = 0.):
        """Returns a triangular lattice of ThreeDGridQubits.

        Args:
            l: Number of qubits along one direction
            top: first coordinate of the first qubit
            left: second coordinate of the first qubit

        Returns:
            A list of ThreeDGridQubits filling in a triangular lattice
        """
        coords = np.array([[x, y] for x in range(l + 1)
                           for y in range(l + 1)], dtype=float)
        coords[:, 0] += 0.5 * np.mod(coords[:, 1], 2)
        coords[:, 1] *= np.sqrt(3) / 2
        coords += [top, left]

        return [
            ThreeDGridQubit(coord[0], coord[1], 0)
            for coord in coords
        ]

    def __repr__(self):
        return 'pasqal.ThreeDGridQubit({}, {}, {})'.format(
            self.x, self.y, self.z)

    def __str__(self):
        return '({}, {}, {})'.format(self.x, self.y, self.z)

    def _json_dict_(self):
        return cirq.protocols.obj_to_dict_helper(self, ['x', 'y', 'z'])

    def __add__(self, other: Tuple[float, float, float]) -> 'ThreeDGridQubit':
        if not (isinstance(other, tuple) and len(other) == 3 and
                all(isinstance(x, float) or isinstance(x, int) for x in other)):
            raise TypeError(
                'Can only add tuples of length 3. Was {}'.format(other))
        return ThreeDGridQubit(row=self.x + other[0],
                               col=self.y + other[1],
                               lay=self.z + other[2])

    def __sub__(self, other: Tuple[float, float, float]) -> 'ThreeDGridQubit':
        if not (isinstance(other, tuple) and len(other) == 3 and
                all(isinstance(x, float) or isinstance(x, int) for x in other)):
            raise TypeError(
                'Can only subtract tuples of length 3. Was {}'.format(other))
        return ThreeDGridQubit(row=self.x - other[0],
                               col=self.y - other[1],
                               lay=self.z - other[2])

    def __radd__(self, other: Tuple[float, float, float]) -> 'ThreeDGridQubit':
        return self + other

    def __rsub__(self, other: Tuple[float, float, float]) -> 'ThreeDGridQubit':
        return -self + other

    def __neg__(self) -> 'ThreeDGridQubit':
        return ThreeDGridQubit(row=-self.x, col=-self.y, lay=-self.z)
