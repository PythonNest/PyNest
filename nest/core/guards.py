from fastapi import Request, HTTPException, status, Security
from fastapi.security.base import SecurityBase
import inspect


class BaseGuard:
    """Base class for creating route guards.

    If ``security_scheme`` is set to an instance of ``fastapi.security.SecurityBase``
    the guard will be injected with the credentials from that scheme and the
    corresponding security requirement will appear in the generated OpenAPI
    schema.
    """

    security_scheme: SecurityBase | None = None

    def can_activate(self, request: Request, credentials=None) -> bool:
        """Override this method with your authorization logic."""
        raise NotImplementedError

    async def __call__(self, request: Request, credentials=None):
        result = self.can_activate(request, credentials)
        if inspect.isawaitable(result):
            result = await result
        if not result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

    @classmethod
    def as_dependency(cls):
        """Return a dependency callable for FastAPI routes."""

        if cls.security_scheme is None:

            async def dependency(request: Request):
                guard = cls()
                await guard(request)

            return dependency

        security_scheme = cls.security_scheme

        async def dependency(request: Request, credentials=Security(security_scheme)):
            guard = cls()
            await guard(request, credentials)

        return dependency


def UseGuards(*guards):
    """Decorator to attach guards to a controller or route."""

    def decorator(obj):
        existing = list(getattr(obj, "__guards__", []))
        existing.extend(guards)
        setattr(obj, "__guards__", existing)
        return obj

    return decorator
