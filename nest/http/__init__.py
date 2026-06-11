"""
User-facing HTTP import facade.

Under the default FastAPI engine these are direct re-exports of the
corresponding fastapi symbols. When a second engine adapter is introduced,
this module will resolve based on the active adapter instead.

Recommended usage:
    from nest.http import Request, Response, Depends

FastAPI imports still work and are not deprecated in 0.7.x.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request, Response

__all__ = ["Depends", "HTTPException", "Request", "Response"]
