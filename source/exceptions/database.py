# COMMON

class SessionNotInitializedError(Exception):
    """Raised on attempt to utilize uninitialized session."""


# MODELS

class ItemNotFoundError(Exception):
    """Item not found"""

class DatabaseError(Exception):
    """Called when a request is processed incorrectly."""