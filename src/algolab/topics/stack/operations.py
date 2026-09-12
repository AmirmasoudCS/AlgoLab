from __future__ import annotations

from abc import ABC, abstractmethod

from .model import Stack


class StackOperation(ABC):
    """Base class for stack operations."""

    @abstractmethod
    def commit(self, stack: Stack) -> object | None:
        """Apply the operation to the given stack."""
        raise NotImplementedError


class PushOperation(StackOperation):
    """Push a value onto the stack."""

    def __init__(self, value: object) -> None:
        self.value = value

    def commit(self, stack: Stack) -> None:
        stack.push(self.value)


class PopOperation(StackOperation):
    """Pop the top value from the stack."""

    def commit(self, stack: Stack) -> object:
        return stack.pop()


class PeekOperation(StackOperation):
    """Peek at the top value without modifying the stack."""

    def commit(self, stack: Stack) -> object:
        return stack.peek()