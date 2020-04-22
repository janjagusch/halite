"""
Custom exceptions for the interpreter.
"""

from abc import ABC


class HaliteInterpreterException(Exception, ABC):
    """
    Base exception. Should not be raised.
    """


class IllegalAction(HaliteInterpreterException, ABC):
    """
    Base exception for when agents try to perform an illegal action.
    """


class InactiveUnitError(IllegalAction):
    """"
    Exception that is thrown when interacting with an inactive unit.
    """


class InvalidUnitError(IllegalAction):
    """
    Exception that is raised when the interpreter is provided with an invalid uid.
    """


class ImpossibleAction(HaliteInterpreterException, ABC):
    """
    Base exception for when the agents try to perform an impossible action.
    """


class CantConvert(ImpossibleAction):
    """
    Exception that is thrown when you cannot convert a ship to a shipyard.
    """


class CantSpawn(ImpossibleAction):
    """
    Exception that is thrown when you cannot spawn a ship at a shipyard.
    """

class CantDeposit(ImpossibleAction):
    """
    Exceptoin that is thrown when you cannot deposit a ship's cargo.
    """

class NoStateError(HaliteInterpreterException):
    """
    Exception that is thrown when trying to access a game state but it is not there.
    """


class InvalidConstantError(HaliteInterpreterException):
    """
    Exception that is thrown when game is presented with an invalid constant.
    """
