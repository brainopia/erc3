class ERC3LiveError(Exception):
    """Base error for live ERC3 wrapper failures."""


class TransportError(ERC3LiveError):
    """Network or browser transport failed."""


class ParseError(ERC3LiveError):
    """Expected ERC3 page structure or payload was missing."""


class TaskStateError(ERC3LiveError):
    """Task state does not allow the requested operation."""


class AgentExecutionError(ERC3LiveError):
    """User agent code failed while solving a task."""
