"""AGAPI - Python client for AtomGPT.org API"""
import os
from .client import (
    Agapi,
    AgapiError,
    AgapiAuthError,
    AgapiValidationError,
    AgapiTimeoutError,
    AgapiServerError,
    __version__,
)

__all__ = [
    "Agapi",
    "AgapiError",
    "AgapiAuthError",
    "AgapiValidationError",
    "AgapiTimeoutError",
    "AgapiServerError",
    "__version__",
]

def test(*args):
    """Run pytest in the base of jarvis."""
    import pytest

    path = os.path.join(os.path.split(__file__)[0], "tests")
    pytest.main(args=[path] + list(args))
