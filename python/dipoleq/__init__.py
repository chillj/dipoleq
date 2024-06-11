"""DipolEq: Levitated Dipole Equilibrium Solver

DipolEq is a Python package for solving the equilibrium of a levitated dipole
magnetized plasma. It is a Python wrapper around the C code that was originally
written by Michael Mauel and his group at Columbia University in the early 1999s
called TokaMac. The C code was later modified by Darren Garnier at Columbia
for use in the LDX experiment. The Python wrapper was written by Darren Garnier
at OpenStar Technologies, LTD.

"""

from pathlib import Path
from typing import Any

from typing_extensions import Self

from . import core, file_input, input, solver, util
from ._version import __version__, __version_tuple__
from .core import Machine as _Machine
from .input import MachineIn
from .saveh5 import save_to_hdf5 as _save_to_hdf5


class Machine(_Machine):
    """Machine class for the Dipole Equilibrium Solver"""

    # don't even think about messing with init
    # and pybind11 superclass

    @classmethod
    def from_fileinput(cls, filename: str | Path) -> Self:
        """Generate a Machine object from a .in file
        Using the Python code to read the file

        Args:
            filename (str): The path to the .in file

        Returns:
            Machine: The Machine object
        """
        input_data = file_input.input_from_dotin(str(filename))
        return cls.from_input_data(input_data)

    @classmethod
    def from_yaml(cls, filename: str | Path) -> Self:
        """Generate a Machine object from a .yaml file

        Args:
            filename (str): The path to the .yaml file

        Returns:
            Machine: The Machine object
        """
        input_data = file_input.input_from_yaml(str(filename))
        return cls.from_input_data(input_data)

    @classmethod
    def from_dict(cls, input_data: dict[str, Any]) -> Self:
        """Generate a Machine object from a dictionary

        Args:
            input_data (dict): The data to create the Machine object

        Returns:
            Machine: The Machine object
        """
        verified_data = MachineIn(**input_data)
        return cls.from_input_data(verified_data)

    @classmethod
    def from_file(cls, filename: str | Path) -> Self:
        """Generate a Machine object from a file

        Args:
            filename (str): The path to the file

        Returns:
            Machine: The Machine object
        """

        p = Path(filename)
        filename = str(filename)
        if p.suffix == ".in":
            return cls.from_fileinput(filename)
        if p.suffix == ".yaml":
            return cls.from_yaml(filename)

        raise ValueError(f"Unknown file type: {filename}")

    @classmethod
    def from_input_data(cls, valid_input: MachineIn) -> Self:
        """Factory method to create a Machine object from validated input

        Args:
            valid_input (MachineIn): Validated input data

        Returns:
            Machine: Machine object ready to be solved
        """
        m = cls()
        valid_input.initalize_machine(m)
        return m

    def solve(self, quiet: bool = True) -> None:
        """Do the thing!"""
        solver.solve(self, quiet=quiet)

    def diff(self, other: _Machine, verbose: bool = False) -> bool:
        """display the differences between two machines

        Args:
            other (Machine): The one to compare to
            verbose (bool, Optional): Be noisy about it. Defaults to False.

        Returns:
            bool: Are they different?
        """
        return util.machine_diff(self, other, verbose=verbose)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Machine):
            return False
        return not self.diff(other)

    def to_hdf5(self, filename: str | Path | None) -> None:
        """Save the machine data to an HDF5 file

        Args:
            filename (str | Path | None): The path to the file
        """
        _save_to_hdf5(self, filename)


__all__ = [
    "Machine",
    "MachineIn",
    "core",
    "solver",
    "input",
    "file_input",
    "util",
    "__version_tuple__",
    "__version__",
]
