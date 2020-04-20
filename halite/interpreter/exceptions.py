"""
Custom exceptions for the interpreter.
"""

from abc import ABC


class HaliteInterpreterException(Exception, ABC):
    """
    Base exception. Should not be raised.
    """


class InactiveUnitError(HaliteInterpreterException):
    """"
    Exception that is thrown when interacting with an inactive unit.
    """


class CantConvertError(HaliteInterpreterException):
    """
    Exception that is thrown when you cannot convert a ship to a shipyard.
    """


class CantMoveError(HaliteInterpreterException):
    """
    Exception that is thrown when you cannot move a ship.
    """


class CantMineError(HaliteInterpreterException):
    """
    Exception that is thrown when you cannot mine with a ship.
    """


class CantSpawnError(HaliteInterpreterException):
    """
    Exception that is thrown when you cannot spawn a ship at a shipyard.
    """


class CantDepositError(HaliteInterpreterException):
    """
    Exception that is thrown when you cannot deposit a ship's halite.
    """


class InvalidActionError(HaliteInterpreterException):
    """
    Exception that is thrown when the interpreter is provided with an invalid action.
    """


class InvalidUnitError(HaliteInterpreterException):
    """
    Exception that is raised when the interpreter is provided with an invalid uid.
    """


class NoStateError(HaliteInterpreterException):
    """
    Exception that is thrown when trying to access a game state but it is not there.
    """

class InvalidUnitTypeError(HaliteInterpreterException):
    """
    Exception that is thrown when trying to create a unit type that does not exist.
    """
