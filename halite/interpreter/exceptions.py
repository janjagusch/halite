"""
Custom exceptions for the interpreter.
"""

from abc import ABC


class HaliteInterpreterExecption(Exception, ABC):
    """
    Base exception. Should not be raised.
    """


class InactiveUnitError(HaliteInterpreterExecption):
    """"
    Exception that is thrown when interacting with an inactive unit.
    """


class CantConvertError(HaliteInterpreterExecption):
    """
    Exception that is thrown when you cannot convert a ship to a shipyard.
    """


class CantMoveError(HaliteInterpreterExecption):
    """
    Exception that is thrown when you cannot move a ship.
    """


class CantMineError(HaliteInterpreterExecption):
    """
    Exception that is thrown when you cannot mine with a ship.
    """


class CantSpawnError(HaliteInterpreterExecption):
    """
    Exception that is thrown when you cannot spawn a ship at a shipyard.
    """


class CantDepositError(HaliteInterpreterExecption):
    """
    Exception that is thrown when you cannot deposit a ship's halite.
    """
